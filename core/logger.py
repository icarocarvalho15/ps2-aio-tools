from datetime import datetime

class Logger:
    def _log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def info(self, msg): self._log("INFO", msg)
    def ok(self, msg): self._log("OK", msg)
    def warn(self, msg): self._log("WARN", msg)
    def error(self, msg): self._log("ERROR", msg)
    def skip(self, msg): self._log("SKIP", msg)