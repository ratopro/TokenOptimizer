# TokenOptimizer

Desktop app for prompt optimization via Ollama with auto-send to other apps.

## Run

```bash
python3 main.py
```

## Architecture

- `core/ai_engine.py` - Ollama integration (async)
- `core/window_manager.py` - Platform window focus
- `core/symbolic_encoder.py` - Symbolic pre-encoder
- `ui/main_window.py` - CustomTkinter GUI

## Optimization Modes

| Mode | temp | top_p |
|------|------|-------|
| Light | 0.3 | 0.9 |
| Optimized | 0.1 | 0.4 |
| Aggressive | 0.0 | 0.1 |
| Symbolic | 0.0 | 0.1 |

## Symbolic Mappings

`and`→`&`, `with`→`w/`, `for`→`->`, `each`→`∀`, `exists`→`∃`, `then`→`=>`, `e.g.`, `i.e.`

## Key Quirks

- Ollama response uses Pydantic: `m.model`
- Ctrl++ zoom: `bind_all("<Control-plus>", ...)`
- pygetwindow: Windows only
- xdotool: Linux only (install separately)
- "Mostrar resultado" OFF → auto-send

## Dependencies

```
pip install --break-system-packages customtkinter ollama pyautogui pyperclip
# Linux
apt install xdotool
```