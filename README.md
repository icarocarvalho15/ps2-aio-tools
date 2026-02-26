# PS2 AIO Tools - DravDev 🎮

Uma ferramenta robusta e automatizada para organização de bibliotecas de jogos de PlayStation 2 e PlayStation 1 (POPS) para uso no Open PS2 Loader (OPL).

## ✨ Funcionalidades Atuais (Backend)

- **Scanner Inteligente**: Identifica automaticamente jogos em pastas OPL (`DVD`, `CD`, `POPS`, `APPS`) e extrai Game IDs (seriais) de arquivos de PS2.
- **Sanitização Profunda (Rename)**: Limpeza automática de nomes de arquivos, removendo tags de região (USA, Europe), versões, revisões e lixos de cena (`[Hacked]`, `[v1.0]`, etc.).
- **Padrão POPStarter Pro**: 
    - Criação automática de executáveis `XX.Nome do Jogo.ELF`.
    - Setup de pastas de suporte com cópia de **VMCs**, **Patches** de compatibilidade e **Cheats**.
    - Suporte avançado a **Multi-disco**: Geração automática de `DISCS.TXT` e `VMCDIR.TXT` para compartilhamento de saves entre discos.
    - Atualização dinâmica do `conf_apps.cfg` para listar jogos de PS1 na aba Apps do OPL.
- **Integração IGDB API**: Busca metadados oficiais (Descrição, Lançamento, Gênero, Desenvolvedora).
- **Tradução Automática**: Converte descrições e gêneros para o Português via Google Translator.
- **Sistema de Cache Local**: Armazena metadados em JSON para economizar cota de API e acelerar execuções futuras.
- **Logger com Histórico**: Todas as operações são exibidas no terminal e salvas em `session_history.log`.

## 🛠️ Tecnologias Utilizadas

- **Python 3.12+**
- **PyCdlib**: Manipulação de sistemas de arquivos ISO.
- **Requests**: Integração com a API IGDB (Twitch OAuth2).
- **Deep Translator**: Tradução dinâmica de conteúdos.
- **Python-dotenv**: Gerenciamento de variáveis de ambiente.

---

## 🚀 Como Clonar e Configurar

### 1. Clonar o Repositório
```bash
git clone [https://github.com/icarocarvalho15/ps2-aio-tools.git](https://github.com/icarocarvalho15/ps2-aio-tools.git)
cd ps2-aio-tools
```

### 2. Clonar o Repositório
Criar e Ativar o Ambiente Virtual (VENV):
```bash
python -m venv venv
# No Windows:
.\venv\Scripts\Activate.ps1
# No Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
Instale as dependências necessárias via pip:
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto e adicione suas credenciais da API IGDB:
```bash
IGDB_CLIENT_ID=seu_client_id_aqui
IGDB_CLIENT_SECRET=seu_client_secret_aqui
```

### 5. Uso via Terminal (CLI)
A ferramenta é modular. Você pode rodar o fluxo completo ou apenas tarefas específicas:
Parâmetro,Função
"--root ""X:\""",Define a letra da unidade do USB/HD (Obrigatório).
--scan-only,"Apenas lista os jogos encontrados, sem fazer alterações."
--rename,Renomeia os arquivos para nomes limpos e padronizados.
--pops,"Executa o setup completo de PS1 (VMCs, Patches, Apps Config)."
--metadata,Busca informações na API e gera os arquivos .cfg.
--full,Executa Rename + POPS + Metadata de uma só vez.
--keep-id,Mantém o Game ID no nome do arquivo (Ex: SLUS_212.03.Game.iso).

Exemplo de uso completo:
```bash
python main.py --root "D:\" --full --keep-id
```

## 📂 Estrutura do Projeto
- **/core**: Módulos lógicos (Scanner, Rename, Metadata, Cache, PopsManager, Logger).
- **metadata_cache.json**: Banco de dados local para buscas rápidas.
- **session_history.log**: Log detalhado de erros e sucessos.
- **main.py**: Ponto de entrada via CLI.

Desenvolvido por DravDev (Ícaro Carvalho)