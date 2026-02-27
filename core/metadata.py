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
            "SLUS_000.00": {"name": "Nostalgia Collection", "summary": "Coletânea de clássicos retrô.", "genres": [{"name": "Coletânea"}]},
            "SLUS_740.32": {"name": "The King Of Fighters 11 in 1", "summary": "Coletânea de jogos arcade do maior jogo de luta de todos os tempos.", "genres": [{"name": "Coletânea / Luta / Arcade"}]},
            "SLUS_774.47": {"name": "Anime Hero I", "summary": "Anime Hero I é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime.", "genres": [{"name": "Música"}]},
            "SLUS_774.48": {"name": "Anime Hero II Evolution", "summary": "Anime Hero II Evolution é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero I.", "genres": [{"name": "Música"}]},
            "SLUS_222.22": {"name": "Anime Hero III Revolution", "summary": "Anime Hero III Revolution é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero II.", "genres": [{"name": "Música"}]},
            "SLUS_216.72": {"name": "Anime Hero IV Spirit Burning", "summary": "Anime Hero IV Spirit Burning é um mod não oficial de Guitar Hero III para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero III.", "genres": [{"name": "Música"}]},
            "SLUS_216.73": {"name": "Anime Hero V Black Edition", "summary": "Anime Hero V Black Edition é um mod não oficial de Guitar Hero III para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero IV.", "genres": [{"name": "Música"}]},
            "SLUS_215.86": {"name": "Anime Hero Zero", "summary": "Anime Hero Zero é uma versão modificada não oficial de Guitar Hero II para PlayStation 2 que adiciona músicas de anime ao jogo.", "genres": [{"name": "Música"}]},
            "SLUS_215.87": {"name": "Anime Hero Zero 2", "summary": "Anime Hero Zero 2 é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero Zero.", "genres": [{"name": "Música"}]},
            "SLUS_261.63": {"name": "Anime Hero Zero 3", "summary": "Anime Hero Zero 3 é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero Zero.", "genres": [{"name": "Música"}]},
            "SLUS_416.34": {"name": "Anime Hero Zero ODLVE", "summary": "Anime Hero Zero ODLVE é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo pode ser considerada uma sequência do Anime Hero Zero.", "genres": [{"name": "Música"}]},
            "SLPS_255.05": {"name": "Namco x Capcom", "summary": "RPG de estratégia crossover desenvolvido pela Monolith Soft.", "genres": [{"name": "RPG"}]},
            "SLUS_210.10": {"name": "Nanobreaker", "summary": "Jogo de ação hack and slash da Konami.", "genres": [{"name": "Ação"}]}
        }

    def _get_access_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            response = requests.post(url, params=params)
            if response.status_code != 200:
                self.logger.error(f"Erro ao gerar Token: {response.status_code} - {response.text}")
                return None
            token = response.json().get("access_token")
            return token
        except Exception as e:
            self.logger.error(f"Erro de conexão na autenticação: {e}")
            return None

    def _api_call(self, query):
        """Força a query a ser uma string limpa e sem quebras de linha estranhas."""
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "text/plain"
        }
        clean_query = " ".join(query.split())
        try:
            response = requests.post(url, headers=headers, data=clean_query.encode('utf-8'))
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Erro IGDB {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Erro de conexão: {e}")
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
        fields = "fields name, summary, first_release_date, genres.name, rating, total_rating, involved_companies.company.name;"
        
        name_only = re.sub(r'\(.*?\)|\[.*?\]', '', game_name).strip()
        name_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', name_only).strip()
        
        data = None

        if game_id:
            id_raw = re.sub(r'[^a-zA-Z0-9]', '', game_id)
            data = self._api_call(f'search "{id_raw}"; {fields} where platforms = {platform_id};')

        if not data:
            data = self._api_call(f'search "{name_clean}"; {fields} where platforms = {platform_id}; limit 1;')

        if not data:
            data = self._api_call(f'search "{name_clean}"; {fields} limit 1;')

        if not data:
            data = self._api_call(f'search "{name_only}"; {fields} limit 1;')

        if not data or len(data) == 0:
            self.logger.warn(f"Metadados não encontrados após 4 tentativas: {game_name}")
            return None
        
        game = data[0]

        try:
            translator = GoogleTranslator(source='en', target='pt')
            if 'summary' in game and game['summary']:
                game['summary'] = translator.translate(game['summary'][:4000])
            if 'genres' in game:
                for g in game['genres']:
                    g['name'] = translator.translate(g['name'])
        except: pass

        if game_id: self.cache.save_game(game_id, game)
        self.cache.save_game(game_name, game)
        
        return game