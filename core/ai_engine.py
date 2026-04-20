import re
import threading
import ollama
from typing import Optional, Callable
from .symbolic_encoder import apply_symbolic_mapping

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
            callback("[Error] No model selected", {"in": 0, "out": 0})
            return None

        def task():
            try:
                # Aplicar pre-procesamiento simbólico si el modo lo requiere o como ayuda
                if modo == "Symbolic":
                    prompt_proc = apply_symbolic_mapping(prompt)
                else:
                    prompt_proc = prompt

                # Instrucción de modo
                instruccion_modo = {
                    "Symbolic": "Use STRICT symbolic notation (&, ->, ∀, ∃, =>) and technical abbreviations. EXTREME compression.",
                    "Aggressive": "Compress to keywords, telegraphic style, no fluff. Remove all auxiliary words.",
                    "Light": "Improve clarity/structure, keep original meaning, slight compression.",
                }.get(modo, "Balance conciseness and clarity, improve structure.")

                # Ejemplos para guiar al modelo (Few-Shot)
                few_shot = (
                    "EXAMPLES:\n"
                    "User: 'Quiero que escribas un código en Python para leer un CSV'\n"
                    "Optimized: [[RES]] Gen Python code to read CSV [[/RES]]\n"
                    "User: 'Puedes traducir esto al inglés y resumirlo un poco?'\n"
                    "Optimized: [[RES]] Tr EN & summarize: [text] [[/RES]]\n"
                )

                system_prompt = (
                    "You are an EXPERT AI prompt engineer. TOKEN REDUCTION IS THE ONLY GOAL.\n"
                    f"Task: {instruccion_modo}\n"
                    f"Target Language: {traducir}\n"
                    f"{few_shot}\n"
                    "RULES:\n"
                    "1. ONLY output the optimized version inside [[RES]] tags.\n"
                    "2. NO chat, NO 'Sure!', NO 'I can help'.\n"
                    "3. If you understand, start directly with [[RES]]."
                )

                # Proteger comillas
                original_quotes = []
                protected_prompt = re.sub(r'("[^"]*"|\'[^\']*\')', lambda m: (original_quotes.append(m.group(0)), f"[[Q{len(original_quotes)-1}]]")[1], prompt_proc)

                # Generación nativa Ollama
                response = ollama.chat(
                    model=self.current_model,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": protected_prompt}],
                    options={"temperature": 0.0} # Menor temperatura para mayor consistencia
                )
                optimized = response['message']['content'].strip()

                # Limpieza agresiva de frases de chatbot si el modelo se salta las reglas
                chat_phrases = [
                    r"Aquí tienes.*?:", r"Claro.*?:", r"Sí, puedo.*?:", 
                    r"Sure!.*?:", r"I can help.*?:", r"Optimized version:.*?:",
                    r"Here is the optimized.*?:", r"Certainly!.*?:",
                    r"^Sí, puedo .*?\.", r"^Claro, .*?\."
                ]
                for phrase in chat_phrases:
                    optimized = re.sub(phrase, "", optimized, flags=re.IGNORECASE | re.DOTALL).strip()

                # Limpieza y restauración
                optimized = re.sub(r'<think>.*?</think>', '', optimized, flags=re.DOTALL).strip()
                for i, q in enumerate(original_quotes):
                    optimized = optimized.replace(f"[[Q{i}]]", q)
                
                # Extraer estadísticas de tokens
                # 'user_in' es una estimación del prompt del usuario para el cálculo de ahorro real
                stats = {
                    "in": response.get('prompt_eval_count', 0),
                    "out": response.get('eval_count', 0),
                    "user_in_est": len(prompt) // 4
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
