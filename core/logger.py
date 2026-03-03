import logging
from datetime import datetime
from pathlib import Path

class Logger:
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback

    def _log(self, msg, type_name):
        print(f"[{type_name}] {msg}")
        if self.gui_callback:
            self.gui_callback(f"[{type_name}] {msg}\n")
    
    def ok(self, msg):
        self._log(msg, "OK")
    def info(self, msg):
        self._log(msg, "INFO")
    def warn(self, msg):
        self._log(msg, "WARN")
    def error(self, msg):
        self._log(msg, "ERROR")
    def skip(self, msg):
        self._log(msg, "SKIP")