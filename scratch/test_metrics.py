import sys
import os
from unittest.mock import MagicMock

# Añadir el path del proyecto
sys.path.append(os.getcwd())

from core.ai_engine import OllamaEngine

def test_token_extraction():
    engine = OllamaEngine()
    engine.current_model = "test-model"
    
    # Simular respuesta de Ollama
    mock_response = {
        'message': {'content': '[[ES]] Hola [[EN]] Hello'},
        'prompt_eval_count': 150,  # Tokens de entrada
        'eval_count': 45           # Tokens de salida
    }
    
    # Mock de ollama.chat
    import ollama
    ollama.chat = MagicMock(return_value=mock_response)
    
    def callback(text, stats):
        print(f"Resultado: {text}")
        print(f"Stats capturadas: {stats}")
        assert stats['in'] == 150
        assert stats['out'] == 45
        print("✅ Verificación de extracción de tokens: EXITOSA")

    # Ejecutar optimización (se lanza en un hilo, esperamos)
    thread = engine.optimize_prompt("Test prompt", callback)
    thread.join()

if __name__ == "__main__":
    try:
        test_token_extraction()
    except Exception as e:
        print(f"❌ Error en la verificación: {e}")
