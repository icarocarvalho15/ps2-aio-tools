import os
from datetime import datetime
from pathlib import Path
import re

class CFGManager:
    def __init__(self, root_path, logger):
        self.root = root_path
        self.logger = logger
        self.cfg_dir = os.path.join(self.root, "CFG")

    def _convert_rating(self, metadata):
        """Tenta pegar a melhor nota disponível e converte 0-100 para 1-5."""
        if metadata is None: return "3"
        raw_score = metadata.get('total_rating') or metadata.get('rating') or 75
        score = round(raw_score / 20)
        return str(max(1, min(5, score)))

    def _format_date(self, timestamp):
        """Converte timestamp IGDB para DD/MM/YYYY."""
        if not timestamp: return "Desconhecido"
        return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y")

    def _get_players_info(self, metadata):
        """Analisa os modos de jogo para definir a quantidade de jogadores."""
        modes = [m['name'] for m in metadata.get('game_modes', [])]
        multiplayer_terms = ['Multiplayer', 'Co-operative', 'Split screen']
        if any(term in modes for term in multiplayer_terms):
            return "2", "2"
        return "1", "1"

    def generate_cfg(self, item, metadata=None):
        target_path = os.path.join(self.cfg_dir, item['cfg_target'])
        m = metadata if metadata else {}
        name_clean = Path(item['file_name']).stem
        display_title = re.sub(r'^[A-Z]{3,4}[_-][0-9]{3}\.[0-9]{2}\.', '', name_clean)
        display_title = re.sub(r'^XX\.', '', display_title)
        display_title = re.sub(r'\b(Disc|CD|Disk|Disco)\s*[1-4]\b', '', display_title, flags=re.IGNORECASE).strip()
        base_title = m.get('name', display_title)
        title = base_title
        desc = m.get('summary', 'Gerado por PS2 AIO Tools.')
        if len(desc) > 252: desc = desc[:252] + "..."
        developer = "Desconhecido"
        if 'involved_companies' in m:
            for corp in m['involved_companies']:
                if corp.get('developer'):
                    developer = corp['company']['name']
                    break
        release_raw = m.get('first_release_date')
        release_date = datetime.fromtimestamp(release_raw).strftime("%d/%m/%Y") if release_raw else "Desconhecido"
        genres_list = m.get('genres', [])
        genre = " / ".join([g['name'] for g in genres_list]) if genres_list else "Desconhecido"
        rating_val = self._convert_rating(metadata)
        players_val, players_text = self._get_players_info(m)

        content = [
            "CfgVersion=8",
            "$ConfigSource=1",
            f"Title={title}",
            f"Players=players/{players_val}",
            f"PlayersText={players_text}",
            f"Genre={genre}",
            f"Release={release_date}",
            f"Developer={developer}",
            f"Rating=rating/{rating_val}",
            f"RatingText={rating_val}",
            "Vmode=vmode/ntsc",
            "VmodeText=NTSC",
            "Scan=scan/480p3",
            "ScanText=480p (GSM)",
            f"Description={desc}"
        ]

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content))
            self.logger.ok(f"CFG Gerado: {item['cfg_target']}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar CFG: {e}")