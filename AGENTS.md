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

---

# Agent: Software Architect

**Skill**: `.agents/skills/software-architect/`

## When to Activate
- Defining system structure, choosing tech stacks
- Evaluating technical trade-offs
- Creating APIs or module boundaries

## Workflow
1. Clarify quality attributes (scalability, latency, availability)
2. For **Web**: Consult `WEB_PATTERNS.md`
3. For **Desktop**: Consult patterns in skill
4. Document decisions with ADR using `ADR_TEMPLATE.md`

## Anti-Rationalization Table
| Agent Excuse | Response |
|---|---|
| "We'll make it scalable later" | "Architecture is defined in design, not patched later" |
| "This is industry standard" | "Every decision requires a context-based ADR" |
| "Looks like it will work" | "Verification is non-negotiable; design evidence required" |

---

# Agent: Security Specialist

**Skill**: `.agents/skills/python-security-hardener/`

## When to Activate
- Writing new code or auditing existing code
- Before any commit

## Mandatory Workflow (execute in order)
1. **SAST Scan**: Run `python .agents/skills/python-security-hardener/scripts/security_scan.py`
2. **Secret Management**: Validate NO API keys or passwords in code; enforce `.env` usage
3. **Dependency Audit**: Run `safety check` to verify no known CVEs
4. **Data Validation**: Use Pydantic schemas for all external input

## Anti-Rationalization Table
| Agent Excuse | Response |
|---|---|
| "It's just a local script" | "All code is susceptible to scaling; security is non-negotiable" |
| "Inputs are trusted" | "Adopt Zero Trust; validate every byte" |
| "I'll add security later" | "Security at start, not end (Shift Left)" |

## OWASP Checklist
See `CHECKLIST.md` in the skill for:
- SQL/Command injection prevention
- Secrets management
- Input validation with Pydantic
- Secure logging (no PII)