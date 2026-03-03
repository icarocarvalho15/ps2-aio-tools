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
            "SLPM_663.74": {"name": "Bomba Patch 2026", "summary": "O melhor mod de futebol brasileiro para PS2.", "genre": "Esporte"},
            "SLES_556.73": {"name": "PES 2026", "summary": "O melhor mod de futebol brasileiro para PS2.", "genre": "Esporte"},
            "LITE_000.01": {"name": "Nostalgia Collection", "summary": "Coletânea de clássicos retrô.", "genre": "Coletânea"},
            "SLUS_000.00": {"name": "Nostalgia Collection", "summary": "Coletânea de clássicos retrô.", "genre": "Coletânea"},
            "SLUS_740.32": {"name": "The King of Fighters 11 in 1", "summary": "Coletânea de jogos arcade do maior jogo de luta de todos os tempos.", "genre": "Coletânea / Luta / Arcade"},
            "SLUS_774.47": {"name": "Anime Hero I", "summary": "Anime Hero I é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime.", "genre": "Música"},
            "SLUS_774.48": {"name": "Anime Hero II Evolution", "summary": "Anime Hero II Evolution é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero I.", "genre": "Música"},
            "SLUS_222.22": {"name": "Anime Hero III Revolution", "summary": "Anime Hero III Revolution é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero II.", "genre": "Música"},
            "SLUS_216.72": {"name": "Anime Hero IV Spirit Burning", "summary": "Anime Hero IV Spirit Burning é um mod não oficial de Guitar Hero III para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero III.", "genre": "Música"},
            "SLUS_216.73": {"name": "Anime Hero V Black Edition", "summary": "Anime Hero V Black Edition é um mod não oficial de Guitar Hero III para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero IV.", "genre": "Música"},
            "SLUS_215.86": {"name": "Anime Hero Zero", "summary": "Anime Hero Zero é uma versão modificada não oficial de Guitar Hero II para PlayStation 2 que adiciona músicas de anime ao jogo.", "genre": "Música"},
            "SLUS_215.87": {"name": "Anime Hero Zero 2", "summary": "Anime Hero Zero 2 é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero Zero.", "genre": "Música"},
            "SLUS_261.63": {"name": "Anime Hero Zero 3", "summary": "Anime Hero Zero 3 é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo é uma sequência do Anime Hero Zero.", "genre": "Música"},
            "SLUS_416.34": {"name": "Anime Hero Zero ODLVE", "summary": "Anime Hero Zero ODLVE é um mod não oficial de Guitar Hero II para PlayStation 2 que adiciona música de anime. O jogo pode ser considerada uma sequência do Anime Hero Zero.", "genre": "Música"}
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
            return {"name": m['name'], "summary": m['summary'], "genre": m.get('genre', 'Outros'), 
                    "release_date": "Desconhecido", "rating": "5", "players": "1", "developer": "Desconhecido"}
        
        cached = self.cache.get_game(game_id, game_name)
        if cached: return cached

        search_term = re.sub(r'\(.*?\)|\[.*?\]', '', game_name)
        search_term = re.sub(r'(?i)\b(Disc|Disco|CD|Disk|Part|PDC|DVD|Leon|Claire)\s*[0-9]*\b', '', search_term).strip()
        
        platform_id = 11 if game_type == "PS2" else 10
        games = []
        include_data = {}

        try:
            params = {
                "apikey": self.api_key,
                "name": search_term,
                "filter[platform]": platform_id,
                "include": "developers,genres",
                "fields": "overview,release_date,rating,players,developers,genres"
            }
            r = requests.get(f"{self.base_url}Games/ByGameName", params=params, timeout=15)
            res = r.json()
            if res.get('code') == 200:
                games = res['data']['games']
                include_data = res.get('include', {})
        except: pass

        if not games: return None

        valid_desc_games = [
            g for g in games 
            if g.get('overview') and len(g.get('overview')) > 50
            and not any(word in g.get('overview').lower() for word in [' mod ', ' hack', ' fan-made', ' version by'])
        ]

        has_digit_search = any(char.isdigit() for char in search_term)

        if valid_desc_games:
            best_match = None
            for g in valid_desc_games:
                api_title = g['game_title'].lower()
                has_digit_api = any(char.isdigit() for char in api_title)
                
                if has_digit_search != has_digit_api: continue
                
                if search_term.lower() in api_title:
                    best_match = g
                    break
            
            game = best_match if best_match else max(valid_desc_games, key=lambda x: len(x.get('overview')))
        else:
            game = min(games, key=lambda x: len(x['game_title']))

        display_name = game['game_title']
        display_name = re.sub(r'\(.*?\)|\[.*?\]', '', display_name)
        display_name = re.sub(r'(?i)\b(Greatest Hits|Platinum|The Best|Selection|Limited Edition|Special Edition|Bundle|Lara Croft|Onimusha:)\b', '', display_name)
        display_name = display_name.replace(":", "").strip()

        if len(display_name) < 3 or search_term.lower() not in display_name.lower():
            display_name = search_term

        raw_ov = game.get('overview', '')
        desc = "Gerado por PS2 AIO Tools."
        if raw_ov:
            try:
                translated = GoogleTranslator(source='auto', target='pt').translate(raw_ov[:1000])
                clean_text = re.sub(r'[\r\n\t]+', ' ', translated)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                desc = (clean_text[:252].rstrip() + "...") if len(clean_text) > 255 else clean_text
            except: desc = raw_ov[:252] + "..."

        date_fmt = "Desconhecido"
        if game.get('release_date'):
            try: date_fmt = datetime.strptime(game['release_date'].split(' ')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
            except: date_fmt = game['release_date']

        dev_ids = game.get('developers') or []
        developer = "Desconhecido"
        if dev_ids and len(dev_ids) > 0:
            dev_id = str(dev_ids[0])
            developer = include_data.get('developers', {}).get(dev_id, {}).get('name') or self.dev_map.get(dev_id, "Desconhecido")
        
        genre_ids = game.get('genres') or []
        genre_list = []
        genre_trans = {
            "Action": "Ação", "Shooter": "Tiro", "Horror": "Terror", "Adventure": "Aventura", "Family": "Família", "Role-Playing": "RPG",
            "Fighting": "Luta", "Puzzle": "Quebra-Cabeça", "Stealth": "Camuflagem", "Music": "Música", "Platform": "Plataforma", "Strategy": "Estratégia"
        }
        for g_id in genre_ids:
            g_name = include_data.get('genres', {}).get(str(g_id), {}).get('name') or self.genre_map.get(str(g_id))
            if g_name: genre_list.append(genre_trans.get(g_name, g_name))

        processed = {
            "name": display_name,
            "summary": desc,
            "release_date": date_fmt,
            "rating": "5",
            "players": str(game.get('players', '1')),
            "developer": developer,
            "genre": " / ".join(genre_list) if genre_list else "Outros"
        }
        
        self.cache.save_game(game_id if game_id else game_name, processed)
        return processed