# TokenOptimizer

Desktop app for prompt optimization via Ollama with auto-send to other applications.

## Features

- **4 Optimization Modes**: Light, Optimized, Aggressive, Symbolic
- **Symbolic Pre-encoder**: Reduces tokens before LLM processing
- **Auto-send**: Direct integration with other apps
- **History**: Navigate with Up/Down arrows
- **Zoom**: Ctrl++ / Ctrl+- for font size

## Installation

```bash
# Clone or download project
cd TokenOptimizer

# Install dependencies
pip install --break-system-packages customtkinter ollama pyautogui pyperclip

# Linux: install xdotool
sudo apt install xdotool
```

## Usage

```bash
python3 main.py
```

1. Select Ollama model
2. Choose optimization mode:
   - **Light**: Removes greetings/redundancies
   - **Optimized**: Core meaning + key data
   - **Aggressive**: Keywords only
   - **Symbolic**: Mathematical notation + pre-encoder
3. Write prompt, press Enter
4. Toggle "Mostrar resultado" to show or auto-send

## Symbolic Mappings

| Input | Output |
|-------|--------|
| and | & |
| with | w/ |
| for | -> |
| then | => |
| each | ∀ |
| exists | ∃ |
| for example | e.g. |
| that is | i.e. |

## Controls

- **Ctrl++ / Ctrl+-**: Zoom
- **Enter**: Optimize
- **Up / Down**: History
- **Mostrar resultado OFF**: Auto-send to destination

## Requirements

- Python 3.8+
- Ollama running locally
- customtkinter, ollama, pyautogui, pyperclip

## License

MIT