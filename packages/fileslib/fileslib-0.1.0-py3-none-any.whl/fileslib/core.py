# This is a custom module
import os
import subprocess
import sys
import time

def file(path: str, msg: str | bytes = "", mode: str = "a", returns_content: bool = False, execute: bool = False, execution_delay: int | float = 0) -> str | None:
    """Function that handles fileslib (able to read, write, append, and execute)."""
    if mode == "r":
        raise ValueError("\"Mode\" parameter cannot be read mode. If you want the file contents set the \"returns_content\" parameter to \"True\" (bool).")
    file_mode = mode if mode in ("a", "w") else "w"
    bytes_ = "b" if isinstance(msg, bytes) else ""
    with open(path, file_mode + bytes_) as f:
        f.write(msg)
    if returns_content:
        with open(path, f"r{bytes_}") as f:
            return f.read()
    if execute and os.path.exists(path):
        time.sleep(execution_delay)
        if sys.platform == "win32":
            os.startfile(path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])