from pomotracker.session import PomoSession, State


def test_initial_state():
    session = PomoSession()
    assert session.state == State.IDLE
    assert session.pomo_cycles == 0


def test_start_session():
    session = PomoSession()
    session.start()
    assert session.state == State.WORKING
    assert session.get_remaining_time() == 25 * 60


def test_work_to_break_transition():
    session = PomoSession(work_duration=1, break_duration=1)
    session.start()
    assert session.state == State.WORKING
    # Simulate 1 minute of work
    for _ in range(1 * 60):
        session.tick()
    assert session.get_remaining_time() == 0
    session.tick()  # One more tick to trigger transition
    assert session.state == State.BREAK
    assert session.get_remaining_time() == 1 * 60


def test_break_to_work_transition():
    session = PomoSession(work_duration=1, break_duration=1)
    session.start()
    
    # Complete a full work cycle to transition to break
    for _ in range(1 * 60 + 1):
        session.tick()
    assert session.state == State.BREAK
    assert session.pomo_cycles == 1

    # Complete the break cycle to transition back to work
    for _ in range(1 * 60 + 1):
        session.tick()
    
    assert session.state == State.WORKING
    assert session.get_remaining_time() == 1 * 60


def test_borrow_mode_simple_case():
    """Test the 37-5-13-5 scenario."""
    session = PomoSession(work_duration=25, break_duration=5)
    session.start()
    session.toggle_borrow_mode()

    # Simulate 37 minutes of work
    for _ in range(37 * 60):
        session.tick()

    assert session.state == State.WORKING
    session.toggle_borrow_mode() # Stop borrowing

    assert session.state == State.BREAK
    assert session.get_remaining_time() == 5 * 60

    # Finish the break
    for _ in range(5 * 60 + 1):
        session.tick()

    assert session.state == State.WORKING
    assert session.get_remaining_time() == 13 * 60


def test_borrow_mode_across_multiple_cycles():
    """Test borrowing more time than one cycle's duration."""
    session = PomoSession(work_duration=25, break_duration=5, long_break_duration=15, pomos_before_long_break=4)
    session.start()
    session.toggle_borrow_mode()

    # Simulate 60 minutes of work
    for _ in range(60 * 60):
        session.tick()

    session.toggle_borrow_mode() # Stop borrowing

    assert session.state == State.BREAK
    assert session.get_remaining_time() == 5 * 60

    # Finish the break
    for _ in range(5 * 60 + 1):
        session.tick()

    # Next work cycle should be 0
    assert session.state == State.WORKING
    assert session.get_remaining_time() == 0
    session.tick()

    # Should go to next break
    assert session.state == State.BREAK

    # Finish the break
    for _ in range(5 * 60 + 1):
        session.tick()

    # The following work cycle should be 15 mins (25 - 10 borrowed)
    assert session.state == State.WORKING
    assert session.get_remaining_time() == 15 * 60

def test_borrow_mode_without_going_over():
    """Test toggling borrow mode off before the timer ends."""
    session = PomoSession(work_duration=25, break_duration=5)
    session.start()
    
    # Tick for 10 minutes
    for _ in range(10 * 60):
        session.tick()

    session.toggle_borrow_mode() # Enable
    assert session._borrow_mode is True

    # Tick for another 5 minutes
    for _ in range(5 * 60):
        session.tick()
    
    session.toggle_borrow_mode() # Disable
    assert session._borrow_mode is False
    assert session.state == State.WORKING
    assert session.get_remaining_time() == 10 * 60
