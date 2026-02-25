import os
import re
from pathlib import Path

def execute_rename(item, keep_id, logger):
    """
    Renomeia arquivos de PS1 e PS2, limpando tags de região e lixo,
    mantendo a compatibilidade com a estrutura do OPL e POPStarter.
    """
    old_path = Path(item['full_path'])
    folder = old_path.parent
    ext = old_path.suffix
    name = old_path.stem

    name = re.sub(r'^[A-Z]{3,4}[_-][0-9]{3}\.[0-9]{2}\.', '', name)

    patterns = [
        r'\((USA|Europe|Japan|UK|France|Germany|Italy|Spain|Brazil|Australia|Portugal)\)',
        r'\((En,Es,It,De|En,Fr,De|En,Es,It|Multi\d+|En|Es|Pt|Br|En,Fr,Es)\)',
        r'(\[| \()v\d+(\.\d+)*(\]| \))|(\[| \()Rev \d+(\]| \))',
        r'\[(Hacked|Beta|Prototype|Alt|Demo|Translated|PT-BR|English|Mod|Modded|Patched|FIX)\]',
        r'\(ISO\)',
        r'\(Unl\)'
    ]

    clean_name = name
    for pattern in patterns:
        clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)

    if item['type'] != "PS1":
        clean_name = re.sub(r'\b(Disc|CD|Disk|Disco)\s*[1-4]\b', '', clean_name, flags=re.IGNORECASE)

    clean_name = re.sub(r'\s+', ' ', clean_name).strip()

    if item['type'] == "PS2" and item['game_id'] and keep_id:
        new_name = f"{item['game_id']}.{clean_name}{ext}"
    else:
        new_name = f"{clean_name}{ext}"

    new_path = folder / new_name

    if old_path != new_path:
        try:
            if not new_path.exists():
                os.rename(old_path, new_path)
                logger.ok(f"Renomeado ({item['type']}): {old_path.name} -> {new_name}")
                return str(new_path)
            else:
                logger.warn(f"Destino já existe, mantendo original: {new_name}")
                return str(old_path)
        except Exception as e:
            logger.error(f"Erro ao renomear {item['type']}: {e}")
            return str(old_path)
    
    return str(old_path)