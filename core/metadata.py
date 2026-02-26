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
        """Método unificado para chamadas à API IGDB."""
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            response = requests.post(url, headers=headers, data=query)
            return response.json()
        except:
            return None

    def fetch_game_data(self, game_name, game_type, game_id=None):
        cached_data = self.cache.get_game(game_id, game_name)
        if cached_data: return cached_data

        if not self.access_token: return None
        
        game_name_clean = re.sub(r'\b(Disc|CD|Disk|Disco)\s*[1-4]\b', '', game_name, flags=re.IGNORECASE).strip()
        platform_id = 8 if game_type == "PS2" else 7
        
        fields = "fields name, summary, first_release_date, genres.name, rating, total_rating, involved_companies.company.name;"
        data = None

        if game_id:
            id_numeric = re.sub(r'[^0-9]', '', game_id)
            variants = [game_id, game_id.replace('-', ''), id_numeric]
            
            for vid in variants:
                if not vid or len(vid) < 3: continue 
                query = f'{fields} where external_games.uid = "{vid}" & platforms = ({platform_id}); limit 1;'
                data = self._api_call(query)
                if data: break

        if not data:
            clean_search = re.sub(r'[^a-zA-Z0-9\s]', '', game_name_clean)
            query = f'search "{clean_search}"; {fields} where platforms = ({platform_id}); limit 1;'
            data = self._api_call(query)

        if not data:
            clean_name = re.sub(r'\b(definitive edition|special edition|pt br|patch|patched|v\d+|hacked|mod|modded|fix)\b', '', game_name_clean, flags=re.IGNORECASE).strip()
            if clean_name != game_name_clean:
                query = f'search "{clean_name}"; {fields} where platforms = ({platform_id}); limit 1;'
                data = self._api_call(query)

        if not data or len(data) == 0:
            self.logger.warn(f"Metadados não encontrados para: {game_name}")
            return None
        
        game = data[0]
        translator = GoogleTranslator(source='en', target='pt')
        
        for key in ['summary']:
            if key in game and game[key]:
                try:
                    game[key] = translator.translate(game[key])
                except: pass
        
        if 'genres' in game:
            for g in game['genres']:
                try:
                    g['name'] = translator.translate(g['name'])
                except: pass
        
        cache_key = game_id if game_id else game_name
        self.cache.save_game(cache_key, game)
        
        return game