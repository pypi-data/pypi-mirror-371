import asyncio
from prompt_toolkit import prompt

from pomotracker.session import PomoSession, State
from pomotracker.window import PomoTrackerWindow
from pomotracker.notification import notify
from pomotracker import database


async def main_loop(session: PomoSession, app):
    last_state = session.state
    while True:
        try:
            session.tick()
            if last_state != session.state:
                if session.state == State.BREAK:
                    await notify("Work Complete!", "Time for a short break.")
                elif session.state == State.LONG_BREAK:
                    await notify("Pomodoro Complete!", "Time for a long break.")
                elif session.state == State.WORKING:
                    await notify("Break Over!", "Time to get back to work.")
            last_state = session.state
            app.invalidate()
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            break


def run():
    database.init_db()
    session = None
    active_session = database.get_active_session()

    if active_session:
        answer = prompt(
            "An active session was found. Do you want to restore it? [y/N] "
        )
        if answer and answer.lower() == "y":
            session = PomoSession.from_db(active_session)
        else:
            database.deactivate_all_sessions()

    if session is None:
        session = PomoSession()
        session.start()

    window = PomoTrackerWindow(session)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    ticker_task = loop.create_task(main_loop(session, window.app))

    try:
        loop.run_until_complete(window.run())
    finally:
        # On clean exit, deactivate the session
        if session.session_id:
            database.deactivate_session(session.session_id)

        ticker_task.cancel()
        # Cleanly shutdown remaining tasks
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()
        group = asyncio.gather(*tasks, return_exceptions=True)
        loop.run_until_complete(group)
        loop.close()


if __name__ == "__main__":
    run()
