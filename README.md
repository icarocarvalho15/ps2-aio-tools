# PS2 AIO Tools - DravDev 🎮

Uma ferramenta robusta e automatizada para organização de bibliotecas de jogos de PlayStation 2 e PlayStation 1 (POPS) para uso no Open PS2 Loader (OPL).

## ✨ Funcionalidades Atuais (Backend)

- **Scanner Inteligente**: Identifica automaticamente jogos em pastas OPL (`DVD`, `CD`, `POPS`, `APPS`).
- **Extração de Game ID**: Lê o serial oficial (Ex: `SLUS_212.03`) diretamente de dentro dos arquivos `.iso` de PS2.
- **Suporte Multi-disco**: Detecta e organiza jogos de PS1/PS2 compostos por múltiplos discos (Disc 1, 2, etc.).
- **Sanitização de Nomes**: Remove tags indesejadas (ISO, BR, PT-BR, Region) e padroniza o título dos jogos.
- **Integração IGDB API**: Busca metadados oficiais (Descrição, Lançamento, Gênero, Desenvolvedora).
- **Tradução Automática**: Converte descrições e gêneros do Inglês para o Português via Google Translator.
- **Gerenciador de CFG**: Gera arquivos de configuração padronizados, incluindo tamanhos de arquivos e contagem de jogadores.
- **Padrão POPStarter**: Lógica específica para PS1, focando nos arquivos `.VCD` mas gerando CFGs para os executáveis `XX.Nome.ELF`.

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **PyCdlib**: Para manipulação de sistemas de arquivos ISO.
- **Requests**: Integração com a API IGDB (Twitch OAuth2).
- **Deep Translator**: Tradução dinâmica de conteúdos.
- **Python-dotenv**: Gerenciamento de variáveis de ambiente.

---

## 🚀 Como Clonar e Configurar

Siga os passos abaixo para rodar o projeto em seu ambiente local:

### 1. Clonar o Repositório
Abra o seu terminal (ou Git Bash) e execute:
```bash
git clone [https://github.com/icarocarvalho15/ps2-aio-tools.git](https://github.com/icarocarvalho15/ps2-aio-tools.git)
cd ps2-aio-tools
```

### 2. Clonar o Repositório
Criar e Ativar o Ambiente Virtual (VENV):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar Dependências
Criar e Ativar o Ambiente Virtual (VENV):
```bash
pip install requests python-dotenv deep-translator pycdlib
```
Ou
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto e adicione suas credenciais da API IGDB:
```bash
IGDB_CLIENT_ID=seu_client_id_aqui
IGDB_CLIENT_SECRET=seu_client_secret_aqui
```

### 5. Uso via Terminal
Para escanear e processar seu dispositivo USB (Ex: Unidade "D:\"):
```bash
python main.py --root "D:\" --full --keep-id
```

## 📂 Estrutura do Projeto
- **/core**: Módulos lógicos (Scanner, Metadata, Rename, CFG Manager).
- **main.py**: Ponto de entrada via CLI.
- **.env**: Configurações sensíveis (não versionar).
