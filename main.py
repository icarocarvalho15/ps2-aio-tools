import argparse
from core.logger import Logger
from core.validator import OPLValidator

def main():
    parser = argparse.ArgumentParser(description="PS2 AIO Tools")
    parser.add_argument("--root", required=True, help="Caminho da raiz do USB")
    parser.add_argument("--ps2cfg", action="store_true", help="Gerar CFG PS2")
    parser.add_argument("--pops", action="store_true", help="Organizar POPS")
    parser.add_argument("--rename", action="store_true", help="Limpar nomes")

    args = parser.parse_args()

    logger = Logger()
    logger.info("PS2 AIO Tools iniciado")

    validator = OPLValidator(args.root, logger)

    if not validator.validate_root():
        logger.error("Encerrando por root inválido")
        return

    validator.validate_structure()

    logger.ok("Validação concluída")

if __name__ == "__main__":
    main()