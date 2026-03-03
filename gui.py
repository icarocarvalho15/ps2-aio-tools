import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
from main import main_logic 

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PS2 AIO Tools - DravDev 🎮")
        self.geometry("700x500")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="PS2 AIO\nTools", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.rename_var = ctk.BooleanVar(value=True)
        self.checkbox_rename = ctk.CTkCheckBox(self.sidebar, text="Renomear Jogos", variable=self.rename_var)
        self.checkbox_rename.grid(row=1, column=0, pady=10, padx=20, sticky="w")

        self.pops_var = ctk.BooleanVar(value=True)
        self.checkbox_pops = ctk.CTkCheckBox(self.sidebar, text="Setup POPS (PS1)", variable=self.pops_var)
        self.checkbox_pops.grid(row=2, column=0, pady=10, padx=20, sticky="w")

        self.meta_var = ctk.BooleanVar(value=True)
        self.checkbox_meta = ctk.CTkCheckBox(self.sidebar, text="Baixar Metadata", variable=self.meta_var)
        self.checkbox_meta.grid(row=3, column=0, pady=10, padx=20, sticky="w")

        self.keep_id_var = ctk.BooleanVar(value=True)
        self.checkbox_id = ctk.CTkCheckBox(self.sidebar, text="Manter Game ID", variable=self.keep_id_var)
        self.checkbox_id.grid(row=4, column=0, pady=10, padx=20, sticky="w")

        self.start_button = ctk.CTkButton(self.sidebar, text="INICIAR PROCESSO", command=self.start_thread, fg_color="green", hover_color="#006400")
        self.start_button.grid(row=5, column=0, padx=20, pady=20)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.label_root = ctk.CTkLabel(self.main_frame, text="Raiz do USB/HDD (Ex: F:\\):")
        self.label_root.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.entry_root = ctk.CTkEntry(self.main_frame, placeholder_text="Selecione a unidade...")
        self.entry_root.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_browse = ctk.CTkButton(self.main_frame, text="Procurar", width=100, command=self.browse_root)
        self.btn_browse.grid(row=1, column=1, padx=(0, 20))

        self.label_filter = ctk.CTkLabel(self.main_frame, text="Filtro de busca (Opcional):")
        self.label_filter.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.entry_filter = ctk.CTkEntry(self.main_frame, placeholder_text="Ex: Resident Evil 4...")
        self.entry_filter.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.textbox = ctk.CTkTextbox(self.main_frame, width=400, height=250)
        self.textbox.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        self.textbox.tag_config("ok", foreground="#2ecc71")
        self.textbox.tag_config("info", foreground="#3498db")
        self.textbox.tag_config("warn", foreground="#f1c40f")
        self.textbox.tag_config("error", foreground="#e74c3c")
        self.textbox.tag_config("skip", foreground="#95a5a6")
        self.textbox.tag_config("start", foreground="#9b59b6")

        self.textbox.insert("0.0", "Aguardando início...\n")
        self.textbox.configure(state="disabled")

    def browse_root(self):
        directory = filedialog.askdirectory()
        if directory:
            self.entry_root.delete(0, "end")
            self.entry_root.insert(0, str(Path(directory)))

    def update_log(self, text):
        self.textbox.configure(state="normal")
        tag = None
        if "[OK]" in text: tag = "ok"
        elif "[INFO]" in text: tag = "info"
        elif "[WARN]" in text: tag = "warn"
        elif "[ERROR]" in text or "[ERRO]" in text: tag = "error"
        elif "[SKIP]" in text: tag = "skip"
        elif "[INICIANDO]" in text: tag = "start"
        self.textbox.insert("end", text, tag)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def start_thread(self):
        threading.Thread(target=self.run_automation, daemon=True).start()

    def run_automation(self):
        root = self.entry_root.get()
        filter_val = self.entry_filter.get() if self.entry_filter.get() else None

        if not root:
            messagebox.showerror("Erro", "Selecione a unidade root!")
            return

        self.start_button.configure(state="disabled")
        self.update_log(f"\n[INICIANDO] Processando unidade: {root}\n")

        class FakeArgs:
            def __init__(self, root, rename, pops, metadata, keep_id, filter_text):
                self.root = root
                self.rename = rename
                self.pops = pops
                self.metadata = metadata
                self.keep_id = keep_id
                self.full = False
                self.scan_only = False
                self.filter = filter_text

        args = FakeArgs(root, 
                        self.rename_var.get(), 
                        self.pops_var.get(), 
                        self.meta_var.get(), 
                        self.keep_id_var.get(),
                        filter_val)

        try:
            main_logic(args, gui_callback=self.update_log)
        except Exception as e:
            self.update_log(f"\n[ERRO CRÍTICO] {str(e)}\n")
        finally:
            self.start_button.configure(state="normal")
            self.update_log("\n[FIM] Processo finalizado!")

if __name__ == "__main__":
    app = App()
    app.mainloop()