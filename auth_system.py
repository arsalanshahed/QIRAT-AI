#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QIRAT AI Authentication System
User authentication, registration, and data persistence
"""

import streamlit as st
import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from datetime import datetime, timedelta
import uuid

class AuthSystem:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User analysis data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reference_file TEXT,
                user_file TEXT,
                analysis_data TEXT,  -- JSON data
                summary_stats TEXT,  -- JSON data
                segments_data TEXT,  -- JSON data for 5s segments
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User memorization table for spaced repetition
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_memorization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                surah INTEGER,
                ayah INTEGER,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                interval INTEGER,
                ease_factor REAL,
                repetitions INTEGER,
                status TEXT,
                streak INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Community feed table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_feed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message TEXT,
                achievement TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password, password_hash, salt):
        """Verify password against stored hash"""
        test_hash, _ = self.hash_password(password, salt)
        return test_hash == password_hash
    
    def register_user(self, username, email, password):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return False, "Username or email already exists"
            
            # Hash password
            password_hash, salt = self.hash_password(password)
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, salt)
            )
            
            conn.commit()
            conn.close()
            return True, "Registration successful"
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username, password):
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user data
            cursor.execute("SELECT id, username, email, password_hash, salt FROM users WHERE username = ? AND is_active = 1", (username,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return False, "Invalid username or password"
            
            user_id, username, email, password_hash, salt = user_data
            
            # Verify password
            if not self.verify_password(password, password_hash, salt):
                return False, "Invalid username or password"
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            return True, {"user_id": user_id, "username": username, "email": email}
            
        except Exception as e:
            return False, f"Login failed: {str(e)}"
    
    def create_reset_token(self, email):
        """Create password reset token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user by email
            cursor.execute("SELECT id, username FROM users WHERE email = ? AND is_active = 1", (email,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return False, "Email not found"
            
            user_id, username = user_data
            
            # Generate token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            # Store token
            cursor.execute(
                "INSERT INTO reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, token, expires_at)
            )
            
            conn.commit()
            conn.close()
            
            return True, {"token": token, "username": username, "expires_at": expires_at}
            
        except Exception as e:
            return False, f"Token creation failed: {str(e)}"
    
    def reset_password(self, token, new_password):
        """Reset password using token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get token data
            cursor.execute(
                "SELECT user_id, expires_at, used FROM reset_tokens WHERE token = ?",
                (token,)
            )
            token_data = cursor.fetchone()
            
            if not token_data:
                return False, "Invalid token"
            
            user_id, expires_at, used = token_data
            
            # Check if token is expired or used
            if used or datetime.fromisoformat(expires_at) < datetime.now():
                return False, "Token expired or already used"
            
            # Hash new password
            password_hash, salt = self.hash_password(new_password)
            
            # Update password
            cursor.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (password_hash, salt, user_id)
            )
            
            # Mark token as used
            cursor.execute("UPDATE reset_tokens SET used = 1 WHERE token = ?", (token,))
            
            conn.commit()
            conn.close()
            
            return True, "Password reset successful"
            
        except Exception as e:
            return False, f"Password reset failed: {str(e)}"
    
    def save_analysis_data(self, user_id, reference_file, user_file, analysis_data, summary_stats, segments_data):
        """Save analysis data for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO user_analyses 
                   (user_id, reference_file, user_file, analysis_data, summary_stats, segments_data)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, reference_file, user_file, 
                 json.dumps(analysis_data), json.dumps(summary_stats), json.dumps(segments_data))
            )
            
            conn.commit()
            conn.close()
            return True, "Analysis data saved successfully"
            
        except Exception as e:
            return False, f"Failed to save analysis data: {str(e)}"
    
    def get_user_analyses(self, user_id, limit=10):
        """Get user's analysis history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT id, analysis_date, reference_file, user_file, summary_stats, segments_data
                   FROM user_analyses 
                   WHERE user_id = ? 
                   ORDER BY analysis_date DESC 
                   LIMIT ?""",
                (user_id, limit)
            )
            
            analyses = []
            for row in cursor.fetchall():
                analysis_id, analysis_date, ref_file, user_file, summary_stats, segments_data = row
                analyses.append({
                    'id': analysis_id,
                    'date': analysis_date,
                    'reference_file': ref_file,
                    'user_file': user_file,
                    'summary_stats': json.loads(summary_stats) if summary_stats else {},
                    'segments_data': json.loads(segments_data) if segments_data else {}
                })
            
            conn.close()
            return True, analyses
            
        except Exception as e:
            return False, f"Failed to retrieve analyses: {str(e)}"
    
    def get_analysis_by_id(self, analysis_id, user_id):
        """Get specific analysis by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT analysis_data, summary_stats, segments_data
                   FROM user_analyses 
                   WHERE id = ? AND user_id = ?""",
                (analysis_id, user_id)
            )
            
            row = cursor.fetchone()
            if not row:
                return False, "Analysis not found"
            
            analysis_data, summary_stats, segments_data = row
            
            conn.close()
            return True, {
                'analysis_data': json.loads(analysis_data) if analysis_data else {},
                'summary_stats': json.loads(summary_stats) if summary_stats else {},
                'segments_data': json.loads(segments_data) if segments_data else {}
            }
            
        except Exception as e:
            return False, f"Failed to retrieve analysis: {str(e)}"

# Email configuration (you'll need to set these up)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': os.getenv('EMAIL_USER', 'your-email@gmail.com'),
    'sender_password': os.getenv('EMAIL_PASSWORD', 'your-app-password')
}

def send_reset_email(email, token, username):
    """Send password reset email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = email
        msg['Subject'] = "QIRAT AI - Password Reset Request"
        
        reset_url = f"https://your-domain.com/reset?token={token}"
        
        body = f"""
        Hello {username},
        
        You have requested a password reset for your QIRAT AI account.
        
        Click the following link to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        QIRAT AI Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], email, text)
        server.quit()
        
        return True, "Reset email sent successfully"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# Streamlit authentication functions
def show_login_page():
    """Display login page"""
    st.title("🔐 QIRAT AI - Login")
    
    auth_system = AuthSystem()
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                success, result = auth_system.login_user(username, password)
                if success:
                    st.session_state['authenticated'] = True
                    st.session_state['user_data'] = result
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.error("Please fill in all fields")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register New Account"):
            st.session_state['show_register'] = True
            st.rerun()
    
    with col2:
        if st.button("Forgot Password?"):
            st.session_state['show_forgot_password'] = True
            st.rerun()

def show_register_page():
    """Display registration page"""
    st.title("📝 QIRAT AI - Register")
    
    auth_system = AuthSystem()
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    success, result = auth_system.register_user(username, email, password)
                    if success:
                        st.success("Registration successful! Please login.")
                        st.session_state['show_register'] = False
                        st.rerun()
                    else:
                        st.error(result)
            else:
                st.error("Please fill in all fields")
    
    if st.button("Back to Login"):
        st.session_state['show_register'] = False
        st.rerun()

def show_forgot_password_page():
    """Display forgot password page"""
    st.title("🔑 QIRAT AI - Forgot Password")
    
    auth_system = AuthSystem()
    
    with st.form("forgot_password_form"):
        email = st.text_input("Email")
        submit_button = st.form_submit_button("Send Reset Link")
        
        if submit_button:
            if email:
                success, result = auth_system.create_reset_token(email)
                if success:
                    # In a real application, you would send the email here
                    # For demo purposes, we'll just show the token
                    st.success(f"Reset token created: {result['token']}")
                    st.info("In a real application, this token would be sent via email.")
                else:
                    st.error(result)
            else:
                st.error("Please enter your email")
    
    if st.button("Back to Login"):
        st.session_state['show_forgot_password'] = False
        st.rerun()

def show_reset_password_page(token):
    """Display password reset page"""
    st.title("🔑 QIRAT AI - Reset Password")
    
    auth_system = AuthSystem()
    
    with st.form("reset_password_form"):
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submit_button = st.form_submit_button("Reset Password")
        
        if submit_button:
            if new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    success, result = auth_system.reset_password(token, new_password)
                    if success:
                        st.success("Password reset successful! Please login.")
                        st.rerun()
                    else:
                        st.error(result)
            else:
                st.error("Please fill in all fields")

def logout():
    """Logout user"""
    if 'authenticated' in st.session_state:
        del st.session_state['authenticated']
    if 'user_data' in st.session_state:
        del st.session_state['user_data']
    st.rerun() 