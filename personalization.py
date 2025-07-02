"""
Personalization & Gamification Module
"""
import sqlite3
import datetime
import json

DB_PATH = 'users.db'

def recommend_next_practice(user_id):
    # Suggest weakest Tajweed rule or least practiced ayah
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Find ayah with lowest accuracy
    cursor.execute('''SELECT reference_file, summary_stats FROM user_analyses WHERE user_id = ?''', (user_id,))
    min_acc = 100
    min_ayah = None
    for ref, stats in cursor.fetchall():
        try:
            acc = json.loads(stats).get('accuracy_percentage', 100)
            if acc < min_acc:
                min_acc = acc
                min_ayah = ref
        except:
            continue
    conn.close()
    if min_ayah:
        return {"suggestion": f"Focus on improving {min_ayah} (lowest accuracy: {min_acc:.1f}%)"}
    return {"suggestion": "Practice a new ayah or review your weakest area!"}

def get_achievements(user_id):
    # Return list of earned badges/achievements
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    badges = []
    # Tajweed Master: >95% accuracy in any ayah
    cursor.execute('''SELECT summary_stats FROM user_analyses WHERE user_id = ?''', (user_id,))
    for stats, in cursor.fetchall():
        try:
            acc = json.loads(stats).get('accuracy_percentage', 0)
            if acc >= 95:
                badges.append("Tajweed Master")
                break
        except:
            continue
    # 7-Day Streak: streak >= 7 in user_memorization
    cursor.execute('''SELECT MAX(streak) FROM user_memorization WHERE user_id = ?''', (user_id,))
    row = cursor.fetchone()
    if row and row[0] and row[0] >= 7:
        badges.append("7-Day Streak")
    conn.close()
    return badges or ["Getting Started"]

def get_streak(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT MAX(streak) FROM user_memorization WHERE user_id = ?''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] or 0

def get_progress_analytics(user_id):
    # Return dates and accuracy for progress chart
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT analysis_date, summary_stats FROM user_analyses WHERE user_id = ? ORDER BY analysis_date ASC''', (user_id,))
    dates = []
    scores = []
    for date, stats in cursor.fetchall():
        try:
            acc = json.loads(stats).get('accuracy_percentage', None)
            if acc is not None:
                dates.append(date[:10])
                scores.append(acc)
        except:
            continue
    conn.close()
    return dates, scores 