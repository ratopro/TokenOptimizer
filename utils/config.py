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
            except:
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
            "modelos": {
                "Light": "",
                "Optimized": "",
                "Aggressive": "",
                "Symbolic": ""
            }
        }
    
    def guardar(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.data, f)
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        self.guardar()
    
    def get_modelo_by_mode(self, mode: str) -> str:
        return self.data.get("modelos", {}).get(mode, "")
    
    def set_modelo_by_mode(self, mode: str, model: str):
        if "modelos" not in self.data:
            self.data["modelos"] = {}
        self.data["modelos"][mode] = model
        self.guardar()