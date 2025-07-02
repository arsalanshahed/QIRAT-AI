"""
Memorization Aid (Hifz) Module
"""
import sqlite3
import datetime

DB_PATH = 'users.db'

def spaced_repetition_schedule(user_id):
    # Placeholder: Return list of ayahs due for review today
    return [("Al-Fatiha", 1), ("Al-Baqarah", 255)]

def check_memorization(user_input, correct_text):
    # Compare user input to correct text, return score and feedback
    return {"score": 85, "missing_words": ["الرحيم"], "suggestion": "Review the last ayah."}

# SM2 algorithm for spaced repetition

def _sm2(ease_factor, interval, repetitions, quality):
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)
        repetitions += 1
    ease_factor = max(1.3, ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return interval, ease_factor, repetitions

def get_due_ayahs(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = datetime.datetime.now().date()
    cursor.execute('''
        SELECT surah, ayah, next_review, status FROM user_memorization
        WHERE user_id = ? AND (next_review IS NULL OR DATE(next_review) <= ?)
        ORDER BY next_review ASC
    ''', (user_id, today))
    results = cursor.fetchall()
    conn.close()
    return [(row[0], row[1], row[2], row[3]) for row in results]

def record_review(user_id, surah, ayah, quality):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT interval, ease_factor, repetitions, streak FROM user_memorization
        WHERE user_id = ? AND surah = ? AND ayah = ?
    ''', (user_id, surah, ayah))
    row = cursor.fetchone()
    if row:
        interval, ef, reps, streak = row
    else:
        interval, ef, reps, streak = 0, 2.5, 0, 0
    new_interval, new_ef, new_reps = _sm2(ef, interval, reps, quality)
    next_review = (datetime.datetime.now() + datetime.timedelta(days=new_interval)).isoformat()
    last_reviewed = datetime.datetime.now().isoformat()
    if quality >= 4:
        streak = (streak or 0) + 1
        status = 'mastered' if streak >= 7 else 'learning'
    else:
        streak = 0
        status = 'learning'
    cursor.execute('''
        INSERT INTO user_memorization (user_id, surah, ayah, last_reviewed, next_review, interval, ease_factor, repetitions, status, streak)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, surah, ayah) DO UPDATE SET
            last_reviewed=excluded.last_reviewed,
            next_review=excluded.next_review,
            interval=excluded.interval,
            ease_factor=excluded.ease_factor,
            repetitions=excluded.repetitions,
            status=excluded.status,
            streak=excluded.streak
    ''', (user_id, surah, ayah, last_reviewed, next_review, new_interval, new_ef, new_reps, status, streak))
    conn.commit()
    conn.close()
    return {'interval': new_interval, 'ease_factor': new_ef, 'repetitions': new_reps, 'streak': streak, 'status': status}

def get_streak(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT MAX(streak) FROM user_memorization WHERE user_id = ?''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] or 0 