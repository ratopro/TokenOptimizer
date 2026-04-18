import customtkinter as ctk
from core.ai_engine import OllamaEngine
from core.window_manager import WindowManager
from core.automation import AutomationController
from utils.config import ConfigManager
import threading
import re
import platform

import webbrowser

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CURRENT_VERSION = "1.1.0"
GITHUB_URL = "https://github.com/ratopro/TokenOptimizer"

LOCALES = {
    "EN": {
        "model": "Model:", "target": "Target:", "no_apps": "No apps", "loading": "Loading...",
        "source": "Source Prompt", "optimize": "Optimize", "savings": "Savings:",
        "output": "Optimized Output", "copy": "Copy", "inject": "Inject", "preview": "Preview",
        "translate": "Translate", "lang": "Language:", "method": "Method:", "ready": "Ready",
        "booting": "Booting...", "shrinking": "Shrinking...", "injecting": "Injecting...",
        "history": "Prompt History", "empty": "History Empty", "notes": "Release Notes",
        "new": "What's New?", "github": "GitHub", "missing": "Missing:", "run": "Run:",
        "new_ver": "New version available: v{v}!"
    },
    "ES": {
        "model": "Modelo:", "target": "Destino:", "no_apps": "Sin apps", "loading": "Cargando...",
        "source": "Prompt Original", "optimize": "Optimizar", "savings": "Ahorro:",
        "output": "Resultado Optimizado", "copy": "Copiar", "inject": "Inyectar", "preview": "Vista Previa",
        "translate": "Traducir", "lang": "Idioma:", "method": "Método:", "ready": "Listo",
        "booting": "Iniciando...", "shrinking": "Optimizando...", "injecting": "Inyectando...",
        "history": "Historial", "empty": "Historial vacío", "notes": "Notas de versión",
        "new": "¿Qué hay de nuevo?", "github": "GitHub", "missing": "Faltan:", "run": "Ejecuta:",
        "new_ver": "¡Nueva versión disponible: v{v}!"
    },
    "FR": {
        "model": "Modèle:", "target": "Cible:", "no_apps": "Aucune app", "loading": "Chargement...",
        "source": "Prompt Source", "optimize": "Optimiser", "savings": "Économie:",
        "output": "Résultat Optimisé", "copy": "Copier", "inject": "Injecter", "preview": "Aperçu",
        "translate": "Traduire", "lang": "Langue:", "method": "Méthode:", "ready": "Prêt",
        "booting": "Démarrage...", "shrinking": "Optimisation...", "injecting": "Injection...",
        "history": "Historique", "empty": "Historique vide", "notes": "Notes de version",
        "new": "Quoi de neuf?", "github": "GitHub", "missing": "Manquant:", "run": "Exécuter:",
        "new_ver": "Nouvelle version: v{v}!"
    },
    "DE": {
        "model": "Modell:", "target": "Ziel:", "no_apps": "Keine Apps", "loading": "Laden...",
        "source": "Quelltext", "optimize": "Optimieren", "savings": "Ersparnis:",
        "output": "Optimierte Ausgabe", "copy": "Kopieren", "inject": "Einfügen", "preview": "Vorschau",
        "translate": "Übersetzen", "lang": "Sprache:", "method": "Methode:", "ready": "Bereit",
        "booting": "Starten...", "shrinking": "Optimierung...", "injecting": "Einfügen...",
        "history": "Verlauf", "empty": "Verlauf leer", "notes": "Versionshinweise",
        "new": "Was ist neu?", "github": "GitHub", "missing": "Fehlt:", "run": "Ausführen:",
        "new_ver": "Neue Version: v{v}!"
    },
    "IT": {
        "model": "Modello:", "target": "Destinazione:", "no_apps": "Nessuna app", "loading": "Caricamento...",
        "source": "Prompt Originale", "optimize": "Ottimizza", "savings": "Risparmio:",
        "output": "Risultato Ottimizzato", "copy": "Copia", "inject": "Iniettare", "preview": "Anteprima",
        "translate": "Traduci", "lang": "Lingua:", "method": "Metodo:", "ready": "Pronto",
        "booting": "Avvio...", "shrinking": "Ottimizzazione...", "injecting": "Iniezione...",
        "history": "Cronologia", "empty": "Cronologia vuota", "notes": "Note di rilascio",
        "new": "Novità?", "github": "GitHub", "missing": "Mancante:", "run": "Esegui:",
        "new_ver": "Nuova versione: v{v}!"
    },
    "PT": {
        "model": "Modelo:", "target": "Destino:", "no_apps": "Sem apps", "loading": "Carregando...",
        "source": "Prompt Original", "optimize": "Otimizar", "savings": "Economia:",
        "output": "Resultado Otimizado", "copy": "Copiar", "inject": "Injetar", "preview": "Visualizar",
        "translate": "Traduzir", "lang": "Idioma:", "method": "Método:", "ready": "Pronto",
        "booting": "Iniciando...", "shrinking": "Otimizando...", "injecting": "Injetando...",
        "history": "Histórico", "empty": "Histórico vazio", "notes": "Notas de versão",
        "new": "O que há de novo?", "github": "GitHub", "missing": "Faltando:", "run": "Executar:",
        "new_ver": "Nova versão: v{v}!"
    }
}

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self._show)
        self.widget.bind("<Leave>", self._hide)
    
    def _show(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(self.tooltip, text=self.text, fg_color="#333333", corner_radius=4)
        label.pack(padx=5, pady=3)
    
    def _hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class TokenShrinkApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Token Optimizer")
        self.config = ConfigManager()
        
        # Dimensiones persistentes
        ancho = self.config.get("ancho", 620)
        alto = self.config.get("alto", 460)
        self.geometry(f"{ancho}x{alto}")

        self.ai_engine = OllamaEngine()
        self.window_manager = WindowManager()
        self.automation = AutomationController()

        self.modelos = []
        self.ventanas = []
        self.resultado_actual = ""
        self._ultimo_prompt = ""
        self._historial_prompts = [] # <--- Lista para el historial
        self._historial_idx = -1     # <--- Índice de navegación
        self._draft_prompt = ""      # <--- Para guardar lo que el usuario estaba escribiendo
        self._widgets_uniformes = [] # <--- Registro de todos los widgets para fuente global
        self._siempre_visible = False
        self._tamano_texto = self.config.get("tamano_texto", 10)
        self._historial_window = None # <--- Referencia para instancia única
        self._changelog_content = ""  # <--- Almacén para el changelog

        self._crear_interfaz()
        self.protocol("WM_DELETE_WINDOW", self._guardar_configuracion)
        self.after(100, self._cargar_datos_iniciales)
        self.after(500, self._verificar_dependencias)
        self.after(2000, lambda: threading.Thread(target=self._comprobar_actualizaciones, daemon=True).start())

    def _verificar_dependencias(self):
        if platform.system() == "Linux":
            import subprocess
            missing = []
            for tool in ["xdotool", "xclip"]:
                if subprocess.run(["which", tool], capture_output=True).returncode != 0:
                    missing.append(tool)
            
            if missing:
                pkgs = " ".join(missing)
                cmd = f"sudo apt install {pkgs}"
                t = LOCALES.get(self.config.get("idioma", "EN"), LOCALES["EN"])
                msg = f"{t['missing']} {pkgs} | {t['run']} {cmd}"
                self.label_st.configure(text=msg, text_color="#e74c3c")
                print(f"\n[!] MISSING DEPENDENCIES DETECTED:")
                print(f"Packages: {pkgs}")
                print(f"Command: {cmd}\n")

    def _localizar_interfaz(self):
        ln = self.combo_lang.get()
        # Fallback a EN si no existe traducción
        t = LOCALES.get(ln, LOCALES["EN"])
        
        self.lbl_model.configure(text=t["model"])
        self.lbl_target.configure(text=t["target"])
        self.lbl_source.configure(text=t["source"])
        self.lbl_output.configure(text=t["output"])
        self.btn_opt.configure(text=t["optimize"])
        self.btn_copy.configure(text=t["copy"])
        self.btn_inject.configure(text=t["inject"])
        self.sw_show.configure(text=t["preview"])
        self.sw_es.configure(text=t["translate"])
        self.lbl_lang.configure(text=t["lang"])
        self.lbl_method.configure(text=t["method"])
        
        if hasattr(self, "label_st") and self.label_st.cget("text") in ["Ready", "Listo", "Prêt", "Bereit", "Pronto"]:
            self.label_st.configure(text=t["ready"])

        # Actualizar placeholders si están activos
        if self.combo_modelos.get() in ["Loading...", "Cargando...", "Chargement...", "Laden..."]:
            self.combo_modelos.set(t["loading"])
        if self.combo_ventanas.get() in ["No apps", "Sin apps", "Aucune app", "Keine Apps"]:
            self.combo_ventanas.set(t["no_apps"])

    def _comprobar_actualizaciones(self):
        try:
            import requests
            repo = "ratopro/TokenOptimizer"
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest = data.get("tag_name", "").replace("v", "")
                if latest and latest != CURRENT_VERSION:
                    self._changelog_content = data.get("body", "No details available.")
                    t = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])
                    msg = t["new_ver"].format(v=latest)
                    self.label_st.configure(text=msg, text_color="orange")
                    self.label_ver.configure(text_color="orange", text=f"v{CURRENT_VERSION} ({t['new']})")
                    print(f"[Update] New version available on GitHub: v{latest}")
        except:
            pass # Silencioso si no hay red o falla API

    def _mostrar_changelog(self):
        if not self._changelog_content:
            webbrowser.open(GITHUB_URL)
            return

        win = ctk.CTkToplevel(self)
        t = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])
        win.title(t["new"])
        win.geometry("500x400")
        win.attributes("-topmost", True)

        lbl = ctk.CTkLabel(win, text=t["notes"], font=("Roboto", 16, "bold"))
        lbl.pack(pady=10)

        txt = ctk.CTkTextbox(win, wrap="word")
        txt.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        txt.insert("1.0", self._changelog_content)
        txt.configure(state="disabled") # Solo lectura

        btn = ctk.CTkButton(win, text=t["github"], command=lambda: webbrowser.open(GITHUB_URL))
        btn.pack(pady=(0, 15))

    def _reg(self, w):
        self._widgets_uniformes.append(w)
        return w

    def _crear_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Barra Superior
        frame_top = ctk.CTkFrame(self)
        frame_top.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        frame_top.grid_columnconfigure(1, weight=1) 
        frame_top.grid_columnconfigure(3, weight=1) 

        self.lbl_model = self._reg(ctk.CTkLabel(frame_top, text="Model:"))
        self.lbl_model.grid(row=0, column=0, padx=2)
        self.combo_modelos = self._reg(ctk.CTkComboBox(frame_top, values=["Loading..."], state="readonly", 
                                                      command=self._on_modelo_change, height=24, 
                                                      width=300)) 
        self.combo_modelos.grid(row=0, column=1, padx=2, sticky="ew")

        self.lbl_target = self._reg(ctk.CTkLabel(frame_top, text="Target:"))
        self.lbl_target.grid(row=0, column=2, padx=2)
        self.combo_ventanas = self._reg(ctk.CTkComboBox(frame_top, values=["No apps"], state="readonly", 
                                                       command=self._on_ventana_change, height=24, 
                                                       width=300)) 
        self.combo_ventanas.grid(row=0, column=3, padx=2, sticky="ew")
        
        frame_btns = ctk.CTkFrame(frame_top, fg_color="transparent")
        frame_btns.grid(row=0, column=4, padx=2)
        self._reg(ctk.CTkButton(frame_btns, text="↻", width=24, height=24, command=self._actualizar_listas)).pack(side="left", padx=1)
        self._reg(ctk.CTkButton(frame_btns, text="🗑️", width=24, height=24, command=self._limpiar)).pack(side="left", padx=1)
        self.btn_pin = self._reg(ctk.CTkButton(frame_btns, text="📌", width=24, height=24, command=self._toggle_siempre_visible))
        self.btn_pin.pack(side="left", padx=1)

        # Entrada (Ocupa peso vertical)
        frame_in = ctk.CTkFrame(self)
        frame_in.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        
        f_in_label = ctk.CTkFrame(frame_in, fg_color="transparent")
        f_in_label.pack(fill="x", pady=1)
        self.lbl_source = self._reg(ctk.CTkLabel(f_in_label, text="Source Prompt"))
        self.lbl_source.pack(side="left", padx=5)
        self._reg(ctk.CTkButton(f_in_label, text="📜", width=24, height=20, command=self._abrir_historial)).pack(side="right", padx=2)
        
        # Controles inferiores primero para que no desaparezcan
        self.btn_opt = self._reg(ctk.CTkButton(frame_in, text="Optimize", height=24, command=self._ejecutar))
        self.btn_opt.pack(side="bottom", pady=2)
        self.label_comp = self._reg(ctk.CTkLabel(frame_in, text="Savings: -", text_color="gray"))
        self.label_comp.pack(side="bottom", pady=0)

        self.text_entrada = ctk.CTkTextbox(frame_in) 
        self.text_entrada.pack(fill="both", expand=True, padx=2, pady=1)
        self.text_entrada.bind("<KeyRelease>", self._update_in_count)
        
        # Bindings restaurados
        self.text_entrada.bind("<Return>", lambda e: (self._ejecutar(), "break")[1])
        self.text_entrada.bind("<KP_Enter>", lambda e: (self._ejecutar(), "break")[1])
        self.text_entrada.bind("<Control-Return>", lambda e: self.text_entrada.insert("insert", "\n"))
        self.text_entrada.bind("<Control-KP_Enter>", lambda e: self.text_entrada.insert("insert", "\n"))
        self.text_entrada.bind("<Control-Up>", self._historial_anterior)
        self.text_entrada.bind("<Control-Down>", self._historial_siguiente)
        
        # Salida (Ocupa peso vertical)
        frame_out = ctk.CTkFrame(self)
        frame_out.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)
        self.frame_out = frame_out
        self.lbl_output = self._reg(ctk.CTkLabel(frame_out, text="Optimized Output"))
        self.lbl_output.pack(pady=1)
        
        # Botones primero en el fondo para que no desaparezcan
        f_btns_out = ctk.CTkFrame(frame_out, fg_color="transparent")
        f_btns_out.pack(side="bottom", pady=2)
        self.btn_copy = self._reg(ctk.CTkButton(f_btns_out, text="Copy", width=60, height=22, command=self._copiar))
        self.btn_copy.pack(side="left", padx=2)
        self.btn_inject = self._reg(ctk.CTkButton(f_btns_out, text="Inject", width=60, height=22, command=self._enviar))
        self.btn_inject.pack(side="left", padx=2)

        self.text_salida = ctk.CTkTextbox(frame_out) 
        self.text_salida.pack(fill="both", expand=True, padx=2, pady=1)

        # Footer
        frame_foot = ctk.CTkFrame(self)
        frame_foot.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
        
        self.sw_show = self._reg(ctk.CTkSwitch(frame_foot, text="Preview", height=18, width=36, command=self._toggle_mostrar))
        self.sw_show.select()
        self.sw_show.pack(side="left", padx=5)

        self.sw_es = self._reg(ctk.CTkSwitch(frame_foot, text="Translate", height=18, width=36, command=self._toggle_idioma))
        self.sw_es.select()
        self.sw_es.pack(side="left", padx=5)
 
        self.lbl_lang = self._reg(ctk.CTkLabel(frame_foot, text="Language:"))
        self.lbl_lang.pack(side="left", padx=(10, 2))
        self.combo_lang = self._reg(ctk.CTkComboBox(frame_foot, values=["EN", "ES", "FR", "DE", "IT", "PT", "ZH", "JA", "RU"], 
                                                   state="readonly", height=22, width=80, command=self._on_lang_change)) 
        self.combo_lang.pack(side="left", padx=2)
        self.combo_lang.set(self.config.get("idioma", "EN"))

        self.lbl_method = self._reg(ctk.CTkLabel(frame_foot, text="Method:"))
        self.lbl_method.pack(side="left", padx=(10, 2))
        self.combo_modo = self._reg(ctk.CTkComboBox(frame_foot, values=["Light", "Optimized", "Aggressive", "Symbolic"], 
                                                   state="readonly", height=22, width=125, command=self._on_modo_change)) 
        self.combo_modo.pack(side="left", padx=5)
        self.combo_modo.set(self.config.get("modo", "Optimized"))
        
        # Contadores de Tokens
        f_stats = ctk.CTkFrame(frame_foot, fg_color="transparent")
        f_stats.pack(side="right", padx=10)
        self.lbl_t_in = self._reg(ctk.CTkLabel(f_stats, text="In: 0", text_color="cyan", font=("Roboto", self._tamano_texto, "bold")))
        self.lbl_t_in.pack(side="left", padx=5)
        self.lbl_t_out = self._reg(ctk.CTkLabel(f_stats, text="Out: 0", text_color="green", font=("Roboto", self._tamano_texto, "bold")))
        self.lbl_t_out.pack(side="left", padx=5)

        self.label_st = self._reg(ctk.CTkLabel(self, text="Ready", text_color="gray"))
        self.label_st.grid(row=4, column=0, sticky="w", padx=5)

        self.label_ver = self._reg(ctk.CTkLabel(self, text=f"v{CURRENT_VERSION}", text_color="gray", cursor="hand2"))
        self.label_ver.grid(row=4, column=0, sticky="e", padx=5)
        self.label_ver.bind("<Button-1>", lambda e: self._mostrar_changelog())

        # Bindings de Zoom
        self.bind_all("<Control-plus>", self._aumentar_texto)
        self.bind_all("<Control-KP_Add>", self._aumentar_texto)
        self.bind_all("<Control-equal>", self._aumentar_texto)
        self.bind_all("<Control-minus>", self._disminuir_texto)
        self.bind_all("<Control-KP_Subtract>", self._disminuir_texto)
        self.bind_all("<Control-underscore>", self._disminuir_texto)
        
        # Aplicar fuente inicial
        self._aplicar_fuente()
        
        # Aplicar localización final cuando todo el árbol de widgets existe
        self._localizar_interfaz()

    def _cargar_datos_iniciales(self):
        self.label_st.configure(text="Booting...", text_color="yellow")
        
        # Aplicar estados guardados
        if not self.config.get("mostrar_resultado", True): 
            self.sw_show.deselect()
            self.frame_out.grid_remove()
        
        if self.config.get("traducir_es", True): 
            self.sw_es.select()
        else:
            self.sw_es.deselect()
        
        self._cargar_modelos()
        self._actualizar_listas()
        self._localizar_interfaz()

    def _on_lang_change(self, v):
        self.config.set("idioma", v)
        self._localizar_interfaz()

    def _cargar_modelos(self):
        self.modelos = self.ai_engine.get_available_models()
        if self.modelos:
            self.combo_modelos.configure(values=self.modelos)
            saved = self.config.get("modelo")
            model = saved if saved in self.modelos else self.modelos[0]
            self.combo_modelos.set(model)
            self.ai_engine.set_model(model)

    def _actualizar_listas(self):
        self.ventanas = self.window_manager.get_active_windows()
        if self.ventanas:
            self.combo_ventanas.configure(values=self.ventanas)
            saved = self.config.get("ventana")
            self.combo_ventanas.set(saved if saved in self.ventanas else self.ventanas[0])

    def _on_modelo_change(self, m):
        self.ai_engine.set_model(m)
        self.config.set("modelo", m)

    def _on_ventana_change(self, v):
        self.config.set("ventana", v)

    def _on_modo_change(self, m):
        self.config.set("modo", m)

    def _toggle_idioma(self):
        self.config.set("traducir_es", self.sw_es.get())
        if hasattr(self, "res_es") and hasattr(self, "res_en"):
            res = self.res_es if self.sw_es.get() else self.res_en
            self.text_salida.delete("1.0", "end")
            self.text_salida.insert("1.0", res)

    def _ejecutar(self):
        p = self.text_entrada.get("1.0", "end").strip()
        if not p: return
        
        # Guardar en historial si es nuevo
        if not self._historial_prompts or self._historial_prompts[0]["prompt"] != p:
            from datetime import datetime
            ts = datetime.now().strftime("%H:%M")
            self._historial_prompts.insert(0, {"ts": ts, "prompt": p})
            if len(self._historial_prompts) > 50: self._historial_prompts.pop()
        
        self._historial_idx = -1 # Resetear navegación
        self._ultimo_prompt = p
        t = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])
        self.label_st.configure(text=t["shrinking"], text_color="yellow")
        
        # Si 'Translate' está activo, forzamos Inglés. Si no, usamos el idioma de la App.
        lang = "English" if self.sw_es.get() else self.combo_lang.get()
        self.ai_engine.optimize_prompt(p, self._on_complete, lang, self.combo_modo.get())

    def _on_complete(self, dual, stats):
        import re
        re_res = re.search(r"\[\[RES\]\](.*?)$", dual, re.DOTALL)
        res = re_res.group(1).strip() if re_res else dual
        self.text_salida.delete("1.0", "end")
        self.text_salida.insert("1.0", res)
        
        # Actualizar contadores
        self.lbl_t_in.configure(text=f"In: {stats['in']}")
        
        # Calcular tokens de salida reales del texto seleccionado (estimación precisa)
        out_tokens = len(res) // 4 if len(res) > 0 else 0
        self.lbl_t_out.configure(text=f"Out: {out_tokens}")

        if self._ultimo_prompt:
            # Compresión basada en tokens reales (estimados para ambos para consistencia)
            in_est = len(self._ultimo_prompt) // 4
            if in_est > 0:
                c = ((in_est - out_tokens) / in_est) * 100
            else:
                c = 0
            color = "#2ecc71" if c >= 0 else "#e74c3c"
            t = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])
            self.label_comp.configure(text=f"{t['savings']} {c:.1f}%", text_color=color)
        t = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])
        self.label_st.configure(text=t["ready"], text_color="green")
        if not self.sw_show.get(): self._enviar()

    def _copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_salida.get("1.0", "end").strip())

    def _enviar(self):
        t = self.text_salida.get("1.0", "end").strip()
        v = self.combo_ventanas.get()
        if t and v:
            msg = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])["injecting"]
            self.label_st.configure(text=msg, text_color="cyan")
            self.window_manager.focus_window_by_title(v)
            # Delay para asegurar foco antes de inyectar
            self.after(300, lambda: self.automation.inject_text(t))
            self.after(400, self._limpiar) # <--- Limpieza automática tras el envío

    def _toggle_mostrar(self):
        self.config.set("mostrar_resultado", self.sw_show.get())
        if self.sw_show.get(): self.frame_out.grid()
        else: self.frame_out.grid_remove()

    def _toggle_siempre_visible(self):
        self._siempre_visible = not self._siempre_visible
        self.attributes("-topmost", self._siempre_visible)
        self.btn_pin.configure(fg_color="blue" if self._siempre_visible else "gray")

    def _abrir_historial(self):
        t = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])
        if not self._historial_prompts:
            self.label_st.configure(text=t["empty"], text_color="orange")
            return

        # Si ya existe y es válida, traer al frente
        if self._historial_window is not None and self._historial_window.winfo_exists():
            self._historial_window.deiconify()
            self._historial_window.focus()
            return

        win = ctk.CTkToplevel(self)
        self._historial_window = win # <--- Guardar referencia
        t = LOCALES.get(self.combo_lang.get(), LOCALES["EN"])
        win.title(t["history"])
        
        # Dimensiones persistentes para el historial
        w_h = self.config.get("historial_ancho", 600)
        h_h = self.config.get("historial_alto", 400)
        win.geometry(f"{w_h}x{h_h}")
        win.attributes("-topmost", True)

        # Capturar dimensiones al cerrar el historial
        def on_close_hist():
            self.config.set("historial_ancho", win.winfo_width())
            self.config.set("historial_alto", win.winfo_height())
            self._historial_window = None # <--- Limpiar referencia
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close_hist)

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        def cargar(txt):
            self.text_entrada.delete("1.0", "end")
            self.text_entrada.insert("1.0", txt)
            self._historial_window = None # <--- Limpiar referencia
            win.destroy()

        for i, h in enumerate(self._historial_prompts):
            # Contenedor para cada entrada para permitir interactividad
            f_entry = ctk.CTkFrame(scroll, fg_color="transparent")
            f_entry.pack(fill="x", pady=1)
            
            # Sello de tiempo destacado
            lbl_ts = ctk.CTkLabel(f_entry, text=f"[{h['ts']}]", text_color="cyan", font=("Roboto", self._tamano_texto, "bold"))
            lbl_ts.pack(side="left", anchor="n", padx=(5, 2))
            
            # Prompt con ajuste de línea (wraplength dinámico basado en ancho de ventana)
            # Usamos un ancho fijo de referencia que se expandirá
            lbl_p = ctk.CTkLabel(f_entry, text=h['prompt'], anchor="w", justify="left",
                                 text_color="gray80", font=("Roboto", self._tamano_texto),
                                 wraplength=550) # Ajustado al ancho inicial de la ventana
            lbl_p.pack(fill="x", expand=True, padx=2, pady=2)
            
            # Hacer que toda la entrada sea clickable
            def cargar_y_cerrar(txt=h['prompt']): cargar(txt)
            f_entry.bind("<Button-1>", lambda e, t=h['prompt']: cargar_y_cerrar(t))
            lbl_p.bind("<Button-1>", lambda e, t=h['prompt']: cargar_y_cerrar(t))
            lbl_ts.bind("<Button-1>", lambda e, t=h['prompt']: cargar_y_cerrar(t))

            # Añadir divisor
            if i < len(self._historial_prompts) - 1:
                ctk.CTkFrame(scroll, height=1, fg_color="gray30").pack(fill="x", padx=10, pady=2)

    def _limpiar(self):
        self.text_entrada.delete("1.0", "end")
        self.text_salida.delete("1.0", "end")
        self.text_entrada.focus_set()

    def _historial_anterior(self, e=None):
        if not self._historial_prompts: return "break"
        
        # Guardar borrador si empezamos a navegar
        if self._historial_idx == -1:
            self._draft_prompt = self.text_entrada.get("1.0", "end").strip()
            
        if self._historial_idx < len(self._historial_prompts) - 1:
            self._historial_idx += 1
            self.text_entrada.delete("1.0", "end")
            self.text_entrada.insert("1.0", self._historial_prompts[self._historial_idx]["prompt"])
        return "break"

    def _historial_siguiente(self, e=None):
        if self._historial_idx == -1: return "break"
        
        self._historial_idx -= 1
        self.text_entrada.delete("1.0", "end")
        
        if self._historial_idx == -1:
            self.text_entrada.insert("1.0", self._draft_prompt)
        else:
            self.text_entrada.insert("1.0", self._historial_prompts[self._historial_idx]["prompt"])
        return "break"

    def _guardar_configuracion(self):
        self.config.set("ancho", self.winfo_width())
        self.config.set("alto", self.winfo_height())
        self.config.set("tamano_texto", self._tamano_texto)
        self.config.guardar()
        self.destroy()

    def _aumentar_texto(self, e=None):
        self._tamano_texto += 1
        self._aplicar_fuente()

    def _disminuir_texto(self, e=None):
        if self._tamano_texto > 8:
            self._tamano_texto -= 1
            self._aplicar_fuente()

    def _aplicar_fuente(self):
        # Fuente única para toda la aplicación
        f = ("Roboto", self._tamano_texto)
        
        # Aplicar a TextBoxes directamente
        self.text_entrada.configure(font=f)
        self.text_salida.configure(font=f)
        
        # Aplicar a etiquetas de tokens y estado
        self.lbl_t_in.configure(font=f)
        self.lbl_t_out.configure(font=f)
        self.label_st.configure(font=f)
        self.label_comp.configure(font=f)
        
        # Aplicar a todos los widgets registrados (Labels, Buttons, Combos, Switches)
        for w in self._widgets_uniformes:
            try:
                if isinstance(w, ctk.CTkComboBox):
                    w.configure(font=f, dropdown_font=f)
                else:
                    w.configure(font=f)
            except:
                pass

    def _update_in_count(self, e=None):
        txt = self.text_entrada.get("1.0", "end-1c")
        # Estimación simple: 4 caracteres por token
        tokens = len(txt) // 4
        self.lbl_t_in.configure(text=f"In: {tokens}")

if __name__ == "__main__":
    app = TokenShrinkApp()
    app.mainloop()