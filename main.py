import argparse
import os
from core.logger import Logger
from core.validator import OPLValidator
from core.scanner import generate_opl_name, scan_isos, sanitize_game_name

def main():
    parser = argparse.ArgumentParser(description="PS2 AIO Tools")
    parser.add_argument("--root", required=True, help="Caminho da raiz do USB")
    parser.add_argument("--ps2cfg", action="store_true", help="Gerar CFG PS2")
    parser.add_argument("--pops", action="store_true", help="Organizar POPS")
    parser.add_argument("--scan", action="store_true", help="Escanear arquivos")
    parser.add_argument("--rename", action="store_true", help="Limpar nomes")
    parser.add_argument("--keep-id", action="store_true", help="Mantém o ID do jogo no início do nome")

    args = parser.parse_args()
    logger = Logger()
    logger.info("PS2 AIO Tools iniciado")

    validator = OPLValidator(args.root, logger)
    if not validator.validate_root():
        return

    validator.validate_structure()

    if args.scan:
        dvd_path = os.path.join(args.root, "DVD")
        logger.info(f"Escaneando diretório: {dvd_path}")
        
        games = scan_isos(dvd_path, logger)
        
        for game in games:
            old_name = game['file_name']
            new_name = f"{game['game_id']}.{old_name}"
            logger.info(f"Sugestão de renomeio: {old_name} -> {new_name}")

    logger.ok("Validação concluída")

    if args.rename:
        dvd_path = os.path.join(args.root, "DVD")
        logger.info(f"Iniciando renomeação em: {dvd_path}")
        
        games = scan_isos(dvd_path, logger)
        
        for game in games:
            old_path = game['full_path']
            
            new_file_name = generate_opl_name(game['game_id'], game['file_name'], args.keep_id)
            
            new_path = os.path.join(dvd_path, new_file_name)
            
            if old_path == new_path:
                logger.skip(f"Já está padronizado: {new_file_name}")
                continue
                
            try:
                if os.path.exists(new_path):
                    logger.warn(f"Conflito: {new_file_name} já existe.")
                    continue

                os.rename(old_path, new_path)
                logger.ok(f"Renomeado: {new_file_name}")
            except Exception as e:
                logger.error(f"Erro ao renomear {game['file_name']}: {e}")

if __name__ == "__main__":
    main()