import sys
import time

class VMLogger:
    def __init__(self, debug_mode: bool = False, component: str = "VM"):
        self.debug_mode = debug_mode
        self.component = component

    def debug(self, message: str):
        if self.debug_mode:
            print(self._format_message("DEBUG", message), file=sys.stderr)

    def info(self, message: str):
        print(self._format_message("INFO", message), file=sys.stderr)

    def warning(self, message: str):
        print(self._format_message("WARNING", message), file=sys.stderr)

    def error(self, message: str):
        print(self._format_message("ERROR", message), file=sys.stderr)

    def _format_message(self, level: str, message: str) -> str:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}][{level}][{self.component}] {message}"
