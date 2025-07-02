# tajweed_rules.py
"""
Tajweed Rule Engine - Comprehensive
"""

# Example expanded Tajweed rules
TAJWEED_RULES = [
    {
        "name": "Ghunnah",
        "description": "Nasalization when ن or م is followed by certain letters (ي, و, م, ن)",
        "example": "مِنْ, أَمَّنْ",
        "trigger": "ن",
        "followed_by": ["ي", "و", "م", "ن"],
    },
    {
        "name": "Ikhfa",
        "description": "Concealment of ن when followed by specific letters (ت, ث, ج, د, ذ, ز, س, ش, ص, ض, ط, ظ, ف, ق, ك)",
        "example": "مِنْ ثَمَرَةٍ",
        "trigger": "ن",
        "followed_by": ["ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك"],
    },
    {
        "name": "Iqlab",
        "description": "Conversion of ن to م when followed by ب",
        "example": "مِن بَعْدِ",
        "trigger": "ن",
        "followed_by": ["ب"],
    },
    {
        "name": "Idgham with Ghunnah",
        "description": "Merging of ن with ي, ن, م, و with nasalization",
        "example": "مَن يَعْمَلْ",
        "trigger": "ن",
        "followed_by": ["ي", "ن", "م", "و"],
    },
    {
        "name": "Idgham without Ghunnah",
        "description": "Merging of ن with ل, ر without nasalization",
        "example": "مِن رَبِّهِمْ",
        "trigger": "ن",
        "followed_by": ["ل", "ر"],
    },
    {
        "name": "Qalqalah",
        "description": "Echoing sound on ق, ط, ب, ج, د when stopped",
        "example": "يَقْطَعُ",
        "trigger": None,
        "followed_by": ["ق", "ط", "ب", "ج", "د"],
    },
    # Add more rules as needed
]

def validate_tajweed(text):
    """
    Context-aware Tajweed validation.
    Returns a list of errors with their positions.
    """
    errors = []
    words = text.split()
    for w_idx, word in enumerate(words):
        for rule in TAJWEED_RULES:
            trigger = rule.get("trigger")
            followed_by = rule.get("followed_by", [])
            for i, char in enumerate(word):
                # Context-aware: check trigger and next letter
                if trigger and char == trigger and i+1 < len(word):
                    next_char = word[i+1]
                    if next_char in followed_by:
                        errors.append({
                            "rule": rule["name"],
                            "description": rule["description"],
                            "example": rule["example"],
                            "word_index": w_idx,
                            "char_index": i,
                            "message": f"Check Tajweed rule: {rule['name']} for '{char}{next_char}' in word '{word}'"
                        })
                # Qalqalah: check for stop on qalqalah letter
                elif not trigger and char in followed_by and i == len(word)-1:
                    errors.append({
                        "rule": rule["name"],
                        "description": rule["description"],
                        "example": rule["example"],
                        "word_index": w_idx,
                        "char_index": i,
                        "message": f"Check Tajweed rule: {rule['name']} for '{char}' at end of word '{word}'"
                    })
    return errors

def tajweed_feedback(text):
    """
    Generate feedback for Tajweed errors in the text.
    Returns feedback and error locations for highlighting.
    """
    errors = validate_tajweed(text)
    if not errors:
        return ["✅ No Tajweed errors detected!"], []
    feedback = []
    highlights = []
    for err in errors:
        feedback.append(f"❌ {err['message']} (e.g., {err['example']})")
        highlights.append((err['word_index'], err['char_index']))
    return feedback, highlights 