from pathlib import Path

class OPLValidator:
    REQUIRED_FOLDERS = ["DVD", "CD", "CFG", "POPS"]

    def __init__(self, root_path, logger):
        self.root = Path(root_path)
        self.logger = logger

    def validate_root(self):
        if not self.root.exists():
            self.logger.error(f"Root não existe: {self.root}")
            return False

        if not self.root.is_dir():
            self.logger.error(f"Root não é diretório: {self.root}")
            return False

        self.logger.ok("Root válido")
        return True

    def validate_structure(self):
        for folder in self.REQUIRED_FOLDERS:
            path = self.root / folder

            if path.exists():
                self.logger.skip(f"Pasta já existe: {folder}")
            else:
                try:
                    path.mkdir(parents=True)
                    self.logger.ok(f"Pasta criada: {folder}")
                except Exception as e:
                    self.logger.error(f"Erro ao criar pasta {folder}: {e}")