# PomoTracker

A simple Pomodoro tracker with a special "borrow time" feature.

## Installation

This project uses `uv` for package management.

1.  **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd pomotracker
    ```

2.  **Install dependencies:**
    ```sh
    uv pip sync --dev
    ```

## Usage

To run the application, use the following command:

```sh
pomotracker
```

Alternatively, you can run the main module directly:

```sh
python -m pomotracker.main
```

### Key Bindings

*   **b**: Toggle borrow mode
*   **p**: Pause/Resume the timer
*   **q**: Quit the application

## How Borrow Mode Works

When you are in a **working** session, you can enable "borrow mode" by pressing `b`. In this mode, the timer will continue even after it reaches zero, allowing you to continue working without interruption. When you stop borrowing (by pressing `b` again), the extra time will be subtracted from your future working sessions.

For example, if you have a `25-5` minute cycle and you work for 37 minutes, your next cycles will be adjusted to `37-5-13-5`.
