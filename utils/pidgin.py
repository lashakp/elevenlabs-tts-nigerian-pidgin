from typing import List, Tuple
from utils.constants import REPLACEMENTS
import re

def stylize_pidgin(text: str, custom_replacements: List[Tuple[str, str]] = []) -> str:
    all_replacements = dict(REPLACEMENTS + custom_replacements)
    sorted_replacements = sorted(all_replacements.items(), key=lambda x: -len(x[0]))

    for eng, pidgin in sorted_replacements:
        pattern = re.compile(r'\b' + re.escape(eng) + r'\b', re.IGNORECASE)
        
        def replace(match):
            original = match.group(0)
            if original.isupper():
                return pidgin.upper()
            elif original[0].isupper() and original[1:].islower():
                words = pidgin.split()
                words[0] = words[0].capitalize()
                return " ".join(words)
            else:
                return pidgin.lower()
        
        text = pattern.sub(replace, text)
    
    return text
