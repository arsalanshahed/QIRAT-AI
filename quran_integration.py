# quran_integration.py
"""
Quran Text Integration - Enhanced
"""
import requests

QURAN_API_URL = "https://api.quran.com/api/v4/"

# Fetch all surah metadata (names, ayah counts)
def fetch_surah_list():
    url = f"{QURAN_API_URL}chapters?language=en"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("chapters", [])
    return []

def fetch_surah_ayah_count(surah_number):
    surahs = fetch_surah_list()
    for surah in surahs:
        if surah["id"] == surah_number:
            return surah["verses_count"]
    return 7  # Default to 7 (Al-Fatiha) if not found

def fetch_surah(surah_number):
    """
    Fetch all ayahs of a surah from Quran.com API.
    Returns a list of ayah dicts.
    """
    url = f"{QURAN_API_URL}quran/verses/uthmani?chapter_number={surah_number}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("verses", [])
    return []

def fetch_ayah(surah_number, ayah_number):
    """
    Fetch a specific ayah from Quran.com API.
    Returns the ayah text.
    """
    verses = fetch_surah(surah_number)
    for verse in verses:
        if verse.get("verse_number") == ayah_number:
            return verse.get("text_uthmani", "")
    return ""

def get_verse_text(surah_number, ayah_number):
    """
    Get the text of a specific verse (surah:ayah).
    """
    return fetch_ayah(surah_number, ayah_number)

# Fetch English translation for a verse
def fetch_ayah_translation(surah_number, ayah_number, translation_id=131):
    # 131 = Saheeh International
    url = f"{QURAN_API_URL}quran/translations/{translation_id}?verse_key={surah_number}:{ayah_number}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        translations = data.get("translations", [])
        if translations:
            return translations[0].get("text", "")
    return "" 