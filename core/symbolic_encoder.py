import re

def apply_symbolic_mapping(text):
    """
    Sustituye palabras comunes por operadores lógicos y símbolos 
    para reducir tokens antes del procesamiento del LLM.
    """
    mappings = {
        r'\buna\b': '1', r'\bun\b': '1',
        r'\bdos\b': '2',
        r'\btres\b': '3',
        r'\bcuatro\b': '4',
        r'\bcinco\b': '5',
        r'\bseis\b': '6',
        r'\bsiete\b': '7',
        r'\bocho\b': '8',
        r'\bnueve\b': '9',
        r'\bdiez\b': '10',
        r'\bcien\b': '100',
        r'\bmil\b': 'k',
        r'\bmillón\b': 'M',
        r'\bdiez mil\b': '10k',
        r'\bun millón\b': '1M',
        r'\by\b': '&', r'\btambién\b': '&',
        r'\bcon\b': 'w/',
        r'\bpara\b': '->',
        r'\bpor\b': '∋',
        r'\bentonces\b': '=>',
        r'\bsi\b': '?',
        r'\bno\b': '!',
        r'\bsin\b': '¬',
        r'\ben\b': '@',
        r'\bde\b': ':',
        r'\bdel\b': ':',
        r'\bde la\b': ':',
        r'\bdel\b': ':',
        r'\bcada\b': '∀', r'\btodos\b': '∀',
        r'\balgunos\b': '∃', r'\bexiste\b': '∃',
        r'\bpor ejemplo\b': 'e.g.', r'\bpor ej\b': 'e.g.',
        r'\bes decir\b': 'i.e.', r'\bsea\b': 'i.e.',
        r'\bigual a\b': '=', r'\biguales\b': '=',
        r'\bdiferente de\b': '!=', r'\bdiferentes\b': '!=',
        r'\bmayor que\b': '>', r'\bmayores\b': '>',
        r'\bmenor que\b': '<', r'\bmenores\b': '<',
        r'\bpero\b': '^',
        r'\bo\b': '|', r'\bu\b': '|',
        r'\bcomo\b': '~',
        r'\bcuando\b': '∇',
        r'\bantes\b': '←', r'\bantes de\b': '←',
        r'\bdespués\b': '→', r'\bdespués de\b': '→',
        r'\bentre\b': '⊂',
        r'\bsobre\b': '⊃',
        r'\bcontra\b': '≠',
        r'\bhacia\b': '→',
        r'\bhasta\b': '→',
        r'\bdesde\b': '←',
        r'\bacause\b': '∵',
        r'\bporque\b': '∵',
        r'\basi\b': '∴',
        r'\basí\b': '∴',
        r'\bpor lo tanto\b': '∴',
        r'\bademás\b': '+',
        r'\bmás\b': '+',
        r'\bmenos\b': '-',
        r'\bvez\b': '×',
        r'\btambi[eé]n\b': '+',
        r'\bal menos\b': '≥',
        r'\bmas\b': '+',
        r'\bmejor\b': '↑',
        r'\bpeor\b': '↓',
        r'\bfalta\b': '⊥',
        r'\bhay\b': '∃',
        r'\btenemos\b': '∋',
        r'\btener\b': '∋',
        r'\bser\b': '≡',
        r'\bestar\b': '≈',
    }
    
    for pattern, symbol in mappings.items():
        text = re.sub(pattern, symbol, text, flags=re.IGNORECASE)
    
    text = " ".join(text.split())
    
    return text