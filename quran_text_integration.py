#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quran Text Integration Module
Integrates with Quran.com API for verse selection and text analysis
"""

import requests
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import sqlite3
from dataclasses import dataclass

# Import our enhanced modules
from tajweed_rules import EnhancedTajweedValidator, ArabicPhonemeDetector
from enhanced_pitch_analysis import ArabicPronunciationAnalyzer

@dataclass
class QuranVerse:
    """Data class for Quran verse information"""
    surah_number: int
    ayah_number: int
    text_arabic: str
    text_translation: str
    juz: int
    page: int
    sajda: bool = False
    ruku: int = 0
    hizb: int = 0

class QuranTextIntegration:
    """Quran text integration with API and local database"""
    
    def __init__(self, api_base_url: str = "https://api.quran.com/api/v4"):
        """
        Initialize Quran text integration
        
        Args:
            api_base_url: Base URL for Quran.com API
        """
        self.api_base_url = api_base_url
        self.tajweed_validator = EnhancedTajweedValidator()
        self.phoneme_detector = ArabicPhonemeDetector()
        self.pronunciation_analyzer = ArabicPronunciationAnalyzer()
        
        # Initialize local database
        self.db_path = "quran_data.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize local SQLite database for Quran data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS surahs (
                    number INTEGER PRIMARY KEY,
                    name_arabic TEXT,
                    name_english TEXT,
                    name_translation TEXT,
                    revelation_type TEXT,
                    ayahs_count INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verses (
                    id INTEGER PRIMARY KEY,
                    surah_number INTEGER,
                    ayah_number INTEGER,
                    text_arabic TEXT,
                    text_translation TEXT,
                    juz INTEGER,
                    page INTEGER,
                    sajda BOOLEAN,
                    ruku INTEGER,
                    hizb INTEGER,
                    FOREIGN KEY (surah_number) REFERENCES surahs (number)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tajweed_analysis (
                    id INTEGER PRIMARY KEY,
                    verse_id INTEGER,
                    analysis_data TEXT,
                    score INTEGER,
                    timestamp TEXT,
                    FOREIGN KEY (verse_id) REFERENCES verses (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Quran database initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
    
    def fetch_surah_list(self) -> List[Dict]:
        """Fetch list of all surahs from API"""
        try:
            url = f"{self.api_base_url}/chapters"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            surahs = data.get('chapters', [])
            
            # Store in local database
            self._store_surah_list(surahs)
            
            return surahs
            
        except Exception as e:
            print(f"❌ Error fetching surah list: {e}")
            return self._get_surah_list_from_db()
    
    def _store_surah_list(self, surahs: List[Dict]):
        """Store surah list in local database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for surah in surahs:
                cursor.execute('''
                    INSERT OR REPLACE INTO surahs 
                    (number, name_arabic, name_english, name_translation, revelation_type, ayahs_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    surah['id'],
                    surah['name_arabic'],
                    surah['name_english'],
                    surah['name_translation'],
                    surah['revelation_type'],
                    surah['verses_count']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing surah list: {e}")
    
    def _get_surah_list_from_db(self) -> List[Dict]:
        """Get surah list from local database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM surahs ORDER BY number')
            rows = cursor.fetchall()
            
            surahs = []
            for row in rows:
                surahs.append({
                    'id': row[0],
                    'name_arabic': row[1],
                    'name_english': row[2],
                    'name_translation': row[3],
                    'revelation_type': row[4],
                    'verses_count': row[5]
                })
            
            conn.close()
            return surahs
            
        except Exception as e:
            print(f"❌ Error getting surah list from DB: {e}")
            return []
    
    def fetch_verse(self, surah_number: int, ayah_number: int) -> Optional[QuranVerse]:
        """Fetch specific verse from API"""
        try:
            url = f"{self.api_base_url}/verses/by_key/{surah_number}:{ayah_number}"
            params = {
                'fields': 'text_arabic,text_translation,juz,page,sajda,ruku,hizb'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            verse_data = data.get('verse', {})
            
            verse = QuranVerse(
                surah_number=surah_number,
                ayah_number=ayah_number,
                text_arabic=verse_data.get('text_arabic', ''),
                text_translation=verse_data.get('text_translation', ''),
                juz=verse_data.get('juz', 0),
                page=verse_data.get('page', 0),
                sajda=verse_data.get('sajda', False),
                ruku=verse_data.get('ruku', 0),
                hizb=verse_data.get('hizb', 0)
            )
            
            # Store in local database
            self._store_verse(verse)
            
            return verse
            
        except Exception as e:
            print(f"❌ Error fetching verse {surah_number}:{ayah_number}: {e}")
            return self._get_verse_from_db(surah_number, ayah_number)
    
    def _store_verse(self, verse: QuranVerse):
        """Store verse in local database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO verses 
                (surah_number, ayah_number, text_arabic, text_translation, juz, page, sajda, ruku, hizb)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                verse.surah_number,
                verse.ayah_number,
                verse.text_arabic,
                verse.text_translation,
                verse.juz,
                verse.page,
                verse.sajda,
                verse.ruku,
                verse.hizb
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing verse: {e}")
    
    def _get_verse_from_db(self, surah_number: int, ayah_number: int) -> Optional[QuranVerse]:
        """Get verse from local database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM verses 
                WHERE surah_number = ? AND ayah_number = ?
            ''', (surah_number, ayah_number))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return QuranVerse(
                    surah_number=row[1],
                    ayah_number=row[2],
                    text_arabic=row[3],
                    text_translation=row[4],
                    juz=row[5],
                    page=row[6],
                    sajda=bool(row[7]),
                    ruku=row[8],
                    hizb=row[9]
                )
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting verse from DB: {e}")
            return None
    
    def fetch_verse_range(self, surah_number: int, start_ayah: int, end_ayah: int) -> List[QuranVerse]:
        """Fetch range of verses"""
        verses = []
        
        for ayah_number in range(start_ayah, end_ayah + 1):
            verse = self.fetch_verse(surah_number, ayah_number)
            if verse:
                verses.append(verse)
        
        return verses
    
    def search_verses(self, query: str, language: str = "ar") -> List[QuranVerse]:
        """Search verses by text"""
        try:
            url = f"{self.api_base_url}/search/{query}/{language}"
            params = {
                'size': 20,
                'page': 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            search_results = data.get('search', {}).get('results', [])
            
            verses = []
            for result in search_results:
                verse_key = result.get('verse_key', '')
                if ':' in verse_key:
                    surah_num, ayah_num = map(int, verse_key.split(':'))
                    verse = self.fetch_verse(surah_num, ayah_num)
                    if verse:
                        verses.append(verse)
            
            return verses
            
        except Exception as e:
            print(f"❌ Error searching verses: {e}")
            return []
    
    def analyze_verse_tajweed(self, verse: QuranVerse) -> Dict:
        """Analyze Tajweed for a specific verse"""
        
        # Analyze Arabic text
        tajweed_result = self.tajweed_validator.validate_text(verse.text_arabic)
        phonemes = self.phoneme_detector.extract_phonemes(verse.text_arabic)
        
        # Generate feedback
        feedback, highlights = self._generate_verse_feedback(tajweed_result, verse)
        
        analysis = {
            'verse_info': {
                'surah_number': verse.surah_number,
                'ayah_number': verse.ayah_number,
                'juz': verse.juz,
                'page': verse.page,
                'sajda': verse.sajda
            },
            'text_analysis': {
                'arabic_text': verse.text_arabic,
                'translation': verse.text_translation,
                'phonemes': phonemes,
                'total_phonemes': len(phonemes)
            },
            'tajweed_analysis': tajweed_result,
            'feedback': feedback,
            'highlights': highlights,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store analysis in database
        self._store_tajweed_analysis(verse, analysis)
        
        return analysis
    
    def _generate_verse_feedback(self, tajweed_result: Dict, verse: QuranVerse) -> Tuple[List[str], List[Tuple]]:
        """Generate feedback for verse analysis"""
        feedback = []
        highlights = []
        
        # Add verse information
        feedback.append(f"📖 Surah {verse.surah_number}, Ayah {verse.ayah_number}")
        feedback.append(f"📄 Page {verse.page}, Juz {verse.juz}")
        
        if verse.sajda:
            feedback.append("🕌 Sajda verse - prostration required")
        
        # Add Tajweed feedback
        if tajweed_result['score'] == 100:
            feedback.append("✅ Perfect Tajweed!")
        else:
            feedback.append(f"📚 Tajweed Score: {tajweed_result['score']}/100")
            for error in tajweed_result['errors']:
                feedback.append(f"⚠️ {error['rule']}: {error['message']}")
                highlights.append((error['word_index'], error['char_index']))
        
        # Add learning suggestions
        if tajweed_result['score'] < 90:
            feedback.append("💡 Practice this verse with focus on Tajweed rules")
        
        return feedback, highlights
    
    def _store_tajweed_analysis(self, verse: QuranVerse, analysis: Dict):
        """Store Tajweed analysis in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get verse ID
            cursor.execute('''
                SELECT id FROM verses 
                WHERE surah_number = ? AND ayah_number = ?
            ''', (verse.surah_number, verse.ayah_number))
            
            row = cursor.fetchone()
            if row:
                verse_id = row[0]
                
                cursor.execute('''
                    INSERT OR REPLACE INTO tajweed_analysis 
                    (verse_id, analysis_data, score, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    verse_id,
                    json.dumps(analysis, ensure_ascii=False),
                    analysis['tajweed_analysis']['score'],
                    analysis['timestamp']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing Tajweed analysis: {e}")
    
    def get_verse_statistics(self, surah_number: int) -> Dict:
        """Get statistics for a surah"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get verse count
            cursor.execute('''
                SELECT COUNT(*) FROM verses WHERE surah_number = ?
            ''', (surah_number,))
            
            verse_count = cursor.fetchone()[0]
            
            # Get average Tajweed score
            cursor.execute('''
                SELECT AVG(ta.score) FROM tajweed_analysis ta
                JOIN verses v ON ta.verse_id = v.id
                WHERE v.surah_number = ?
            ''', (surah_number,))
            
            avg_score = cursor.fetchone()[0] or 0
            
            # Get surah info
            cursor.execute('''
                SELECT name_arabic, name_english, revelation_type
                FROM surahs WHERE number = ?
            ''', (surah_number,))
            
            surah_info = cursor.fetchone()
            
            conn.close()
            
            return {
                'surah_number': surah_number,
                'name_arabic': surah_info[0] if surah_info else '',
                'name_english': surah_info[1] if surah_info else '',
                'revelation_type': surah_info[2] if surah_info else '',
                'verse_count': verse_count,
                'average_tajweed_score': round(avg_score, 2)
            }
            
        except Exception as e:
            print(f"❌ Error getting verse statistics: {e}")
            return {}
    
    def compare_verses(self, verse1: QuranVerse, verse2: QuranVerse) -> Dict:
        """Compare two verses for analysis"""
        
        analysis1 = self.analyze_verse_tajweed(verse1)
        analysis2 = self.analyze_verse_tajweed(verse2)
        
        comparison = {
            'verse1': {
                'info': analysis1['verse_info'],
                'tajweed_score': analysis1['tajweed_analysis']['score'],
                'phoneme_count': analysis1['text_analysis']['total_phonemes']
            },
            'verse2': {
                'info': analysis2['verse_info'],
                'tajweed_score': analysis2['tajweed_analysis']['score'],
                'phoneme_count': analysis2['text_analysis']['total_phonemes']
            },
            'comparison': {
                'score_difference': analysis1['tajweed_analysis']['score'] - analysis2['tajweed_analysis']['score'],
                'phoneme_difference': analysis1['text_analysis']['total_phonemes'] - analysis2['text_analysis']['total_phonemes'],
                'complexity_ratio': analysis1['text_analysis']['total_phonemes'] / analysis2['text_analysis']['total_phonemes'] if analysis2['text_analysis']['total_phonemes'] > 0 else 0
            }
        }
        
        return comparison
    
    def get_recommended_verses(self, difficulty_level: str = "beginner") -> List[QuranVerse]:
        """Get recommended verses based on difficulty level"""
        
        # Define difficulty criteria
        difficulty_criteria = {
            "beginner": {
                "max_phonemes": 50,
                "min_score": 80,
                "max_ayah_length": 100
            },
            "intermediate": {
                "max_phonemes": 100,
                "min_score": 70,
                "max_ayah_length": 200
            },
            "advanced": {
                "max_phonemes": 200,
                "min_score": 60,
                "max_ayah_length": 500
            }
        }
        
        criteria = difficulty_criteria.get(difficulty_level, difficulty_criteria["beginner"])
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get verses matching criteria
            cursor.execute('''
                SELECT v.*, ta.score 
                FROM verses v
                LEFT JOIN tajweed_analysis ta ON v.id = ta.verse_id
                WHERE LENGTH(v.text_arabic) <= ?
                AND (ta.score IS NULL OR ta.score >= ?)
                ORDER BY RANDOM()
                LIMIT 10
            ''', (criteria['max_ayah_length'], criteria['min_score']))
            
            rows = cursor.fetchall()
            conn.close()
            
            verses = []
            for row in rows:
                verse = QuranVerse(
                    surah_number=row[1],
                    ayah_number=row[2],
                    text_arabic=row[3],
                    text_translation=row[4],
                    juz=row[5],
                    page=row[6],
                    sajda=bool(row[7]),
                    ruku=row[8],
                    hizb=row[9]
                )
                verses.append(verse)
            
            return verses
            
        except Exception as e:
            print(f"❌ Error getting recommended verses: {e}")
            return []

def main():
    """Demo function for Quran text integration"""
    print("📖 Quran Text Integration Demo")
    print("=" * 50)
    
    # Initialize integration
    quran = QuranTextIntegration()
    
    # Fetch surah list
    print("\n📋 Fetching surah list...")
    surahs = quran.fetch_surah_list()
    print(f"Found {len(surahs)} surahs")
    
    # Show first few surahs
    for surah in surahs[:5]:
        print(f"  {surah['id']}. {surah['name_arabic']} ({surah['name_english']})")
    
    # Fetch and analyze a verse
    print("\n🔍 Analyzing a verse...")
    verse = quran.fetch_verse(1, 1)  # Al-Fatiha, verse 1
    
    if verse:
        print(f"Verse: {verse.text_arabic}")
        print(f"Translation: {verse.text_translation}")
        
        # Analyze Tajweed
        analysis = quran.analyze_verse_tajweed(verse)
        print(f"Tajweed Score: {analysis['tajweed_analysis']['score']}/100")
        
        # Show feedback
        print("\nFeedback:")
        for feedback in analysis['feedback']:
            print(f"  {feedback}")
    
    # Get recommended verses
    print("\n💡 Getting recommended verses...")
    recommended = quran.get_recommended_verses("beginner")
    print(f"Found {len(recommended)} recommended verses for beginners")
    
    for verse in recommended[:3]:
        print(f"  {verse.surah_number}:{verse.ayah_number} - {verse.text_arabic[:30]}...")

if __name__ == "__main__":
    main() 