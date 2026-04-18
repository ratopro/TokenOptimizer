import re
import threading
import requests
import ollama
from typing import Optional, Callable
from core.symbolic_encoder import apply_symbolic_mapping

OPTIMIZATION_MODES = {
    "Light": {
        "system": (
            "You are a prompt optimizer. Your ONLY job is to rewrite the user's prompt: "
            "ensure the output is in Spanish if the translation flag is set, otherwise keep the original language. "
            "Remove unnecessary greetings and obvious redundancies while keeping the original tone. "
            "Output ONLY the rewritten prompt in the target language. No explanations, no commentary, no extra text."
        ),
        "temperature": 0.3,
        "top_p": 0.9
    },
    "Optimized": {
        "system": (
            "You are a prompt optimizer. Your ONLY job is to rewrite the user's prompt: "
            "ensure the output is in Spanish if the translation flag is set, otherwise keep the original language. "
            "Remove filler words, politeness and redundancy while preserving core meaning and key data. "
            "Output ONLY the rewritten prompt in the target language. No explanations, no commentary, no extra text."
        ),
        "temperature": 0.1,
        "top_p": 0.4
    },
    "Aggressive": {
        "system": (
            "You are a prompt optimizer. Your ONLY job is to rewrite the user's prompt: "
            "ensure the output is in Spanish if the translation flag is set, otherwise keep the original language. "
            "Compress it to the bare minimum — keywords and core commands only, telegraphic style. "
            "Output ONLY the rewritten prompt in the target language. No explanations, no commentary, no extra text."
        ),
        "temperature": 0.0,
        "top_p": 0.1
    },
    "Symbolic": {
        "system": (
            "You are a prompt optimizer. Your ONLY job is to rewrite the user's prompt: "
            "ensure the output is in Spanish if the translation flag is set, otherwise keep the original language. "
            "Rewrite it using symbolic notation and abbreviations "
            "(e.g. & for 'and', -> for 'leads to', w/ for 'with', ∀ for 'each'). Remove all articles and non-essential connectors. "
            "Output ONLY the rewritten prompt in the target language. No explanations, no commentary, no extra text."
        ),
        "temperature": 0.0,
        "top_p": 0.1
    }
}

BACKENDS = ["Ollama", "LM Studio"]


class OllamaEngine:
    def __init__(self):
        self.current_model: Optional[str] = None
        self._mode = "Optimized"
        self._traducir = True
        self._backend = "Ollama"
        self._lmstudio_url = "http://localhost:1234"

    # ── Backend ──────────────────────────────────────────────────────────────

    def set_backend(self, backend: str):
        if backend in BACKENDS:
            self._backend = backend

    def get_backend(self) -> str:
        return self._backend

    def set_lmstudio_url(self, url: str):
        self._lmstudio_url = url.rstrip("/")

    def get_lmstudio_url(self) -> str:
        return self._lmstudio_url

    # ── Mode ─────────────────────────────────────────────────────────────────

    def set_mode(self, mode: str):
        if mode in OPTIMIZATION_MODES:
            self._mode = mode

    def get_mode(self) -> str:
        return self._mode

    def get_modes(self) -> list:
        return list(OPTIMIZATION_MODES.keys())

    # ── Models ────────────────────────────────────────────────────────────────

    def get_available_models(self) -> list:
        if self._backend == "LM Studio":
            return self._get_lmstudio_models()
        return self._get_ollama_models()

    def _get_ollama_models(self) -> list:
        try:
            response = ollama.list()
            all_models = [m.model for m in response.models]
            exclude_keywords = ['clip', 'llava', 'bakllava', 'vision']
            text_models = [m for m in all_models if not any(kw in m.lower() for kw in exclude_keywords)]
            return text_models if text_models else all_models
        except Exception as e:
            print(f"[Error] Ollama: {e}")
            return []

    def _get_lmstudio_models(self) -> list:
        try:
            resp = requests.get(f"{self._lmstudio_url}/v1/models", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception as e:
            print(f"[Error] LM Studio: {e}")
            return []

    def set_model(self, model_name: str) -> bool:
        if not model_name:
            return False
        self.current_model = model_name
        return True

    # ── Prompt ────────────────────────────────────────────────────────────────

    def get_system_prompt(self, traducir: bool = True) -> str:
        mode = OPTIMIZATION_MODES[self._mode]
        system = mode["system"]
        if traducir:
            system = system.replace("ensure the output is in Spanish if the translation flag is set, otherwise keep the original language", "MANDATORY: Translate the prompt to SPANISH and then optimize it")
        else:
            system = system.replace("ensure the output is in Spanish if the translation flag is set, otherwise keep the original language", "Optimize the prompt while keeping its ORIGINAL language")
        return system

    # ── Optimization ─────────────────────────────────────────────────────────

    def optimize_prompt(self, prompt: str, callback: Callable[[str], None], traducir: bool = True) -> threading.Thread:
        if not self.current_model:
            callback("[Error] No model selected")
            return None

        if not prompt.strip():
            callback("[Error] Empty prompt")
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
            if self._backend == "LM Studio":
                self._generate_lmstudio(prompt, callback)
            else:
                self._generate_ollama(prompt, callback)
        except Exception as e:
            callback(f"[Error] Generation failed: {e}")

    def _build_messages(self, prompt: str) -> tuple:
        """Returns (system_prompt, prompt_for_llm)"""
        system_prompt = self.get_system_prompt(self._traducir)
        if self._mode == "Symbolic":
            prompt_for_llm = apply_symbolic_mapping(prompt)
        else:
            prompt_for_llm = prompt
        return system_prompt, prompt_for_llm

    def _generate_ollama(self, prompt: str, callback: Callable[[str], None]):
        mode = OPTIMIZATION_MODES[self._mode]
        system_prompt, prompt_for_llm = self._build_messages(prompt)

        options = {
            'temperature': mode["temperature"],
            'top_p': mode["top_p"],
            'num_predict': 512
        }

        response = ollama.chat(
            model=self.current_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_for_llm}
            ],
            options=options
        )

        optimized_text = response['message']['content'].strip()
        optimized_text = self._clean_thought_process(optimized_text)
        callback(optimized_text)

    def _generate_lmstudio(self, prompt: str, callback: Callable[[str], None]):
        mode = OPTIMIZATION_MODES[self._mode]
        system_prompt, prompt_for_llm = self._build_messages(prompt)

        payload = {
            "model": self.current_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_for_llm}
            ],
            "temperature": mode["temperature"],
            "top_p": mode["top_p"],
            "max_tokens": 512,
            "stream": False
        }

        resp = requests.post(
            f"{self._lmstudio_url}/v1/chat/completions",
            json=payload,
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        optimized_text = data["choices"][0]["message"]["content"].strip()
        optimized_text = self._clean_thought_process(optimized_text)
        callback(optimized_text)

    # ── Connection ────────────────────────────────────────────────────────────

    def check_connection(self) -> bool:
        if self._backend == "LM Studio":
            try:
                requests.get(f"{self._lmstudio_url}/v1/models", timeout=3)
                return True
            except Exception:
                return False
        try:
            ollama.list()
            return True
        except Exception:
            return False

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _clean_thought_process(self, text: str) -> str:
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
