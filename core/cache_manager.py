import json
import os
from pathlib import Path

class CacheManager:
    def __init__(self, logger):
        self.logger = logger
        self.cache_path = Path(__file__).parent.parent / "metadata_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self):
        """Carrega o arquivo de cache se ele existir."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Erro ao carregar cache: {e}")
                return {}
        return {}

    def get_game(self, game_id, game_name):
        """Tenta buscar no cache e garante que os dados sejam válidos."""
        data = None
        if game_id and game_id in self.cache:
            data = self.cache[game_id]
        elif game_name in self.cache:
            data = self.cache[game_name]
        if data and isinstance(data, dict) and len(data) > 0:
            return data
        return None

    def save_game(self, key, data):
        """Salva os dados de um jogo no cache."""
        if not data:
            return
        self.cache[key] = data
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar cache: {e}")