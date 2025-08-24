import subprocess
import asyncio

CMD = """
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
"""

async def notify(title: str, message: str):
    """Sends a desktop notification using osascript on macOS."""
    subprocess.call(["osascript", "-e", CMD, title, message])