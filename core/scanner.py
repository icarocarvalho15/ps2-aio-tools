import os
import re
import pycdlib
from pathlib import Path

GAME_ID_REGEX = re.compile(r'[A-Z]{3,4}_[0-9]{3}\.[0-9]{2}')

def extract_id(path, game_type, logger):
    if game_type == "PS2":
        try:
            iso = pycdlib.PyCdlib()
            iso.open(path)
            for child in iso.list_children(iso_path='/'):
                name = child.file_identifier().decode(errors="ignore").strip()
                if "SYSTEM.CNF" in name.upper():
                    with iso.open_file_from_iso(iso_path="/" + name) as f:
                        content = f.read().decode(errors="ignore")
                    match = GAME_ID_REGEX.search(content)
                    iso.close()
                    return match.group().replace("_", "-") if match else None
            iso.close()
        except: return None
    elif game_type == "PS1":
        match = GAME_ID_REGEX.search(os.path.basename(path))
        return match.group().replace("_", "-") if match else None
    return None

def get_file_size_formatted(file_path):
    """Retorna o tamanho do arquivo formatado para o OPL."""
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb >= 1024:
        return f"{size_mb / 1024:.2f} GB"
    return f"{int(size_mb)} MB"

def scan_all(root_path, logger):
    root = Path(root_path)
    results = []
    mapping = {"DVD": "PS2", "CD": "PS2", "POPS": "PS1", "APPS": "APP"}

    for folder, game_type in mapping.items():
        dir_path = root / folder
        if not dir_path.exists(): continue

        for file in dir_path.iterdir():
            if file.suffix.lower() not in [".iso", ".vcd", ".elf"]: continue

            gid = extract_id(str(file), game_type, logger)
            
            if game_type == "PS2" and gid:
                cfg_name = f"{gid.replace('-', '_')}.cfg"
            elif game_type == "PS1":
                cfg_name = f"{file.name}.ELF.cfg"
            else:
                cfg_name = f"{file.name}.cfg"

            results.append({
                "type": game_type,
                "file_name": file.name,
                "full_path": str(file),
                "game_id": gid,
                "file_size": get_file_size_formatted(str(file)),
                "cfg_target": cfg_name,
                "cfg_exists": (root / "CFG" / cfg_name).exists()
            })
    return results