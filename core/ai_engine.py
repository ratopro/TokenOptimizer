import re
import threading
import ollama
from typing import Optional, Callable
from pydantic import BaseModel, Field
from .symbolic_encoder import apply_symbolic_mapping

class OptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    traducir: str = "EN"
    modo: str = "Optimized"

class OllamaEngine:
    def __init__(self):
        self.current_model: Optional[str] = None
        self._mode = "Optimized"

    def set_model(self, model_name: str) -> bool:
        if not model_name:
            return False
        self.current_model = model_name
        return True

    def get_available_models(self) -> list:
        try:
            response = ollama.list()
            return [m.model for m in response.models
                    if not any(kw in m.model.lower() for kw in ['clip', 'llava', 'bakllava', 'vision'])]
        except Exception:
            return []

    def optimize_prompt(self, prompt: str, callback: Callable, traducir: str = "EN", modo: str = "Optimized") -> threading.Thread:
        try:
            request = OptimizeRequest(prompt=prompt, traducir=traducir, modo=modo)
        except Exception as e:
            callback(f"[Error] Invalid input: {e}", {"in": 0, "out": 0})
            return None

        if not self.current_model:
            callback("[Error] No model selected", {"in": 0, "out": 0})
            return None

        def task():
            try:
                p, m = request.prompt, request.modo
                prompt_proc = apply_symbolic_mapping(p) if m == "Symbolic" else p

                instruccion = {
                    "Symbolic": "Use STRICT symbolic notation (&, ->, ∀, ∃, =>). EXTREME compression.",
                    "Aggressive": "Compress to keywords, telegraphic style, no fluff.",
                    "Light": "Improve clarity/structure, keep meaning.",
                }.get(m, "Balance conciseness and clarity.")

                few_shot = "EXAMPLES:\nUser: ' Quiero que escribas un código...'\nOptimized: [[RES]] Gen Python code... [[/RES]]\n"

                system_prompt = f"You are an AI prompt engineer. TOKEN REDUCTION IS THE GOAL.\nTask: {instruccion}\nTarget: {traducir}\n{few_shot}Rules:\n1. ONLY output inside [[RES]] tags.\n2. NO chat, NO 'Sure!'."

                original_quotes = []
                protected = re.sub(r'("[^"]*"|\'[^\']*\')', lambda m: (original_quotes.append(m.group(0)), f"[[Q{len(original_quotes)-1}]]")[1], prompt_proc)

                response = ollama.chat(model=self.current_model, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": protected}], options={"temperature": 0.0})
                optimized = response['message']['content'].strip()

                chat_pattern = r"(Aqui tienes|Claro|SI can|Sure!|I can help|Optimized version|Here is|Certainly!)"
                optimized = re.sub(chat_pattern, "", optimized, flags=re.IGNORECASE).strip()
                optimized = re.sub(r'<think>.*?</think>', '', optimized, flags=re.DOTALL).strip()

                for i, q in enumerate(original_quotes):
                    optimized = optimized.replace(f"[[Q{i}]]", q)

                stats = {"in": getattr(response, 'prompt_eval_count', 0), "out": getattr(response, 'eval_count', 0), "user_in_est": len(p) // 4}
                callback(optimized, stats)
            except Exception as e:
                callback(f"[Error] Generation failed: {e}", {"in": 0, "out": 0})

        threading.Thread(target=task, daemon=True).start()

    def check_connection(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False
