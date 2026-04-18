import customtkinter as ctk
from core.ai_engine import OllamaEngine
from core.window_manager import WindowManager
from core.automation import AutomationController
from utils.config import ConfigManager
import threading
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
        self.title("Token Optimizer (Ollama Only)")
        self.geometry("700x520")

        self.ai_engine = OllamaEngine()
        self.window_manager = WindowManager()
        self.automation = AutomationController()
        self.config = ConfigManager()

        self.modelos = []
        self.ventanas = []
        self.resultado_actual = ""
        self._ultimo_prompt = ""
        self._siempre_visible = False
        self._tamano_texto = self.config.get("tamano_texto", 14)

        self._crear_interfaz()
        self.protocol("WM_DELETE_WINDOW", self._guardar_configuracion)
        self.after(100, self._cargar_datos_iniciales)

    def _crear_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Barra Superior
        frame_top = ctk.CTkFrame(self)
        frame_top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_top.grid_columnconfigure(1, weight=1)
        frame_top.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(frame_top, text="Modelo:").grid(row=0, column=0, padx=5)
        self.combo_modelos = ctk.CTkComboBox(frame_top, values=["Cargando..."], state="readonly", command=self._on_modelo_change)
        self.combo_modelos.grid(row=0, column=1, padx=5, sticky="ew")

        ctk.CTkLabel(frame_top, text="Destino:").grid(row=0, column=2, padx=5)
        self.combo_ventanas = ctk.CTkComboBox(frame_top, values=["Sin apps"], state="readonly", command=self._on_ventana_change)
        self.combo_ventanas.grid(row=0, column=3, padx=5, sticky="ew")
        
        frame_btns = ctk.CTkFrame(frame_top, fg_color="transparent")
        frame_btns.grid(row=0, column=4, padx=5)
        self.btn_pin = ctk.CTkButton(frame_btns, text="📌", width=30, command=self._toggle_siempre_visible)
        self.btn_pin.pack(side="left", padx=2)
        ctk.CTkButton(frame_btns, text="🗑️", width=30, command=self._limpiar).pack(side="left", padx=2)
        ctk.CTkButton(frame_btns, text="↻", width=30, command=self._actualizar_listas).pack(side="left", padx=2)

        # Entrada
        frame_in = ctk.CTkFrame(self)
        frame_in.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        ctk.CTkLabel(frame_in, text="Prompt Original").pack(pady=2)
        self.text_entrada = ctk.CTkTextbox(frame_in, height=100)
        self.text_entrada.pack(fill="both", expand=True, padx=5, pady=2)
        
        # Atajos de teclado para optimización rápida
        self.text_entrada.bind("<Return>", lambda e: (self._ejecutar(), "break")[1])
        self.text_entrada.bind("<KP_Enter>", lambda e: (self._ejecutar(), "break")[1])
        
        # Ctrl+Intro para saltos de línea manuales
        self.text_entrada.bind("<Control-Return>", lambda e: self.text_entrada.insert("insert", "\n"))
        self.text_entrada.bind("<Control-KP_Enter>", lambda e: self.text_entrada.insert("insert", "\n"))
        
        self.label_comp = ctk.CTkLabel(frame_in, text="Compresión: -", text_color="gray")
        self.label_comp.pack(pady=2)
        ctk.CTkButton(frame_in, text="Optimizar", command=self._ejecutar).pack(pady=5)

        # Salida
        frame_out = ctk.CTkFrame(self)
        frame_out.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.frame_out = frame_out
        ctk.CTkLabel(frame_out, text="Prompt Optimizado").pack(pady=2)
        self.text_salida = ctk.CTkTextbox(frame_out, height=100)
        self.text_salida.pack(fill="both", expand=True, padx=5, pady=2)

        f_btns_out = ctk.CTkFrame(frame_out)
        f_btns_out.pack(pady=5)
        ctk.CTkButton(f_btns_out, text="Copiar", width=80, command=self._copiar).pack(side="left", padx=5)
        ctk.CTkButton(f_btns_out, text="Enviar", width=80, command=self._enviar).pack(side="left", padx=5)

        # Footer
        frame_foot = ctk.CTkFrame(self)
        frame_foot.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        self.sw_show = ctk.CTkSwitch(frame_foot, text="Mostrar", command=self._toggle_mostrar)
        self.sw_show.select()
        self.sw_show.pack(side="left", padx=10)

        self.sw_es = ctk.CTkSwitch(frame_foot, text="Traducir a ES", command=self._toggle_idioma)
        self.sw_es.select()
        self.sw_es.pack(side="left", padx=10)

        self.combo_modo = ctk.CTkComboBox(frame_foot, values=["Light", "Optimized", "Aggressive", "Symbolic"], state="readonly", command=self._on_modo_change)
        self.combo_modo.pack(side="left", padx=10)
        self.combo_modo.set("Optimized")

        self.label_st = ctk.CTkLabel(self, text="Listo", text_color="gray")
        self.label_st.grid(row=4, column=0, sticky="w", padx=10)

    def _cargar_datos_iniciales(self):
        self.label_st.configure(text="Cargando sesión...", text_color="yellow")
        
        # Aplicar estados guardados
        if not self.config.get("mostrar_resultado", True): 
            self.sw_show.deselect()
            self.frame_out.grid_remove()
        
        if not self.config.get("traducir_es", True): 
            self.sw_es.deselect()
        
        modo = self.config.get("modo", "Optimized")
        self.combo_modo.set(modo)
        
        self._cargar_modelos()
        self._actualizar_listas()
        self.label_st.configure(text="Listo", text_color="gray")

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
        self._ultimo_prompt = p
        self.label_st.configure(text="Optimizando...", text_color="yellow")
        self.ai_engine.optimize_prompt(p, self._on_complete, self.sw_es.get(), self.combo_modo.get())

    def _on_complete(self, dual):
        import re
        re_es = re.search(r"\[\[ES\]\](.*?)\[\[", dual + " [[", re.DOTALL)
        re_en = re.search(r"\[\[EN\]\](.*?)$", dual, re.DOTALL)
        self.res_es = re_es.group(1).strip() if re_es else dual
        self.res_en = re_en.group(1).strip() if re_en else dual
        res = self.res_es if self.sw_es.get() else self.res_en
        self.text_salida.delete("1.0", "end")
        self.text_salida.insert("1.0", res)
        if self._ultimo_prompt:
            c = ((len(self._ultimo_prompt) - len(res)) / len(self._ultimo_prompt)) * 100
            self.label_comp.configure(text=f"Compresión: {c:.1f}%")
        self.label_st.configure(text="Listo", text_color="green")
        if not self.sw_show.get(): self._enviar()

    def _copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_salida.get("1.0", "end").strip())

    def _enviar(self):
        t = self.text_salida.get("1.0", "end").strip()
        v = self.combo_ventanas.get()
        if t and v:
            self.window_manager.focus_window_by_title(v)
            import time
            self.after(300, lambda: self.automation.inject_text(t))

    def _toggle_mostrar(self):
        self.config.set("mostrar_resultado", self.sw_show.get())
        if self.sw_show.get(): self.frame_out.grid()
        else: self.frame_out.grid_remove()

    def _toggle_siempre_visible(self):
        self._siempre_visible = not self._siempre_visible
        self.attributes("-topmost", self._siempre_visible)
        self.btn_pin.configure(fg_color="blue" if self._siempre_visible else "gray")

    def _limpiar(self):
        self.text_entrada.delete("1.0", "end")
        self.text_salida.delete("1.0", "end")

    def _guardar_configuracion(self):
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
        f = ("Roboto", self._tamano_texto)
        self.text_entrada.configure(font=f)
        self.text_salida.configure(font=f)

if __name__ == "__main__":
    app = TokenShrinkApp()
    app.mainloop()