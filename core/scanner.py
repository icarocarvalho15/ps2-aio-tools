import os
import re
import pycdlib
from core.logger import Logger

logger = Logger()

GAME_ID_REGEX = re.compile(r'[A-Z]{4}_[0-9]{3}\.[0-9]{2}')

def extract_game_id_from_iso(iso_path: str) -> str | None:
    try:
        iso = pycdlib.PyCdlib()
        iso.open(iso_path)

        system_path = None

        children = iso.list_children(iso_path='/')

        for child in children:
            name = child.file_identifier().decode(errors="ignore").strip()

            if "SYSTEM.CNF" in name.upper():
                system_path = "/" + name
                break

        if not system_path:
            logger.error(f"SYSTEM.CNF não encontrado em {iso_path}")
            iso.close()
            return None

        with iso.open_file_from_iso(iso_path=system_path) as f:
            content = f.read().decode(errors="ignore")

        iso.close()

        match = GAME_ID_REGEX.search(content)

        if match:
            return match.group()

        logger.warning(f"Game ID não encontrado no SYSTEM.CNF: {iso_path}")
        return None

    except Exception as e:
        logger.error(f"Erro ao ler ISO {iso_path}: {e}")
        return None

def scan_isos(root_path: str, logger) -> list:
    results = []

    for file in os.listdir(root_path):
        if not file.lower().endswith(".iso"):
            continue

        full_path = os.path.join(root_path, file)

        logger.info(f"Processando ISO: {file}")

        game_id = extract_game_id_from_iso(full_path)

        if not game_id:
            continue

        results.append({
            "file_name": file,
            "full_path": full_path,
            "game_id": game_id,
            "size_bytes": os.path.getsize(full_path)
        })

        logger.info(f"ISO válida: {file} | ID: {game_id}")

    return results

def generate_opl_name(game_id: str, file_name: str, keep_id: bool = True) -> str:
    clean_name = sanitize_game_name(file_name)
    
    if keep_id:
        return f"{game_id}.{clean_name}.iso"
    
    return f"{clean_name}.iso"

def sanitize_game_name(file_name: str) -> str:
    name = re.sub(r'\.iso$', '', file_name, flags=re.IGNORECASE)
    game_id_pattern = r'[A-Z]{3,4}[_-][0-9]{3,5}[\._][0-9]{2}'
    name = re.sub(game_id_pattern, '', name)
    
    name = re.sub(r'[\._\-]', ' ', name)
    name = re.sub(r'[\(\[][^\]\.)]*[\)\]]', '', name)
    
    name = ' '.join(name.split()).title()
    
    return name.strip()

if __name__ == "__main__":
    test_logger = Logger()
    import sys

    if len(sys.argv) < 2:
        print(r"Uso: python scanner.py D:\PS2\HD\DVD")
        sys.exit(1)

    root_path = sys.argv[1]

    games = scan_isos(root_path, test_logger)

    print("\nResultado do Scanner:\n")
    for game in games:
        print(game)