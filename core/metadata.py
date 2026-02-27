import os
import re
import requests
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from core.cache_manager import CacheManager

load_dotenv()

class MetadataManager:
    def __init__(self, logger):
        self.client_id = os.getenv("IGDB_CLIENT_ID")
        self.client_secret = os.getenv("IGDB_CLIENT_SECRET")
        self.logger = logger
        self.cache = CacheManager(logger)
        self.access_token = self._get_access_token()
        self.manual_db = {
            "SLPM_663.74": {"name": "Bomba Patch 2026", "summary": "O melhor mod de futebol brasileiro para PS2.", "genres": [{"name": "Esporte"}]},
            "SLES_556.73": {"name": "PES 2026", "summary": "O melhor mod de futebol brasileiro para PS2.", "genres": [{"name": "Esporte"}]},
            "LITE_000.01": {"name": "Nostalgia Collection", "summary": "Coletânea de clássicos retrô.", "genres": [{"name": "Coletânea"}]},
            "SLUS_740.32": {"name": "The King Of Fighters 11 in 1", "summary": "Coletânea de jogos arcade do maior jogo de luta de todos os tempos.", "genres": [{"name": "Coletânea / Luta / Arcade"}]},
            "SLUS_222.22": {"name": "Anime Hero III Revolution", "summary": "Anime Hero III Revolution é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero..", "genres": [{"name": "Música"}]}
        }

    def _get_access_token(self):
        if not self.client_id or not self.client_secret:
            self.logger.error("Credenciais IGDB não encontradas no arquivo .env")
            return None

        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            self.logger.error(f"Erro de autenticação IGDB: {e}")
            return None

    def _api_call(self, query):
        """Método com tratamento de erro e debug."""
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        try:
            response = requests.post(url, headers=headers, data=query)
            if response.status_code != 200:
                self.logger.error(f"Erro API IGDB ({response.status_code}): {response.text}")
                return None
            return response.json()
        except Exception as e:
            self.logger.error(f"Falha de conexão: {e}")
            return None

    def fetch_game_data(self, game_name, game_type, game_id=None):
        cached_data = self.cache.get_game(game_id, game_name)
        if cached_data: return cached_data

        if game_id and game_id in self.manual_db:
            manual_game = self.manual_db[game_id]
            self.cache.save_game(game_id, manual_game)
            return manual_game

        if not self.access_token: return None
        
        platform_id = 8 if game_type == "PS2" else 7
        fields = "fields name, summary, first_release_date, genres.name;"
        data = None

        if game_id:
            clean_id = re.sub(r'[^a-zA-Z0-9]', '', game_id)
            query = f'search "{clean_id}"; {fields} where platforms = {platform_id};'
            data = self._api_call(query)

        if not data or len(data) == 0:
            clean_name = re.sub(r'\(.*?\)|\[.*?\]', '', game_name)
            clean_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean_name).strip()
            
            query = f'search "{clean_name}"; {fields} where platforms = {platform_id}; limit 1;'
            data = self._api_call(query)

        if not data or not isinstance(data, list) or len(data) == 0:
            self.logger.warn(f"Metadados não encontrados para: {game_name}")
            return None
        
        game = data[0]

        try:
            translator = GoogleTranslator(source='en', target='pt')
            if 'summary' in game and game['summary']:
                game['summary'] = translator.translate(game['summary'][:4000])
            if 'genres' in game:
                for g in game['genres']:
                    g['name'] = translator.translate(g['name'])
        except:
            pass

        self.cache.save_game(game_id if game_id else game_name, game)
        return game