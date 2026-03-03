import os
import re
import shutil
from pathlib import Path

class POPSManager:
    def __init__(self, root_path, logger):
        self.root = Path(root_path)
        self.pops_dir = self.root / "POPS"
        self.logger = logger
        self.base_elf = self.pops_dir / "POPSTARTER.ELF"
        self.base_vmc0 = self.pops_dir / "SLOT0.VMC"
        self.base_vmc1 = self.pops_dir / "SLOT1.VMC"
        self.base_patch9 = self.pops_dir / "PATCH_9.BIN"

        self.default_cheats = [
            "$COMPATIBILITY_0x01",
            "$COMPATIBILITY_0x04",
            "$COMPATIBILITY_0x06",
            "$SUBCDSTATUS",
            "$SMOOTH",
            "$HDTVFIX"
        ]

    def create_global_cheats(self):
        """Cria o CHEATS.TXT global e garante os patches na raiz POPS."""
        global_cheat = self.pops_dir / "CHEATS.TXT"
        if not global_cheat.exists():
            with open(global_cheat, "w", encoding="utf-8") as f:
                f.write("// Códigos padrão POPStarter\n")
                f.write("\n".join(self.default_cheats))
            self.logger.info("CHEATS.TXT global criado com códigos padrão.")

    def setup_game(self, item, all_items):
        if item['type'] != "PS1": return
        vcd_path = Path(item['full_path'])
        original_stem = vcd_path.stem 
        game_name_clean = re.sub(r'\b(Disc|CD|Disk|Disco)\s*[1-4]\b', '', original_stem, flags=re.IGNORECASE).strip()
        self._create_launcher(original_stem)
        game_folder = self.pops_dir / original_stem
        game_folder.mkdir(parents=True, exist_ok=True)
        self._copy_patches_to_folder(game_folder)
        self._setup_vmcs(game_folder)
        self._create_game_cheats(game_folder)
        if item.get('disc_suffix'):
            self._handle_multi_disc(game_name_clean, game_folder, all_items)

    def _create_launcher(self, game_name):
        target_elf = self.pops_dir / f"XX.{game_name}.ELF"
        if self.base_elf.exists() and not target_elf.exists():
            shutil.copy2(self.base_elf, target_elf)
            self.logger.ok(f"Executável criado: {target_elf.name}")

    def _setup_vmcs(self, game_folder):
        """Copia os arquivos VMC funcionais da raiz /POPS para a pasta do jogo."""
        vmc_pairs = [
            (self.base_vmc0, "SLOT0.VMC"), 
            (self.base_vmc1, "SLOT1.VMC")
        ]
        any_copied = False
        for base_path, target_name in vmc_pairs:
            target_path = game_folder / target_name
            if target_path.exists():
                self.logger.skip(f"VMC preservado (já existe): {target_name} em {game_folder.name}")
                continue
            if base_path.exists():
                try:
                    shutil.copy2(base_path, target_path)
                    any_copied = True
                except Exception as e:
                    self.logger.error(f"Erro ao copiar VMC {target_name}: {e}")
            else:
                self.logger.error(f"ERRO: Matriz {target_name} NÃO ENCONTRADA na raiz /POPS!")
                self.logger.warn("Certifique-se de que os arquivos SLOT0.VMC e SLOT1.VMC funcionais estão na pasta POPS.")
        if any_copied:
            self.logger.ok(f"Memory Cards funcionais aplicados em: {game_folder.name}")

    def _copy_patches_to_folder(self, game_folder):
        """Copia os patches ou avisa se as matrizes sumiram da raiz."""
        patches_base = [(self.base_patch9, "PATCH_9.BIN")]
        any_patch_copied = False
        for base_path, patch_name in patches_base:
            target = game_folder / patch_name
            if target.exists():
                self.logger.skip(f"Patch preservado: {patch_name} em {game_folder.name}")
                continue
            if base_path.exists():
                shutil.copy2(base_path, target)
                any_patch_copied = True
            else:
                self.logger.warn(f"Patch base {patch_name} não encontrado na raiz /POPS.")
        if any_patch_copied:
            self.logger.ok(f"Patches aplicados em: {game_folder.name}")

    def _create_game_cheats(self, game_folder):
        """Cria o CHEATS.TXT ou avisa se houver erro."""
        cheat_file = game_folder / "CHEATS.TXT"
        if cheat_file.exists():
            self.logger.skip(f"CHEATS.TXT já existente em: {game_folder.name}")
            return
        try:
            with open(cheat_file, "w", encoding="utf-8") as f:
                f.write("// Códigos padrão POPStarter\n")
                f.write("\n".join(self.default_cheats))
            self.logger.info(f"CHEATS.TXT criado em: {game_folder.name}")
        except Exception as e:
            self.logger.error(f"Não foi possível criar CHEATS.TXT em {game_folder.name}: {e}")

    def _handle_multi_disc(self, game_name_clean, game_folder, all_items):
        discs_vcds = []
        disc_folders = []
        for i in all_items:
            if i['type'] == "PS1":
                item_stem = Path(i['file_name']).stem
                current_clean = re.sub(r'\b(Disc|CD|Disk|Disco)\s*[1-4]\b', '', item_stem, flags=re.IGNORECASE).strip()
                if current_clean == game_name_clean:
                    discs_vcds.append(i['file_name'])
                    disc_folders.append(item_stem)
        if len(discs_vcds) > 1:
            discs_vcds.sort()
            disc_folders.sort()
            with open(game_folder / "DISCS.TXT", "w", encoding="utf-8") as f:
                f.write("\n".join(discs_vcds))
            with open(game_folder / "VMCDIR.TXT", "w", encoding="utf-8") as f:
                f.write(disc_folders[0])
            self.logger.info(f"Configuração Multi-disco aplicada em: {game_folder.name}")

    def update_apps_config(self, all_items):
        """Atualização do arquivo conf_apps.cfg na raiz do USB. Mantém o que já existe e adiciona os novos jogos de PS1."""
        apps_cfg_path = self.root / "conf_apps.cfg"
        existing_content = {}
        if apps_cfg_path.exists():
            try:
                with open(apps_cfg_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line:
                            name, path = line.strip().split("=", 1)
                            existing_content[name] = path
            except Exception as e:
                self.logger.error(f"Erro ao ler conf_apps.cfg: {e}")
        new_entries_count = 0
        for item in all_items:
            if item['type'] == "PS1":
                game_name = Path(item['full_path']).stem
                entry_name = game_name
                entry_path = f"mass:/POPS/XX.{game_name}.ELF"
                if entry_name not in existing_content:
                    existing_content[entry_name] = entry_path
                    new_entries_count += 1
        if new_entries_count > 0:
            try:
                sorted_names = sorted(existing_content.keys())
                with open(apps_cfg_path, "w", encoding="utf-8") as f:
                    for name in sorted_names:
                        f.write(f"{name}={existing_content[name]}\n")
                self.logger.ok(f"conf_apps.cfg atualizado! {new_entries_count} novos jogos adicionados.")
            except Exception as e:
                self.logger.error(f"Erro ao salvar conf_apps.cfg: {e}")
        else:
            self.logger.info("Nenhum novo jogo de PS1 para adicionar ao conf_apps.cfg.")