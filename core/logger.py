from datetime import datetime

class Logger:
    def __init__(self):
        self.logs = []

    def _log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        self.logs.append(formatted)
        print(formatted)

    def info(self, message):
        self._log("INFO", message)

    def ok(self, message):
        self._log("OK", message)

    def skip(self, message):
        self._log("SKIP", message)

    def warn(self, message):
        self._log("WARN", message)

    def error(self, message):
        self._log("ERROR", message)

    def export(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            for line in self.logs:
                f.write(line + "\n")