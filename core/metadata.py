import os
import re
import requests
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

load_dotenv()

class MetadataManager:
    def __init__(self, logger):
        self.client_id = os.getenv("IGDB_CLIENT_ID")
        self.client_secret = os.getenv("IGDB_CLIENT_SECRET")
        self.logger = logger
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
        if not self.access_token: return None
        
        game_name_clean = re.sub(r'\b(Disc|CD|Disk)\s*[1-4]\b', '', game_name, flags=re.IGNORECASE).strip()
        
        platform_id = 8 if game_type == "PS2" else 7
        data = None

        if game_id:
            variants = [game_id, game_id.replace('-', ''), game_id.replace('.', '').replace('-', '')]
            for vid in variants:
                query = f'fields name, summary, first_release_date, genres.name, game_modes.name, rating, total_rating, involved_companies.developer, involved_companies.company.name; where external_games.uid = "{vid}" & platforms = ({platform_id}); limit 1;'
                data = self._api_call(query)
                if data: break

        if not data:
            clean_search = re.sub(r'^[A-Z]{3,4}[_-][0-9]{3}\.[0-9]{2}\.', '', game_name_clean)
            query = f'search "{clean_search}"; fields name, summary, first_release_date, genres.name, game_modes.name, rating, total_rating, involved_companies.developer, involved_companies.company.name; where platforms = ({platform_id}); limit 1;'
            data = self._api_call(query)

        if not data:
            clean_name = re.sub(r'\b(definitive edition|special edition|pt br|patch|patched|v\d+|hacked|mod|modded)\b', '', game_name_clean, flags=re.IGNORECASE).strip()
            if clean_name != game_name_clean:
                query = f'''
                    search "{clean_name}"; 
                    fields name, summary, first_release_date, genres.name, game_modes.name, rating, total_rating,
                    involved_companies.developer, involved_companies.company.name;
                    where platforms = ({platform_id});
                    limit 1;
                '''
                data = self._api_call(query)

        if not data:
            self.logger.warn(f"Metadados não encontrados para: {game_name}")
            return None
        
        game = data[0]
        
        translator = GoogleTranslator(source='en', target='pt')
        
        if 'summary' in game:
            try:
                game['summary'] = translator.translate(game['summary'])
            except: pass
        
        if 'genres' in game:
            for g in game['genres']:
                try:
                    g['name'] = translator.translate(g['name'])
                except: pass
        
        return game