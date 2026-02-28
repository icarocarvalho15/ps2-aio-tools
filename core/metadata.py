import os
import re
import requests
from dotenv import load_dotenv
from datetime import datetime
from deep_translator import GoogleTranslator
from core.cache_manager import CacheManager

load_dotenv()

class MetadataManager:
    def __init__(self, logger):
        self.api_key = os.getenv("THEGAMESDB_API_KEY")
        self.base_url = "https://api.thegamesdb.net/v1/"
        self.logger = logger
        self.cache = CacheManager(logger)
        
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
        }

        self.dev_map = {}
        self.genre_map = {}
        self._load_maps()

    def _load_maps(self):
        """Sincroniza os dicionários de IDs da API TheGamesDB."""
        try:
            r_gen = requests.get(f"{self.base_url}Genres", params={"apikey": self.api_key}, timeout=10)
            if r_gen.status_code == 200:
                data = r_gen.json().get('data', {}).get('genres', {})
                self.genre_map = {str(k): v['name'] for k, v in data.items()}

            r_dev = requests.get(f"{self.base_url}Developers", params={"apikey": self.api_key}, timeout=10)
            if r_dev.status_code == 200:
                data = r_dev.json().get('data', {}).get('developers', {})
                self.dev_map = {str(k): v['name'] for k, v in data.items()}
        except:
            self.logger.warn("Aviso: Não foi possível sincronizar mapas de IDs da API.")

    def fetch_game_data(self, game_name, game_type, game_id=None):
        if game_id and game_id in self.manual_db:
            m = self.manual_db[game_id]
            raw_genre = m.get('genre') or m.get('genres')
            if isinstance(raw_genre, list) and len(raw_genre) > 0:
                final_genre = raw_genre[0].get('name', 'Outros')
            else:
                final_genre = str(raw_genre) if raw_genre else "Outros"
            return {
                "name": m.get('name', game_name),
                "summary": m.get('summary', 'Sem descrição.'),
                "genre": final_genre,
                "release_date": "Desconhecido",
                "rating": "5",
                "players": "1",
                "developer": "Custom/Mod"
            }

        cached = self.cache.get_game(game_id, game_name)
        if cached: return cached

        platform_id = 11 if game_type == "PS2" else 10
        clean_search = re.sub(r'\(.*?\)|\[.*?\]', '', game_name).strip()

        params = {
            "apikey": self.api_key, 
            "name": clean_search, 
            "filter[platform]": platform_id,
            "include": "developers,genres", 
            "fields": "overview,release_date,rating,players,developers,genres"
        }

        try:
            response = requests.get(f"{self.base_url}Games/ByGameName", params=params, timeout=15)
            res = response.json()

            if res.get('code') == 200 and res['data']['count'] > 0:
                games = res['data']['games']
                include_data = res.get('include', {})

                valid_with_desc = [g for g in games if g.get('overview') and len(g.get('overview')) > 10]
                
                if valid_with_desc:
                    game = min(valid_with_desc, key=lambda x: len(x['game_title']))
                else:
                    game = min(games, key=lambda x: len(x['game_title']))

                display_name = game['game_title']
                display_name = re.sub(r'\(.*?\)|\[.*?\]', '', display_name).strip()

                genre_list = []
                genre_ids = game.get('genres', []) or []
                genre_trans = {
                    "Action": "Ação", "Adventure": "Aventura", "Horror": "Terror",
                    "Shooter": "Tiro", "Racing": "Corrida", "Sports": "Esportes",
                    "Role-playing (RPG)": "RPG", "Fighting": "Luta", "Platform": "Plataforma"
                }
                
                for g_id in genre_ids:
                    g_id_str = str(g_id)
                    name = include_data.get('genres', {}).get(g_id_str, {}).get('name') or self.genre_map.get(g_id_str)
                    if name: genre_list.append(genre_trans.get(name, name))
                
                genre_final = " / ".join(genre_list) if genre_list else "Ação"

                raw_ov = game.get('overview', '')
                desc = "Gerado por PS2 AIO Tools."
                if raw_ov:
                    try:
                        translated = GoogleTranslator(source='auto', target='pt').translate(raw_ov[:1000])
                        clean_text = re.sub(r'[\r\n\t]+', ' ', translated)
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                        desc = (clean_text[:252].rstrip() + "...") if len(clean_text) > 255 else clean_text
                    except:
                        desc = raw_ov[:252] + "..."

                date_fmt = "Desconhecido"
                if game.get('release_date'):
                    try: 
                        date_fmt = datetime.strptime(game['release_date'].split(' ')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
                    except: 
                        date_fmt = game['release_date']

                dev_id = str(game.get('developers', [0])[0])
                developer = include_data.get('developers', {}).get(dev_id, {}).get('name') or self.dev_map.get(dev_id, "Desconhecido")

                processed = {
                    "name": display_name,
                    "summary": desc,
                    "release_date": date_fmt,
                    "rating": "4",
                    "players": str(game.get('players', '1')),
                    "developer": developer,
                    "genre": genre_final
                }
                
                self.cache.save_game(game_id if game_id else game_name, processed)
                return processed

        except Exception as e:
            self.logger.error(f"Erro no processamento de {game_name}: {e}")
            
        return None