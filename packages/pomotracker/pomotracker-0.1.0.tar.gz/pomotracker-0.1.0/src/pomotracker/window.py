import psutil
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    Window,
    VSplit,
    HSplit,
    ConditionalContainer,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Layout
from prompt_toolkit.filters import Condition

from pomotracker.session import PomoSession


class PomoTrackerWindow:
    def __init__(self, session: PomoSession):
        self.session = session
        self.show_stats = False
        self.process = psutil.Process()
        # Initial call to cpu_percent to get a baseline
        self.process.cpu_percent(interval=None)
        self.app = self._build_app()

    def _build_app(self) -> Application:
        stats_window = ConditionalContainer(
            Window(
                content=FormattedTextControl(self._get_stats_text),
                height=1,
                style="reverse",
            ),
            filter=Condition(lambda: self.show_stats),
        )

        root_container = HSplit(
            [
                Window(
                    height=1,
                    content=FormattedTextControl([("bold", " PomoTracker ")]),
                    style="reverse",
                ),
                VSplit(
                    [
                        Window(
                            content=FormattedTextControl(self._get_timer_text),
                            width=20,
                            align="center",
                        ),
                        Window(content=FormattedTextControl(self._get_status_text)),
                    ]
                ),
                stats_window,
                Window(
                    height=1,
                    content=FormattedTextControl(
                        " (b)orrow | (p)ause | (s)tats | (q)uit "
                    ),
                    style="reverse",
                ),
            ]
        )

        layout = Layout(root_container)
        kb = self._get_key_bindings()
        return Application(layout=layout, key_bindings=kb, full_screen=True)

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("q")
        def _(event):
            event.app.exit()

        @kb.add("b")
        def _(event):
            self.session.toggle_borrow_mode()

        @kb.add("p")
        def _(event):
            self.session.toggle_pause()

        @kb.add("s")
        def _(event):
            self.show_stats = not self.show_stats

        return kb

    def _get_timer_text(self):
        remaining_seconds = self.session.get_remaining_time()
        minutes = abs(remaining_seconds) // 60
        seconds = abs(remaining_seconds) % 60
        sign = "-" if remaining_seconds < 0 else ""
        return f"{sign}{minutes:02d}:{seconds:02d}"

    def _get_status_text(self):
        return "\n".join(
            (
                f"State: {self.session.state.name}",
                f"Pomo Cycles: {self.session.pomo_cycles}",
                f"Borrow Mode: {'ON' if self.session._borrow_mode else 'OFF'}",
            )
        )

    def _get_stats_text(self):
        cpu_percent = self.process.cpu_percent(interval=None)
        ram_mb = self.process.memory_info().rss / (1024 * 1024)
        return f" CPU: {cpu_percent:.1f}% | RAM: {ram_mb:.2f} MB "

    async def run(self):
        await self.app.run_async()

