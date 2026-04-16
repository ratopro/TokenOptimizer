import customtkinter as ctk
from core.ai_engine import OllamaEngine
from core.window_manager import WindowManager
from core.automation import AutomationController
from utils.config import ConfigManager
import threading

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

        self.title("Token Optimizer")
        self.geometry("700x500")

        self.ai_engine = OllamaEngine()
        self.window_manager = WindowManager()
        self.automation = AutomationController()
        self.config = ConfigManager()

        self.modelos = []
        self.ventanas = []
        self._ventanas_originales = []
        self.resultado_actual = ""
        self._ultimo_prompt = ""
        self._historial_prompts = []
        self._indice_historial = -1
        self._siempre_visible = False
        
        tamano_guardado = self.config.get("tamano_texto", 14)
        self._tamano_texto = tamano_guardado

        self._crear_interfaz()
        self._cargar_configuracion()
        self.protocol("WM_DELETE_WINDOW", self._guardar_configuracion)
        self.after(100, self._cargar_datos_iniciales)

    def _crear_interfaz(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        frame_config = ctk.CTkFrame(self)
        frame_config.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(frame_config, text="Modelo:").grid(row=0, column=0, padx=3)
        self.combo_modelos = ctk.CTkComboBox(frame_config, values=["Cargando..."], state="readonly", command=self._on_modelo_change, width=200)
        self.combo_modelos.grid(row=0, column=1, padx=3)
        ToolTip(self.combo_modelos, "Seleccionar modelo de IA")

        ctk.CTkLabel(frame_config, text="Destino:").grid(row=0, column=2, padx=3)
        
        self.combo_ventanas = ctk.CTkComboBox(frame_config, values=["Sin aplicaciones"], state="readonly", command=self._on_ventana_change, width=180)
        self.combo_ventanas.grid(row=0, column=3, padx=2)
        ToolTip(self.combo_ventanas, "Seleccionar aplicación destino")
        
        self.combo_ventanas.bind("<Button-1>", self._abrir_combobox)
        
        self.combo_ventanas.bind("<Enter>", self._actualizar_ventanas_hover)
        
        btn_actualizar = ctk.CTkButton(frame_config, text="↻", width=28, height=24, command=self._actualizar_listas)
        btn_actualizar.grid(row=0, column=4, padx=1)
        ToolTip(btn_actualizar, "Actualizar lista de ventanas")

        self.btn_siempre_visible = ctk.CTkButton(frame_config, text="📌", width=28, height=24, command=self._toggle_siempre_visible)
        self.btn_siempre_visible.grid(row=0, column=5, padx=1)
        ToolTip(self.btn_siempre_visible, "Mantener ventana siempre visible")

        btn_limpiar = ctk.CTkButton(frame_config, text="🗑️", width=28, height=24, command=self._limpiar_prompts)
        btn_limpiar.grid(row=0, column=6, padx=2)
        ToolTip(btn_limpiar, "Limpiar campos de texto")

        btn_modelos = ctk.CTkButton(frame_config, text="⚙️", width=28, height=24, command=self._abrir_config_modelos)
        btn_modelos.grid(row=0, column=7, padx=2)
        ToolTip(btn_modelos, "Configurar modelos por modo")

        frame_entrada = ctk.CTkFrame(self)
        frame_entrada.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        ctk.CTkLabel(frame_entrada, text="Prompt Original").pack(pady=2)
        self.text_entrada = ctk.CTkTextbox(frame_entrada, height=80)
        self.text_entrada.pack(fill="both", expand=True, padx=5, pady=2)
        self.text_entrada.bind("<Return>", self._on_enter_press)
        self.text_entrada.bind("<Control-Return>", self._on_ctrl_enter_press)
        self.text_entrada.bind("<Up>", self._historial_arriba)
        self.text_entrada.bind("<Down>", self._historial_abajo)

        self.label_compresion = ctk.CTkLabel(frame_entrada, text="Compresión: -", text_color="gray")
        self.label_compresion.pack(pady=2)

        btn_optimizar = ctk.CTkButton(frame_entrada, text="Optimizar", width=120, height=26, font=("Roboto", 12), command=self._ejecutar_optimizacion)
        btn_optimizar.pack(pady=3)
        ToolTip(btn_optimizar, "Optimizar prompt con IA (Enter)")

        frame_salida = ctk.CTkFrame(self)
        frame_salida.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.frame_salida = frame_salida

        ctk.CTkLabel(frame_salida, text="Prompt Optimizado").pack(pady=2)
        self.text_salida = ctk.CTkTextbox(frame_salida, height=80)
        self.text_salida.pack(fill="both", expand=True, padx=5, pady=2)
        self.text_salida.bind("<Control-a>", self._seleccionar_texto_salida)

        frame_botones_salida = ctk.CTkFrame(frame_salida)
        frame_botones_salida.pack(pady=2)

        btn_copiar = ctk.CTkButton(frame_botones_salida, text="Copiar", width=70, height=24, font=("Roboto", 11), command=self._copiar_resultado)
        btn_copiar.pack(side="left", padx=3)
        ToolTip(btn_copiar, "Copiar resultado al portapapeles")

        btn_enviar = ctk.CTkButton(frame_botones_salida, text="Enviar", width=70, height=24, font=("Roboto", 11), command=self._enviar_prompt)
        btn_enviar.pack(side="left", padx=3)
        ToolTip(btn_enviar, "Enviar resultado a aplicación destino")

        frame_opciones = ctk.CTkFrame(self)
        frame_opciones.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        self.switch_mostrar = ctk.CTkSwitch(frame_opciones, text="Mostrar resultado", command=self._toggle_mostrar)
        self.switch_mostrar.select()
        self.switch_mostrar.pack(side="left", padx=10)
        ToolTip(self.switch_mostrar, "ON: mostrar respuesta | OFF: enviar a destino")

        self.switch_traducir = ctk.CTkSwitch(frame_opciones, text="Traducir al inglés", command=self._toggle_traducir)
        self.switch_traducir.select()
        self.switch_traducir.pack(side="left", padx=10)
        ToolTip(self.switch_traducir, "Traducir el prompt al inglés antes de optimizar")

        self.combo_modos = ctk.CTkComboBox(frame_opciones, values=["Light", "Optimized", "Aggressive", "Symbolic"], state="readonly", command=self._on_modo_change, width=100)
        self.combo_modos.pack(side="left", padx=10)
        self.combo_modos.set("Optimized")
        ToolTip(self.combo_modos, "Modo de optimización")

        self.label_estado = ctk.CTkLabel(self, text="Listo", text_color="gray")
        self.label_estado.grid(row=4, column=0, pady=5)

        self._aplicar_tamano_texto()
        
        self.bind_all("<Control-plus>", self._aumentar_texto)
        self.bind_all("<Control-minus>", self._disminuir_texto)
        self.bind_all("<Control-equal>", self._aumentar_texto)
        self.bind_all("<Control-KP_Add>", self._aumentar_texto)
        self.bind_all("<Control-KP_Subtract>", self._disminuir_texto)

    def _cargar_datos_iniciales(self):
        threading.Thread(target=self._cargar_modelos, daemon=True).start()
        self._actualizar_listas()

    def _cargar_modelos(self):
        self.modelos = self.ai_engine.get_available_models()
        self.after(0, self._actualizar_combo_modelos)

    def _actualizar_combo_modelos(self):
        if self.modelos:
            self.combo_modelos.configure(values=self.modelos)
            modelo_guardado = self.config.get("modelo")
            if modelo_guardado and modelo_guardado in self.modelos:
                self.combo_modelos.set(modelo_guardado)
                self.ai_engine.set_model(modelo_guardado)
            else:
                self.combo_modelos.set(self.modelos[0])
                self.ai_engine.set_model(self.modelos[0])
            self.label_estado.configure(text=f"Modelos: {len(self.modelos)}", text_color="green")
        else:
            self.combo_modelos.configure(values=["Sin modelos"])
            self.label_estado.configure(text="Error: Ollama no disponible", text_color="red")

    def _actualizar_listas(self):
        threading.Thread(target=self._obtener_ventanas, daemon=True).start()

    def _obtener_ventanas(self):
        self.ventanas = self.window_manager.get_active_windows()
        self._ventanas_originales = self.ventanas.copy()
        self.after(0, self._actualizar_combo_ventanas)

    def _filtrar_ventanas(self, event=None):
        return "break"

    def _detectar_ventana_activa(self):
        import platform
        import subprocess
        
        if platform.system() == "Linux":
            try:
                result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], 
                                      capture_output=True, text=True)
                ventana_activa = result.stdout.strip()
                
                self.btn_detectar.configure(text="❌")
                
                if ventana_activa and ventana_activa in self.ventanas:
                    self.combo_ventanas.set(ventana_activa)
                    self.label_estado.configure(text=f"Detectado: {ventana_activa}", text_color="cyan")
                else:
                    self.label_estado.configure(text="Ventana activa no encontrada", text_color="yellow")
            except Exception as e:
                self.label_estado.configure(text="Error detectando ventana", text_color="red")
        else:
            self.label_estado.configure(text="Solo disponible en Linux", text_color="yellow")
        return "break"

    def _abrir_combobox(self, event=None):
        self._actualizar_listas()
        return

    def _actualizar_ventanas_hover(self, event=None):
        self._actualizar_listas()
        return

    def _actualizar_combo_ventanas(self):
        if self.ventanas:
            self.combo_ventanas.configure(values=self.ventanas)
            ventana_guardada = self.config.get("ventana")
            if ventana_guardada and ventana_guardada in self.ventanas:
                self.combo_ventanas.set(ventana_guardada)
            else:
                self.combo_ventanas.set(self.ventanas[0])
        self.label_estado.configure(text=f"Ventanas: {len(self.ventanas)}")

    def _on_modelo_change(self, choice):
        self.config.set("modelo", choice)
        self.ai_engine.set_model(choice)
    
    def _on_modo_change(self, mode):
        self.ai_engine.set_mode(mode)
        self.config.set("modo", mode)
        
        modelo_asignado = self.config.get_modelo_by_mode(mode)
        if modelo_asignado:
            self.ai_engine.set_model(modelo_asignado)
            self.combo_modelos.set(modelo_asignado)
        
        if mode == "Symbolic":
            self.label_estado.configure(text="Recommended: llama3.2:3b or qwen2.5:1.5b", text_color="cyan")
        else:
            self.label_estado.configure(text="Ready", text_color="gray")

    def _abrir_config_modelos(self):
        ventana_config = ctk.CTkToplevel(self)
        ventana_config.title("Configurar Modelos")
        ventana_config.geometry("500x400")
        
        modos = ["Light", "Optimized", "Aggressive", "Symbolic"]
        self._combos_modelos = {}
        
        for modo in modos:
            frame_mode = ctk.CTkFrame(ventana_config)
            frame_mode.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame_mode, text=modo, width=100).pack(side="left", padx=5)
            
            combo = ctk.CTkComboBox(frame_mode, values=self.modelos, state="readonly", width=250)
            modelo_actual = self.config.get_modelo_by_mode(modo)
            if modelo_actual and modelo_actual in self.modelos:
                combo.set(modelo_actual)
            combo.pack(side="left", padx=5)
            self._combos_modelos[modo] = combo
        
        def guardar_modelos():
            for modo, combo in self._combos_modelos.items():
                modelo = combo.get()
                if modelo:
                    self.config.set_modelo_by_mode(modo, modelo)
            ventana_config.destroy()
            self.label_estado.configure(text="Modelos guardados", text_color="green")
        
        btn_guardar = ctk.CTkButton(ventana_config, text="Guardar", command=guardar_modelos)
        btn_guardar.pack(pady=10)

    def _on_ventana_change(self, choice):
        self.config.set("ventana", choice)

    def _ejecutar_optimizacion(self):
        prompt_original = self.text_entrada.get("1.0", "end").strip()
        if not prompt_original:
            self.label_estado.configure(text="Error: Prompt vacío", text_color="red")
            return

        self._ultimo_prompt = prompt_original
        
        if prompt_original not in self._historial_prompts:
            self._historial_prompts.append(prompt_original)
            if len(self._historial_prompts) > 50:
                self._historial_prompts.pop(0)
        self._indice_historial = len(self._historial_prompts)
        
        modelo_seleccionado = self.combo_modelos.get()
        if modelo_seleccionado:
            self.ai_engine.set_model(modelo_seleccionado)

        self.label_estado.configure(text="Optimizando...", text_color="yellow")
        traducir = self.switch_traducir.get()
        self.ai_engine.optimize_prompt(prompt_original, self._on_optimizacion_complete, traducir)

    def _on_optimizacion_complete(self, resultado: str):
        self.resultado_actual = resultado
        
        self.text_salida.configure(state="normal")
        self.text_salida.delete("1.0", "end")
        self.text_salida.insert("1.0", resultado)
        self.text_salida.configure(state="disabled" if not self.switch_mostrar.get() else "normal")
        
        if self._ultimo_prompt:
            original_len = len(self._ultimo_prompt)
            optimizado_len = len(resultado)
            if original_len > 0:
                compresion = ((original_len - optimizado_len) / original_len) * 100
                self.label_compresion.configure(text=f"Compresión: {compresion:.1f}% ({original_len} → {optimizado_len})")
                self.label_estado.configure(text=f"Optimización completa ({compresion:.1f}%)", text_color="green")
            else:
                self.label_compresion.configure(text="Compresión: 0%")
                self.label_estado.configure(text="Optimización completa", text_color="green")
        
        if not self.switch_mostrar.get():
            self.after(100, self._enviar_a_app)
        else:
            self.after(100, self._ajustar_ventana)

    def _toggle_mostrar(self):
        if self.switch_mostrar.get():
            self.frame_salida.grid()
            self.text_salida.configure(state="normal")
        else:
            self.frame_salida.grid_remove()
            self.text_salida.configure(state="disabled")
        
        self.after(100, self._ajustar_ventana)
        
        if self.resultado_actual:
            self.text_salida.delete("1.0", "end")
            self.text_salida.insert("1.0", self.resultado_actual)
            self.text_salida.configure(state="disabled" if not self.switch_mostrar.get() else "normal")
        return "break"

    def _toggle_envio(self):
        if not self.switch_enviar.get():
            self.switch_mostrar.select()
            self.frame_salida.grid()
            self.text_salida.configure(state="normal")
            self.switch_enviar.configure(state="normal")
        
        if self.resultado_actual:
            self.text_salida.delete("1.0", "end")
            self.text_salida.insert("1.0", self.resultado_actual)
            self.text_salida.configure(state="disabled" if not self.switch_mostrar.get() else "normal")
        return "break"

    def _toggle_traducir(self):
        return "break"

    def _toggle_siempre_visible(self):
        self._siempre_visible = not self._siempre_visible
        if self._siempre_visible:
            self.attributes("-topmost", True)
            self.btn_siempre_visible.configure(fg_color="green")
        else:
            self.attributes("-topmost", False)
            self.btn_siempre_visible.configure(fg_color="gray")
        return "break"

    def _limpiar_prompts(self):
        self.text_entrada.delete("1.0", "end")
        self.text_salida.delete("1.0", "end")
        self.resultado_actual = ""
        self.label_compresion.configure(text="Compresión: -")
        self.label_estado.configure(text="Campos limpiados", text_color="green")

    def _seleccionar_texto_salida(self, event=None):
        self.text_salida.tag_add("sel", "1.0", "end")
        return "break"

    def _on_enter_press(self, event=None):
        self._ejecutar_optimizacion()
        return "break"

    def _on_ctrl_enter_press(self, event=None):
        self.text_entrada.insert("insert", "\n")
        return "break"

    def _historial_arriba(self, event=None):
        if not self._historial_prompts:
            return "break"
        if self._indice_historial > 0:
            self._indice_historial -= 1
            self.text_entrada.delete("1.0", "end")
            self.text_entrada.insert("1.0", self._historial_prompts[self._indice_historial])
        return "break"

    def _historial_abajo(self, event=None):
        if not self._historial_prompts:
            return "break"
        if self._indice_historial < len(self._historial_prompts) - 1:
            self._indice_historial += 1
            self.text_entrada.delete("1.0", "end")
            self.text_entrada.insert("1.0", self._historial_prompts[self._indice_historial])
        else:
            self._indice_historial = len(self._historial_prompts)
            self.text_entrada.delete("1.0", "end")
        return "break"

    def _aumentar_texto(self, event=None):
        self._tamano_texto = min(self._tamano_texto + 2, 32)
        self._aplicar_tamano_texto()
        self._ajustar_ventana()
        self.config.set("tamano_texto", self._tamano_texto)
        return "break"

    def _disminuir_texto(self, event=None):
        self._tamano_texto = max(self._tamano_texto - 2, 8)
        self._aplicar_tamano_texto()
        self._ajustar_ventana()
        self.config.set("tamano_texto", self._tamano_texto)
        return "break"
    
    def _ajustar_ventana(self):
        base_width = 600
        base_height = 500
        
        if not self.switch_mostrar.get():
            base_height = base_height * 0.6
        
        entrada_len = len(self.text_entrada.get("1.0", "end"))
        if entrada_len > 200:
            base_height += (entrada_len - 200) // 50 * 20
        
        if self.switch_mostrar.get():
            salida_len = len(self.text_salida.get("1.0", "end"))
            if salida_len > 200:
                base_height += (salida_len - 200) // 50 * 20
        
        new_width = 700
        new_height = base_height
        new_width = max(450, min(850, new_width))
        new_height = max(280, min(750, new_height))
        self.geometry(f"{new_width}x{new_height}")
    
    def _aplicar_tamano_texto(self):
        font_size = self._tamano_texto
        
        self.text_entrada.configure(font=("Roboto", font_size))
        self.text_salida.configure(font=("Roboto", font_size))
        self.label_compresion.configure(font=("Roboto", font_size - 2))
        self.label_estado.configure(font=("Roboto", font_size - 2))
        
        factor = font_size / 14
        
        if hasattr(self, 'combo_modelos'):
            self.combo_modelos.configure(font=("Roboto", int(12 * factor)))
            self.combo_ventanas.configure(font=("Roboto", int(12 * factor)))
        
        self._aplicar_todos_widgets(factor)
    
    def _aplicar_todos_widgets(self, factor):
        for widget in self.winfo_children():
            self._aplicar_tamano_recursivo(widget, factor)
    
    def _aplicar_tamano_recursivo(self, widget, factor):
        font_size = self._tamano_texto
        try:
            widget_class = widget.winfo_class()
            
            if widget_class in ['Label', 'CTkLabel']:
                try:
                    current_font = widget.cget("font")
                    if isinstance(current_font, tuple) and len(current_font) >= 2:
                        widget.configure(font=(current_font[0], int(current_font[1] * factor)))
                    else:
                        widget.configure(font=("Roboto", int(12 * factor)))
                except:
                    widget.configure(font=("Roboto", int(12 * factor)))
            
            elif widget_class in ['TCombobox', 'CTkComboBox']:
                try:
                    font_size = int(12 * factor)
                    widget.configure(font=("Roboto", font_size))
                    
                    base_width = 200
                    new_width = max(150, int(base_width * factor))
                    widget.configure(width=new_width)
                except:
                    pass
            
            elif widget_class in ['Button', 'CTkButton']:
                try:
                    base_height = 26
                    base_width = 80
                    new_height = int(base_height * factor)
                    new_width = int(base_width * factor)
                    widget.configure(height=new_height, width=new_width, font=("Roboto", int(11 * factor)))
                except:
                    pass
            
            elif widget_class in ['TEntry', 'CTkEntry']:
                try:
                    widget.configure(font=("Roboto", int(font_size)))
                except:
                    pass
            
            elif widget_class in ['Checkbutton', 'CTkSwitch']:
                try:
                    widget.configure(font=("Roboto", int(11 * factor)))
                except:
                    pass
            
        except:
            pass
        
        try:
            for child in widget.winfo_children():
                self._aplicar_tamano_recursivo(child, factor)
        except:
            pass

    def _copiar_resultado(self):
        try:
            import pyperclip
            contenido = self.text_salida.get("1.0", "end-1c")
            pyperclip.copy(contenido)
            self.label_estado.configure(text="Texto copiado", text_color="green")
        except Exception as e:
            self.label_estado.configure(text=f"Error: {str(e)[:30]}", text_color="red")

    def _enviar_a_app(self):
        try:
            import pyperclip
            import pyautogui
            import time
            
            contenido = self.text_salida.get("1.0", "end-1c")
            
            ventana_destino = self.combo_ventanas.get()
            
            if self.window_manager.focus_window_by_title(ventana_destino):
                time.sleep(0.3)
                pyperclip.copy(contenido)
                time.sleep(0.2)
                pyautogui.write(contenido, interval=0.01)
                pyautogui.press('enter')
                
                self.text_entrada.delete("1.0", "end")
                self.text_salida.delete("1.0", "end")
                self.resultado_actual = ""
                self.label_estado.configure(text="Enviado a: " + ventana_destino, text_color="cyan")
            else:
                self.label_estado.configure(text="Error: Ventana no encontrada", text_color="red")
        except Exception as e:
            self.label_estado.configure(text=f"Error: {str(e)[:30]}", text_color="red")

    def _enviar_prompt(self):
        try:
            import pyperclip
            import pyautogui
            import time
            
            contenido = self.text_salida.get("1.0", "end-1c")
            
            ventana_destino = self.combo_ventanas.get()
            
            if self.window_manager.focus_window_by_title(ventana_destino):
                time.sleep(0.3)
                pyperclip.copy(contenido)
                time.sleep(0.2)
                pyautogui.write(contenido, interval=0.01)
                pyautogui.press('enter')
                
                self.text_entrada.delete("1.0", "end")
                self.text_salida.delete("1.0", "end")
                self.resultado_actual = ""
                self.label_estado.configure(text="Enviado a: " + ventana_destino, text_color="cyan")
            else:
                self.label_estado.configure(text="Error: Ventana no encontrada", text_color="red")
        except Exception as e:
            self.label_estado.configure(text=f"Error: {str(e)[:30]}", text_color="red")

    def _cargar_configuracion(self):
        geo = self.config.get("geo")
        if geo:
            self.geometry(geo)
        
        self._siempre_visible = self.config.get("siempre_visible", False)
        if self._siempre_visible:
            self.attributes("-topmost", True)
            self.btn_siempre_visible.configure(fg_color="green")
        
        if self.config.get("mostrar_resultado", True):
            self.switch_mostrar.select()
            self.frame_salida.grid()
            self.text_salida.configure(state="normal")
        else:
            self.switch_mostrar.deselect()
            self.frame_salida.grid_remove()
            self.text_salida.configure(state="disabled")
        
        if self.config.get("traducir", True):
            self.switch_traducir.select()
        else:
            self.switch_traducir.deselect()
    
    def _guardar_configuracion(self):
        self.config.set("geo", self.geometry())
        self.config.set("siempre_visible", self._siempre_visible)
        self.config.set("mostrar_resultado", self.switch_mostrar.get())
        self.config.set("traducir", self.switch_traducir.get())
        self.destroy()

if __name__ == "__main__":
    app = TokenShrinkApp()
    app.mainloop()