import threading
import ollama
from typing import Optional, Callable
from core.symbolic_encoder import apply_symbolic_mapping

OPTIMIZATION_MODES = {
    "Light": {
        "prompt": "Compress the prompt by removing unnecessary greetings and obvious redundancies. Keep the original tone. Output only plain text.",
        "temperature": 0.3,
        "top_p": 0.9
    },
    "Optimized": {
        "prompt": "Act as a token optimizer. Remove filler words and politeness. Maintain core meaning and key data. Output only plain text.",
        "temperature": 0.1,
        "top_p": 0.4
    },
    "Aggressive": {
        "prompt": "Extreme compression. Remove everything except keywords and core commands. Use telegraphic style. Output only keywords and logic.",
        "temperature": 0.0,
        "top_p": 0.1
    },
    "Symbolic": {
        "prompt": "Rewrite the input using symbolic notation, math operators, and common abbreviations (e.g., & for and, -> for lead to). Use a key-value or telegraphic format. Remove all articles and non-essential connectors. Output only the encoded plain text.",
        "temperature": 0.0,
        "top_p": 0.1
    }
}

class OllamaEngine:
    def __init__(self):
        self.current_model: Optional[str] = None
        self._mode = "Optimized"
        self._traducir = True
    
    def set_mode(self, mode: str):
        if mode in OPTIMIZATION_MODES:
            self._mode = mode
    
    def get_mode(self) -> str:
        return self._mode
    
    def get_modes(self) -> list:
        return list(OPTIMIZATION_MODES.keys())
    
    def get_available_models(self) -> list:
        try:
            response = ollama.list()
            all_models = [m.model for m in response.models]
            exclude_keywords = ['clip', 'llava', 'bakllava', 'vision']
            text_models = [m for m in all_models if not any(kw in m.lower() for kw in exclude_keywords)]
            return text_models if text_models else all_models
        except Exception as e:
            print(f"[Error] Ollama: {e}")
            return []

    def set_model(self, model_name: str) -> bool:
        if not model_name:
            return False
        self.current_model = model_name
        return True

    def get_prompt(self, traducir: bool = True) -> str:
        mode = OPTIMIZATION_MODES[self._mode]
        base_prompt = mode["prompt"]
        
        if traducir:
            base_prompt = (
                f"First simplify in English: {base_prompt}\n"
                "Then translate to English if needed."
            )
        
        return base_prompt

    def optimize_prompt(self, prompt: str, callback: Callable[[str], None], traducir: bool = True) -> threading.Thread:
        if not self.current_model:
            callback("[Error] Modelo no seleccionado")
            return None
        
        if not prompt.strip():
            callback("[Error] Prompt vacío")
            return None

        self._traducir = traducir
        thread = threading.Thread(
            target=self._generate_optimized_text,
            args=(prompt, callback),
            daemon=True
        )
        thread.start()
        return thread

    def _generate_optimized_text(self, prompt: str, callback: Callable[[str], None]):
        try:
            mode = OPTIMIZATION_MODES[self._mode]
            
            if self._mode == "Symbolic":
                prompt = apply_symbolic_mapping(prompt)
            
            system_prompt = self.get_prompt(self._traducir)
            full_prompt = f"{system_prompt}\n\nInput:\n{prompt}"
            
            options = {
                'temperature': mode["temperature"],
                'top_p': mode["top_p"],
                'num_predict': 512
            }
            
            response = ollama.generate(
                model=self.current_model,
                prompt=full_prompt,
                options=options
            )
            
            optimized_text = response['response'].strip()
            callback(optimized_text)
            
        except Exception as e:
            callback(f"[Error] Fallo en la generación: {e}")

    def check_connection(self) -> bool:
        try:
            ollama.list()
            return True
        except Exception:
            return False