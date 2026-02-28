import os
from pathlib import Path

class CFGManager:
    def __init__(self, root_path, logger):
        self.cfg_dir = Path(root_path) / "CFG"
        self.logger = logger

    def generate_cfg(self, item, metadata):
        if not metadata: return

        cfg_path = self.cfg_dir / item['cfg_target']
        
        p = metadata.get('players', '1')
        r = metadata.get('rating', '5')

        content = [
            "CfgVersion=8",
            "$ConfigSource=1",
            f"Title={metadata.get('name', item['file_name'])}",
            f"Players=players/{p}",
            f"PlayersText={p}",
            f"Genre={metadata.get('genre', 'Outros')}",
            f"Release={metadata.get('release_date', 'Desconhecido')}",
            f"Developer={metadata.get('developer', 'Desconhecido')}",
            f"Rating=rating/{r}",
            f"RatingText={r}",
            "Vmode=vmode/ntsc",
            "VmodeText=NTSC",
            "Scan=scan/480p3",
            "ScanText=480p (GSM)",
            f"Description={metadata.get('summary', '')}"
        ]

        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content))
            self.logger.ok(f"CFG gerado do {metadata.get('name', item['file_name'])} - {item['cfg_target']}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar CFG do {metadata.get('name', item['file_name'])} - {item['cfg_target']}: {e}")