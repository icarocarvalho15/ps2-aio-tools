import argparse
import re
from pathlib import Path
from core.logger import Logger
from core.validator import OPLValidator
from core.scanner import scan_all
from core.rename import execute_rename
from core.metadata import MetadataManager
from core.cfg_manager import CFGManager
from core.pops_manager import POPSManager

def main_logic(args, gui_callback=None):
    """Lógica principal separada para suportar CLI e GUI. gui_callback: Função opcional para enviar logs para a interface."""
    logger = Logger(gui_callback=gui_callback)

    validator = OPLValidator(args.root, logger)
    if not validator.validate_root():
        return
    validator.validate_structure(silent=False)

    items = scan_all(args.root, logger)
    
    if args.filter:
        original_count = len(items)
        items = [i for i in items if args.filter.lower() in i['file_name'].lower()]
        logger.info(f"Filtro aplicado: '{args.filter}'. Itens selecionados: {len(items)}")
    
    if args.scan_only:
        for item in items:
            logger.info(f"-> Encontrado: {item['file_name']} | ID: {item['game_id']}")
        return

    do_rename = args.full or args.rename
    do_pops = args.full or args.pops
    do_metadata = args.full or args.metadata

    metadata_tool = MetadataManager(logger) if do_metadata else None
    cfg_tool = CFGManager(args.root, logger) if do_metadata else None
    pops_tool = POPSManager(args.root, logger) if do_pops else None

    if do_pops and pops_tool:
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
            clean_id = item['game_id'].replace('-', '_')
            item['cfg_target'] = f"{clean_id}.cfg"
        elif item['type'] == "PS1":
            display_name = re.sub(r'^XX\.', '', nome_sem_ext)
            item['cfg_target'] = f"XX.{display_name}.ELF.cfg"
        else:
            item['cfg_target'] = f"{nome_sem_ext}.ELF.cfg"

        if do_pops and item['type'] == "PS1":
            pops_tool.setup_game(item, items)

        if do_metadata:
            cfg_full_path = Path(args.root) / "CFG" / item['cfg_target']

            if not cfg_full_path.exists() or args.filter:
                data = metadata_tool.fetch_game_data(nome_sem_ext, item['type'], item['game_id'])
                if data:
                    cfg_tool.generate_cfg(item, data)
            else:
                logger.skip(f"CFG já existe: {item['cfg_target']}")

    if do_pops and pops_tool:
        pops_tool.update_apps_config(items)

    logger.ok(f"Processamento concluído para {len(items)} itens.")

def main():
    """Ponto de entrada para uso via CLI (Terminal)"""
    parser = argparse.ArgumentParser(description="PS2 AIO Tools - DravDev")
    parser.add_argument("--root", required=True, help="Raiz do USB/HDD")
    parser.add_argument("--scan-only", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--rename", action="store_true")
    parser.add_argument("--pops", action="store_true")
    parser.add_argument("--metadata", action="store_true")
    parser.add_argument("--keep-id", action="store_true")
    parser.add_argument("--filter", help="Filtra por nome")
    
    args = parser.parse_args()
    main_logic(args)

if __name__ == "__main__":
    main()