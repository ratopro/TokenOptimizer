import re

def apply_symbolic_mapping(text):
    """
    Sustituye palabras comunes por operadores lógicos y símbolos 
    para reducir tokens antes del procesamiento del LLM.
    """
    mappings = {
        r'\buna\b': '1',
        r'\bdos\b': '2',
        r'\btres\b': '3',
        r'\bcuatro\b': '4',
        r'\bcinco\b': '5',
        r'\bdiez mil\b': '10k',
        r'\bun millón\b': '1M',
        r'\by\b': '&',
        r'\bcon\b': 'w/',
        r'\bpara\b': '->',
        r'\bentonces\b': '=>',
        r'\bsi\b': '?',
        r'\bno\b': '!',
        r'\ben\b': '@',
        r'\bcada\b': '∀',
        r'\btodos\b': '∀',
        r'\balgunos\b': '∃',
        r'\bexiste\b': '∃',
        r'\bpor ejemplo\b': 'e.g.',
        r'\bes decir\b': 'i.e.',
        r'\bigual a\b': '=',
        r'\bdiferente de\b': '!=',
        r'\bmayor que\b': '>',
        r'\bmenor que\b': '<',
        r'\bpero\b': '^',
        r'\bo\b': '|',
        r'\bcomo\b': '~',
        r'\bcuando\b': '∇',
        r'\bantes\b': '←',
        r'\bdespués\b': '→',
        r'\bantes de\b': '←',
        r'\bdespués de\b': '→',
        r'\bentre\b': '⊂',
        r'\bsobre\b': '⊃',
        r'\bcontra\b': '≠',
        r'\bhacia\b': '→',
    }
    
    for pattern, symbol in mappings.items():
        text = re.sub(pattern, symbol, text, flags=re.IGNORECASE)
    
    text = " ".join(text.split())
    
    return text