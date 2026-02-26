import logging
from datetime import datetime
from pathlib import Path

class Logger:
    def __init__(self):
        log_file = Path(__file__).parent.parent / "session_history.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )

    def info(self, msg):
        print(f"[INFO] {msg}")
        logging.info(msg)

    def error(self, msg):
        print(f"[ERRO] {msg}")
        logging.error(msg)
        
    def ok(self, msg):
        print(f"[OK] {msg}")
        logging.info(f"SUCESSO: {msg}")

    def skip(self, msg):
        print(f"[SKIP] {msg}")
        logging.info(f"PULADO: {msg}")

    def warn(self, msg):
        print(f"[AVISO] {msg}")
        logging.warning(msg)