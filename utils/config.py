import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".tokenoptimizer"
CONFIG_FILE = CONFIG_DIR / "config.json"

class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cargar()
        return cls._instance

    def _cargar(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.data = json.load(f)
                self._migrate()
            except Exception:
                self._defaults()
        else:
            self._defaults()

    def _defaults(self):
        self.data = {
            "modelo": "",
            "ventana": "",
            "metodo": "Pegado Rápido",
            "enviar_inmediato": False,
            "mostrar_resultado": True,
            "tamano_texto": 14,
            "backend": "Ollama",
            "lmstudio_url": "http://localhost:1234",
            "modelos_ollama": {
                "Light": "",
                "Optimized": "",
                "Aggressive": "",
                "Symbolic": ""
            },
            "modelos_lmstudio": {
                "Light": "",
                "Optimized": "",
                "Aggressive": "",
                "Symbolic": ""
            },
            "backends_por_modo": {
                "Light": "Ollama",
                "Optimized": "Ollama",
                "Aggressive": "Ollama",
                "Symbolic": "Ollama"
            }
        }

    def _migrate(self):
        """Migrate old single 'modelos' key to per-backend keys."""
        if "modelos" in self.data and "modelos_ollama" not in self.data:
            self.data["modelos_ollama"] = self.data.pop("modelos")
        if "modelos_lmstudio" not in self.data:
            self.data["modelos_lmstudio"] = {
                "Light": "", "Optimized": "", "Aggressive": "", "Symbolic": ""
            }
        if "modelos_ollama" not in self.data:
            self.data["modelos_ollama"] = {
                "Light": "", "Optimized": "", "Aggressive": "", "Symbolic": ""
            }
        if "backends_por_modo" not in self.data:
            self.data["backends_por_modo"] = {
                "Light": "Ollama", "Optimized": "Ollama", "Aggressive": "Ollama", "Symbolic": "Ollama"
            }

    def guardar(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.guardar()

    # ── Per-backend model helpers ─────────────────────────────────────────────

    def _key_for_backend(self, backend: str) -> str:
        return "modelos_lmstudio" if backend == "LM Studio" else "modelos_ollama"

    def get_modelo_by_mode(self, mode: str, backend: str = None) -> str:
        if backend is None:
            backend = self.data.get("backend", "Ollama")
        return self.data.get(self._key_for_backend(backend), {}).get(mode, "")

    def set_modelo_by_mode(self, mode: str, model: str, backend: str = None):
        if backend is None:
            backend = self.data.get("backend", "Ollama")
        key = self._key_for_backend(backend)
        if key not in self.data:
            self.data[key] = {}
        self.data[key][mode] = model
        self.guardar()

    def get_all_models_for_backend(self, backend: str) -> dict:
        return dict(self.data.get(self._key_for_backend(backend), {}))

    def set_all_models_for_backend(self, backend: str, models: dict):
        self.data[self._key_for_backend(backend)] = models
        self.guardar()

    def get_backend_for_mode(self, mode: str) -> str:
        return self.data.get("backends_por_modo", {}).get(mode, "Ollama")

    def set_backend_for_mode(self, mode: str, backend: str):
        if "backends_por_modo" not in self.data:
            self.data["backends_por_modo"] = {}
        self.data["backends_por_modo"][mode] = backend
        self.guardar()
