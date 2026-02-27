import os
import re
import pycdlib
from pathlib import Path

GAME_ID_REGEX = re.compile(r'[A-Z]{3,4}[_-][0-9]{3}\.[0-9]{2}')

def _get_disc_suffix(file_name):
    """Detecta se o arquivo é parte de um jogo multi-disco."""
    match = re.search(r'\b(Disc|CD|Disk|Disco)\s*([1-4])\b', file_name, re.IGNORECASE)
    if match:
        return f" (Disc {match.group(2)})"
    return ""

def extract_id(path, game_type, logger):
    OFFICIAL_ID_REGEX = re.compile(r'\b(S[LC][EUP][S_A])[_-](\d{3})\.(\d{2})\b', re.IGNORECASE)

    GENERIC_ID_REGEX = re.compile(r'[A-Z]{3,4}[_-][0-9]{3}\.[0-9]{2}')
    
    BLACKLIST_IDS = ["SCRP_000.00", "BUM_000.00", "000_00.00"]

    def clean_found_id(match):
        """Formata o ID encontrado para o padrão OPL (AAAA_000.00)."""
        if isinstance(match, tuple):
            prefix, n1, n2 = match
            return f"{prefix.upper().replace('-', '_')}_{n1}.{n2}"
        
        found = match.group().upper().replace('-', '_')
        return found

    if game_type == "PS2":
        try:
            iso = pycdlib.PyCdlib()
            iso.open(path)
            
            for child in iso.list_children(iso_path='/'):
                name = child.file_identifier().decode(errors="ignore").strip().upper()
                if "SYSTEM.CNF" in name:
                    try:
                        with iso.open_file_from_iso(iso_path="/" + name) as f:
                            content = f.read().decode(errors="ignore")
                            match = OFFICIAL_ID_REGEX.search(content)
                            if match:
                                iso.close()
                                return clean_found_id(match.groups())
                    except: pass
            
            for child in iso.list_children(iso_path='/'):
                name = child.file_identifier().decode(errors="ignore").strip().upper()
                match = OFFICIAL_ID_REGEX.search(name)
                if match and match.group() not in BLACKLIST_IDS:
                    iso.close()
                    return clean_found_id(match.groups())
            iso.close()
        except: pass

    try:
        with open(path, "rb") as f:
            chunk = f.read(15 * 1024 * 1024) 
            content = chunk.decode(errors="ignore")
            
            matches = OFFICIAL_ID_REGEX.findall(content)
            for m in matches:
                candidate = clean_found_id(m)
                if candidate not in BLACKLIST_IDS:
                    return candidate
            
            match = GENERIC_ID_REGEX.search(content)
            if match and match.group().upper() not in BLACKLIST_IDS:
                return match.group().upper().replace('-', '_')
    except Exception:
        pass
        
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
    mapping = {"DVD": "PS2", "CD": "PS2", "POPS": "PS1", "VCD": "PS1", "APPS": "APP"}

    for folder, game_type in mapping.items():
        dir_path = root / folder
        if not dir_path.exists(): continue

        for file in dir_path.iterdir():
            if file.is_dir(): continue
            
            ext = file.suffix.lower()

            if game_type == "PS1" and ext == ".elf": continue
            if ext not in [".iso", ".vcd", ".elf"]: continue

            gid = extract_id(str(file), game_type, logger)
            
            disc_suffix = _get_disc_suffix(file.name)
            
            if game_type == "PS2" and gid:
                cfg_name = f"{gid}.cfg"
            elif game_type == "PS1":
                cfg_name = f"XX.{file.stem}.ELF.cfg"
            else:
                cfg_name = f"{file.name}.ELF.cfg"

            results.append({
                "type": game_type,
                "file_name": file.name,
                "full_path": str(file),
                "game_id": gid,
                "disc_suffix": disc_suffix,
                "file_size": get_file_size_formatted(str(file)),
                "cfg_target": cfg_name,
                "cfg_exists": (root / "CFG" / cfg_name).exists()
            })
    return results