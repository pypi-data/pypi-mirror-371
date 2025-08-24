from enum import Enum, auto
import json
from pomotracker import database


class State(Enum):
    IDLE = auto()
    WORKING = auto()
    BREAK = auto()
    LONG_BREAK = auto()
    PAUSED = auto()


class PomoSession:
    def __init__(
        self,
        work_duration: int = 25,
        break_duration: int = 5,
        long_break_duration: int = 15,
        pomos_before_long_break: int = 4,
        session_id: int = None,
    ):
        self.work_duration = work_duration * 60
        self.break_duration = break_duration * 60
        self.long_break_duration = long_break_duration * 60
        self.pomos_before_long_break = pomos_before_long_break

        self.state = State.IDLE
        self.pomo_cycles = 0
        self._remaining_time = 0
        self._borrow_mode = False
        self._borrowed_time = 0
        self._work_debt = []
        self._previous_state = None
        self.session_id = session_id

    def to_dict(self):
        return {
            "state": self.state.name,
            "pomo_cycles": self.pomo_cycles,
            "remaining_time": self._remaining_time,
            "borrow_mode": self._borrow_mode,
            "work_debt": self._work_debt,
        }

    @classmethod
    def from_db(cls, session_data):
        session = cls(session_id=session_data["id"])
        session.state = State[session_data["state"]]
        session.pomo_cycles = session_data["pomo_cycles"]
        session._remaining_time = session_data["remaining_time"]
        session._borrow_mode = bool(session_data["borrow_mode"])
        session._work_debt = json.loads(session_data["work_debt"])
        return session

    def start(self):
        self.state = State.WORKING
        self._remaining_time = self.work_duration
        if self.session_id is None:
            self.session_id = database.create_session(self.to_dict())

    def toggle_pause(self):
        if self.state == State.PAUSED:
            self.state = self._previous_state
        else:
            self._previous_state = self.state
            self.state = State.PAUSED
        self._save_state()

    def tick(self):
        if self.state in [State.PAUSED, State.IDLE]:
            return
        
        if self.state in [State.WORKING, State.BREAK, State.LONG_BREAK]:
            self._remaining_time -= 1

        if self.state == State.WORKING and self._borrow_mode:
            self._save_state()
            # In borrow mode, we allow the timer to go negative.
            return

        if self._remaining_time < 0:
            if self.state == State.WORKING:
                self.pomo_cycles += 1
                if self.pomo_cycles % self.pomos_before_long_break == 0:
                    self.state = State.LONG_BREAK
                    self._remaining_time = self.long_break_duration
                else:
                    self.state = State.BREAK
                    self._remaining_time = self.break_duration
            elif self.state in [State.BREAK, State.LONG_BREAK]:
                self.state = State.WORKING
                self._remaining_time = self._get_next_work_duration()
        
        self._save_state()

    def get_remaining_time(self) -> int:
        return self._remaining_time

    def toggle_borrow_mode(self):
        self._borrow_mode = not self._borrow_mode
        # If we are turning borrow mode OFF, check if we need to resolve the debt.
        if not self._borrow_mode:
            self._resolve_borrowing()
        self._save_state()

    def _resolve_borrowing(self):
        # Only resolve borrowing if the timer has gone into negative.
        if self._remaining_time < 0:
            time_over = -self._remaining_time

            self._work_debt = []
            debt = time_over
            while debt > 0:
                full_cycles = debt // self.work_duration
                for _ in range(full_cycles):
                    self._work_debt.append(0)
                debt %= self.work_duration
                
                if debt > 0:
                    self._work_debt.append(self.work_duration - debt)
                    debt = 0
            
            self.pomo_cycles += 1
            if self.pomo_cycles % self.pomos_before_long_break == 0:
                self.state = State.LONG_BREAK
                self._remaining_time = self.long_break_duration
            else:
                self.state = State.BREAK
                self._remaining_time = self.break_duration

    def stop_borrowing(self):
        """
        This method is deprecated and will be removed.
        Use toggle_borrow_mode.
        """
        self.toggle_borrow_mode()
    
    def _get_next_work_duration(self) -> int:
        if self._work_debt:
            return self._work_debt.pop(0)
        return self.work_duration

    def _save_state(self):
        if self.session_id:
            database.update_session(self.session_id, self.to_dict())