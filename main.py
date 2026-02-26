import argparse
from pathlib import Path
from core.logger import Logger
from core.validator import OPLValidator
from core.scanner import scan_all
from core.rename import execute_rename
from core.metadata import MetadataManager
from core.cfg_manager import CFGManager
from core.pops_manager import POPSManager

def main():
    parser = argparse.ArgumentParser(description="PS2 AIO Tools - DravDev")
    parser.add_argument("--root", required=True, help="Raiz do USB/HD")
    parser.add_argument("--scan-only", action="store_true", help="Apenas escaneia e exibe os resultados")
    parser.add_argument("--full", action="store_true", help="Executa todo o fluxo de automação")
    parser.add_argument("--rename", action="store_true", help="Apenas renomeia os arquivos")
    parser.add_argument("--pops", action="store_true", help="Apenas setup de PS1 (VMCs, Patches, TXTs)")
    parser.add_argument("--metadata", action="store_true", help="Apenas gera os arquivos CFG")
    parser.add_argument("--keep-id", action="store_true", help="Mantém ID no rename (PS2)")
    
    args = parser.parse_args()
    logger = Logger()

    validator = OPLValidator(args.root, logger)
    if not validator.validate_root(): return
    validator.validate_structure()

    logger.info("Escaneando arquivos...")
    items = scan_all(args.root, logger)
    
    for item in items:
        print(f"-> Encontrado: {item['file_name']} | Tipo: {item['type']} | ID: {item['game_id']}")

    if args.scan_only:
        logger.ok(f"Scan concluído para {len(items)} itens.")
        return

    do_rename = args.full or args.rename
    do_pops = args.full or args.pops
    do_metadata = args.full or args.metadata

    metadata_tool = MetadataManager(logger) if do_metadata else None
    cfg_tool = CFGManager(args.root, logger) if do_metadata else None
    pops_tool = POPSManager(args.root, logger) if do_pops else None

    if pops_tool:
        pops_tool.create_global_cheats()

    for item in items:
        if do_rename:
            item['full_path'] = execute_rename(item, args.keep_id, logger)
            path_obj = Path(item['full_path'])
            item['file_name'] = path_obj.name 
            nome_sem_ext = path_obj.stem
        else:
            nome_sem_ext = Path(item['full_path']).stem

        if item['type'] == "PS2" and item['game_id']:
            item['cfg_target'] = f"{item['game_id'].replace('-', '_')}.cfg"
        elif item['type'] == "PS1":
            item['cfg_target'] = f"XX.{nome_sem_ext}.ELF.cfg"
        else:
            item['cfg_target'] = f"{nome_sem_ext}.cfg"

        if do_pops and item['type'] == "PS1":
            pops_tool.setup_game(item, items)

        if do_metadata:
            cfg_full_path = Path(args.root) / "CFG" / item['cfg_target']
            if not cfg_full_path.exists():
                data = metadata_tool.fetch_game_data(nome_sem_ext, item['type'], item['game_id'])
                cfg_tool.generate_cfg(item, data)
            else:
                logger.skip(f"CFG já existe para: {item['cfg_target']}")

    if pops_tool:
        pops_tool.update_apps_config(items)

    logger.ok(f"Processamento concluído para {len(items)} itens.")

if __name__ == "__main__":
    main()