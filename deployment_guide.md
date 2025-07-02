# QIRAT AI Enhanced Deployment Guide

## Overview
This guide covers deploying the enhanced QIRAT AI system with user authentication and 5-second segment analysis to the internet.

## New Features Added

### 1. 5-Second Segment Analysis
- **Replaces**: Individual 0.n second pitch differences
- **New Approach**: Analyzes audio in 5-second segments
- **Benefits**: 
  - Focuses on major pitch differences only
  - Reduces noise from minor variations
  - Provides more actionable feedback
  - Easier to practice specific segments

### 2. User Authentication System
- **User Registration**: Create accounts with username, email, and password
- **Secure Login**: Password hashing with salt
- **Password Reset**: Forgot password functionality with email tokens
- **Data Persistence**: User analysis history stored in SQLite database
- **Session Management**: Secure user sessions

### 3. Enhanced User Experience
- **Analysis History**: View previous analyses
- **Personalized Dashboard**: User-specific settings and recommendations
- **Data Export**: Download analysis reports and audio segments
- **Progress Tracking**: Monitor improvement over time

## Deployment Options

### Option 1: Streamlit Cloud (Recommended)

#### Prerequisites
1. GitHub account
2. Streamlit Cloud account (free)

#### Steps
1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Enhanced QIRAT AI"
   git branch -M main
   git remote add origin https://github.com/yourusername/qirat-ai-enhanced.git
   git push -u origin main
   ```

2. **Configure Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `enhanced_frontend.py`
   - Deploy

3. **Environment Variables** (Optional for email functionality)
   ```bash
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```

### Option 2: Heroku

#### Prerequisites
1. Heroku account
2. Heroku CLI installed

#### Steps
1. **Create Procfile**
   ```
   web: streamlit run enhanced_frontend.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create runtime.txt**
   ```
   python-3.11.0
   ```

3. **Deploy to Heroku**
   ```bash
   heroku create qirat-ai-enhanced
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 3: DigitalOcean App Platform

#### Steps
1. **Create app.yaml**
   ```yaml
   name: qirat-ai-enhanced
   services:
   - name: web
     source_dir: /
     github:
       repo: yourusername/qirat-ai-enhanced
       branch: main
     run_command: streamlit run enhanced_frontend.py --server.port=$PORT --server.address=0.0.0.0
     environment_slug: python
   ```

2. **Deploy via DigitalOcean Dashboard**

### Option 4: AWS EC2

#### Steps
1. **Launch EC2 Instance**
   - Ubuntu 20.04 LTS
   - t3.medium or larger
   - Security group with ports 22, 80, 443, 8501

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```

3. **Setup Application**
   ```bash
   git clone https://github.com/yourusername/qirat-ai-enhanced.git
   cd qirat-ai-enhanced
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements_enhanced.txt
   ```

4. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Run Application**
   ```bash
   streamlit run enhanced_frontend.py --server.port=8501 --server.address=0.0.0.0
   ```

## Database Setup

### SQLite (Default)
- Automatically created on first run
- File: `users.db`
- Tables: `users`, `reset_tokens`, `user_analyses`

### PostgreSQL (Production)
1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE qirat_ai;
   CREATE USER qirat_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE qirat_ai TO qirat_user;
   ```

3. **Update Database Configuration**
   ```python
   # In auth_system.py, change:
   self.db_path = "postgresql://qirat_user:your_password@localhost/qirat_ai"
   ```

## Email Configuration

### Gmail Setup
1. **Enable 2-Factor Authentication**
2. **Generate App Password**
3. **Set Environment Variables**
   ```bash
   export EMAIL_USER=your-email@gmail.com
   export EMAIL_PASSWORD=your-app-password
   ```

### Custom SMTP Server
```python
EMAIL_CONFIG = {
    'smtp_server': 'your-smtp-server.com',
    'smtp_port': 587,
    'sender_email': 'noreply@yourdomain.com',
    'sender_password': 'your-password'
}
```

## Security Considerations

### 1. Password Security
- Passwords are hashed using PBKDF2 with salt
- Minimum 8 characters required
- Secure password reset tokens

### 2. Data Protection
- User data stored securely in database
- Analysis files cleaned up after processing
- No sensitive data logged

### 3. HTTPS
- Enable HTTPS in production
- Use SSL certificates (Let's Encrypt)

### 4. Rate Limiting
- Implement rate limiting for login attempts
- Add CAPTCHA for registration

## Monitoring and Maintenance

### 1. Logs
```bash
# Streamlit logs
streamlit run enhanced_frontend.py --logger.level=info

# Application logs
tail -f /var/log/qirat-ai/app.log
```

### 2. Database Backup
```bash
# SQLite backup
cp users.db users_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump qirat_ai > backup_$(date +%Y%m%d).sql
```

### 3. Performance Monitoring
- Monitor CPU and memory usage
- Track user sessions and analysis requests
- Set up alerts for system issues

## Troubleshooting

### Common Issues

1. **Audio Processing Errors**
   - Check FFmpeg installation
   - Verify audio file formats
   - Monitor memory usage

2. **Database Connection Issues**
   - Verify database file permissions
   - Check database schema
   - Test database connectivity

3. **Email Not Sending**
   - Verify SMTP settings
   - Check firewall rules
   - Test email credentials

4. **Performance Issues**
   - Optimize audio processing
   - Implement caching
   - Scale resources

### Support
- Check application logs
- Monitor system resources
- Review error messages
- Test with different audio files

## Future Enhancements

### Planned Features
1. **Real-time Analysis**: Live pitch feedback during recording
2. **Advanced Analytics**: Progress tracking and improvement metrics
3. **Social Features**: Share analyses and compare with others
4. **Mobile App**: Native mobile application
5. **API Access**: REST API for third-party integrations

### Scalability Improvements
1. **Microservices**: Separate authentication and analysis services
2. **Load Balancing**: Distribute traffic across multiple instances
3. **Caching**: Redis for session and analysis caching
4. **CDN**: Content delivery network for static assets

## Conclusion

The enhanced QIRAT AI system provides a robust, scalable solution for pitch analysis with user authentication and 5-second segment analysis. Follow this guide to deploy successfully and maintain the application in production. 