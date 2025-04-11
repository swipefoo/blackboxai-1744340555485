# Arabic to Latin character mapping
ARABIC_TO_LATIN = {
    'ا': 'a',
    'ب': 'b',
    'ت': 't',
    'ث': 'th',
    'ج': 'j',
    'ح': 'h',
    'خ': 'kh',
    'د': 'd',
    'ذ': 'dh',
    'ر': 'r',
    'ز': 'z',
    'س': 's',
    'ش': 'sh',
    'ص': 's',
    'ض': 'd',
    'ط': 't',
    'ظ': 'dh',
    'ع': '3',
    'غ': 'gh',
    'ف': 'f',
    'ق': 'q',
    'ك': 'k',
    'ل': 'l',
    'م': 'm',
    'ن': 'n',
    'ه': 'h',
    'و': 'w',
    'ي': 'y',
    'ة': 'a',
    'ى': 'a',
    'ء': '\'',
    'ؤ': 'w',
    'ئ': 'y',
    'إ': 'i',
    'أ': 'a',
    'آ': 'aa',
}

# Create reverse mapping for Latin to Arabic
LATIN_TO_ARABIC = {v: k for k, v in ARABIC_TO_LATIN.items()}

def transliterate_to_latin(arabic_text):
    """
    Convert Arabic text to Latin script using common Darija transliteration.
    """
    if not arabic_text:
        return ""
    
    result = ""
    i = 0
    while i < len(arabic_text):
        char = arabic_text[i]
        # Handle special cases for two-character combinations
        if i + 1 < len(arabic_text) and char + arabic_text[i + 1] in ARABIC_TO_LATIN:
            result += ARABIC_TO_LATIN[char + arabic_text[i + 1]]
            i += 2
        # Handle single characters
        elif char in ARABIC_TO_LATIN:
            result += ARABIC_TO_LATIN[char]
            i += 1
        # Keep non-Arabic characters as is
        else:
            result += char
            i += 1
    
    return result

def transliterate_to_arabic(latin_text):
    """
    Convert Latin script to Arabic using common Darija transliteration.
    """
    if not latin_text:
        return ""
    
    result = ""
    i = 0
    while i < len(latin_text):
        # Try to match two characters first
        if i + 1 < len(latin_text):
            two_chars = latin_text[i:i+2].lower()
            if two_chars in LATIN_TO_ARABIC:
                result += LATIN_TO_ARABIC[two_chars]
                i += 2
                continue
        
        # If no two-character match, try single character
        char = latin_text[i].lower()
        if char in LATIN_TO_ARABIC:
            result += LATIN_TO_ARABIC[char]
        else:
            result += char
        i += 1
    
    return result
