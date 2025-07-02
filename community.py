"""
Community & Social Features Module
"""
import sqlite3
import json

DB_PATH = 'users.db'

def share_progress(user_id, username, message, achievement):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO community_feed (user_id, username, message, achievement)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, message, achievement))
    conn.commit()
    conn.close()
    return True

def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Top by max accuracy
    cursor.execute('''
        SELECT u.username, MAX(CAST(json_extract(a.summary_stats, '$.accuracy_percentage') AS FLOAT)) as max_acc, MAX(m.streak) as max_streak
        FROM users u
        LEFT JOIN user_analyses a ON u.id = a.user_id
        LEFT JOIN user_memorization m ON u.id = m.user_id
        GROUP BY u.id
        ORDER BY max_acc DESC, max_streak DESC
        LIMIT 10
    ''')
    leaderboard = []
    for row in cursor.fetchall():
        username, max_acc, max_streak = row
        leaderboard.append({"username": username, "score": round(max_acc or 0, 1), "streak": max_streak or 0})
    conn.close()
    return leaderboard

def get_community_feed(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, message, achievement, date, likes FROM community_feed ORDER BY date DESC LIMIT ?
    ''', (limit,))
    feed = []
    for row in cursor.fetchall():
        username, message, achievement, date, likes = row
        feed.append({"username": username, "message": message, "achievement": achievement, "date": date, "likes": likes})
    conn.close()
    return feed 