import re
from pathlib import Path

def sanitize(name):
    name = re.sub(r'\.(iso|vcd|elf)$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[A-Z]{3,4}[_-][0-9]{3}\.[0-9]{2}', '', name)
    name = re.sub(r'[\(\[][^\]\)]*[\)\]]', '', name)
    name = re.sub(r'[\._\-]', ' ', name)
    blacklist = r'\b(iso|bin|img|mod|modded|ps2|ps1|br|pt|usa|eur|jpn|rip|patched|vcd|v\d+)\b'
    name = re.sub(blacklist, '', name, flags=re.IGNORECASE)
    name = ' '.join(name.split()).title().strip()
    excecoes = {
        r"\bGta\b": "GTA",
        r"\bOpl\b": "OPL",
        r"\bGsm\b": "GSM",
        r"\bVmc\b": "VMC",
        r"\bII\b": "II",
        r"\bIII\b": "III",
        r"\bIV\b": "IV",
        r"\bV\b": "V",
        r"\bResident Evil\b": "Resident Evil"
    }
    for errado, correto in excecoes.items():
        name = re.sub(errado, correto, name)        
    return name

def execute_rename(item, keep_id, logger):
    old_path = Path(item['full_path'])
    clean = sanitize(item['file_name'])
    ext = old_path.suffix.lower()

    if item['type'] == "PS2" and keep_id and item['game_id']:
        formatted_id = item['game_id'].replace('-', '_')
        new_name = f"{formatted_id}.{clean}{ext}"
    else:
        new_name = f"{clean}{ext}"

    new_path = old_path.parent / new_name

    if old_path == new_path:
        return str(old_path)

    try:
        if not new_path.exists():
            old_path.rename(new_path)
            logger.ok(f"Renomeado: {new_name}")
            return str(new_path)
        else:
            logger.warn(f"Ignorado (já existe): {new_name}")
            return str(new_path)
    except Exception as e:
        logger.error(f"Erro no rename: {e}")
        return str(old_path)