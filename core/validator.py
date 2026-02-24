from pathlib import Path

class OPLValidator:
    REQUIRED_FOLDERS = ["DVD", "CD", "CFG", "POPS", "APPS", "ART", "VMC"]

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

        self.logger.ok("Dispositivo/Diretório root validado")
        return True

    def validate_structure(self):
        """Verifica e cria a estrutura de pastas necessária para o OPL."""
        self.logger.info("Validando estrutura de pastas OPL...")
        for folder in self.REQUIRED_FOLDERS:
            path = self.root / folder

            if path.exists():
                if path.is_dir():
                    self.logger.skip(f"Estrutura confirmada: {folder}/")
                else:
                    self.logger.warn(f"Conflito: {folder} existe mas não é uma pasta!")
            else:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.logger.ok(f"Pasta criada com sucesso: {folder}/")
                except Exception as e:
                    self.logger.error(f"Falha crítica ao criar {folder}: {e}")