import re
import threading
import ollama
from typing import Optional, Callable

class OllamaEngine:
    def __init__(self):
        self.current_model: Optional[str] = None
        self._mode = "Optimized"

    def set_model(self, model_name: str) -> bool:
        if not model_name: return False
        self.current_model = model_name
        return True

    def get_available_models(self) -> list:
        try:
            response = ollama.list()
            all_models = [m.model for m in response.models]
            exclude = ['clip', 'llava', 'bakllava', 'vision']
            return [m for m in all_models if not any(kw in m.lower() for kw in exclude)]
        except: return []

    def optimize_prompt(self, prompt: str, callback: Callable[[str, dict], None], traducir: str = "EN", modo: str = "Optimized") -> threading.Thread:
        if not self.current_model:
            callback("[Error] No model selected")
            return None

        def task():
            try:
                # Instrucción de modo
                instruccion_modo = {
                    "Symbolic": "Use symbolic notation (&, ->, ∀) and technical abbreviations (w/, f/).",
                    "Aggressive": "Compress to keywords, telegraphic style, no fluff.",
                    "Light": "Improve clarity/structure, keep original meaning.",
                }.get(modo, "Balance conciseness and clarity, improve structure.")

                system_prompt = (
                    "You are an AI prompt engineer. MANDATORY: Generate the optimized prompt version.\n"
                    f"Task: {instruccion_modo}\n"
                    f"Target Language: {traducir}\n"
                    "FORMAT: [[RES]] (Optimized version). No other text."
                )

                # Proteger comillas
                original_quotes = []
                protected_prompt = re.sub(r'("[^"]*"|\'[^\']*\')', lambda m: (original_quotes.append(m.group(0)), f"[[Q{len(original_quotes)-1}]]")[1], prompt)

                # Generación nativa Ollama
                response = ollama.chat(
                    model=self.current_model,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": protected_prompt}],
                    options={"temperature": 0.1}
                )
                optimized = response['message']['content'].strip()

                # Limpieza y restauración
                optimized = re.sub(r'<think>.*?</think>', '', optimized, flags=re.DOTALL).strip()
                for i, q in enumerate(original_quotes):
                    optimized = optimized.replace(f"[[Q{i}]]", q)
                
                # Extraer estadísticas de tokens si están disponibles
                stats = {
                    "in": response.get('prompt_eval_count', 0),
                    "out": response.get('eval_count', 0)
                }
                
                callback(optimized, stats)
            except Exception as e:
                callback(f"[Error] Generation failed: {str(e)}", {"in": 0, "out": 0})

        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        return thread

    def check_connection(self) -> bool:
        try:
            ollama.list()
            return True
        except: return False
