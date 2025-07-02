# QIRAT AI Enhanced - Advanced Pitch Analysis System

## 🎵 Overview

QIRAT AI Enhanced is a sophisticated pitch analysis system that provides detailed 5-second segment analysis with user authentication and data persistence. This system helps users improve their singing by comparing their audio recordings with reference tracks and identifying major pitch differences.

## ✨ Key Features

### 🔐 User Authentication System
- **Secure Registration**: Create accounts with username, email, and password
- **Password Security**: PBKDF2 hashing with salt for maximum security
- **Password Reset**: Forgot password functionality with email tokens
- **Session Management**: Secure user sessions with automatic logout

### 🎯 5-Second Segment Analysis
- **Major Differences Focus**: Analyzes audio in 5-second segments instead of individual frames
- **Reduced Noise**: Filters out minor pitch variations to focus on significant issues
- **Actionable Feedback**: Provides specific recommendations for each problematic segment
- **Practice-Friendly**: Easy to practice specific 5-second segments

### 📊 Enhanced Analytics
- **Segment-by-Segment Analysis**: Detailed breakdown of each 5-second interval
- **Visualizations**: Interactive charts showing accuracy and deviation by segment
- **Progress Tracking**: Monitor improvement over time with analysis history
- **Export Capabilities**: Download analysis reports and audio segments

### 🎧 Multiple Audio Sources
- **File Upload**: Upload reference and user audio files
- **URL Download**: Download audio from direct links
- **YouTube Integration**: Extract audio from YouTube videos
- **Live Recording**: Record audio directly in the browser

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- FFmpeg (for audio processing)
- Internet connection (for YouTube downloads)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/qirat-ai-enhanced.git
   cd qirat-ai-enhanced
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_enhanced.txt
   ```

3. **Run the application**
   ```bash
   streamlit run enhanced_frontend.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## 📁 Project Structure

```
qirat-ai-enhanced/
├── enhanced_frontend.py      # Main Streamlit application
├── auth_system.py           # User authentication system
├── enhanced_pitch_analysis.py # 5-second segment analysis
├── requirements_enhanced.txt # Python dependencies
├── deployment_guide.md      # Deployment instructions
├── test_enhanced_system.py  # Test suite
├── README_ENHANCED.md       # This file
└── users.db                 # SQLite database (created automatically)
```

## 🔧 How It Works

### 1. User Authentication
- Users register with username, email, and password
- Passwords are securely hashed using PBKDF2 with salt
- Login sessions are managed securely
- Password reset functionality with email tokens

### 2. Audio Processing
- Audio files are aligned by detecting the first word/sound
- Both reference and user audio are segmented into 5-second intervals
- Pitch contours are extracted using librosa's piptrack
- Each segment is analyzed independently

### 3. 5-Second Segment Analysis
- **Segmentation**: Audio is divided into 5-second chunks
- **Pitch Extraction**: Pitch contours are extracted for each segment
- **Difference Detection**: Major pitch differences (>50Hz by default) are identified
- **Statistics Calculation**: Comprehensive metrics for each segment
- **Feedback Generation**: Actionable recommendations based on analysis

### 4. Data Persistence
- Analysis results are stored in SQLite database
- Users can view their analysis history
- Previous analyses can be retrieved and compared
- Data is associated with user accounts

## 🎯 Analysis Features

### Segment Statistics
- **Average Deviation**: Mean pitch difference in Hz
- **Accuracy Percentage**: Percentage of frames within threshold
- **High/Low Pitch Count**: Number of frames above/below reference
- **Maximum Deviation**: Largest pitch difference detected
- **Standard Deviation**: Consistency of pitch accuracy

### Visualizations
- **Segment Accuracy Chart**: Bar chart showing accuracy by segment
- **Pitch Deviation Chart**: Average deviation for each segment
- **Pitch Contour Comparison**: Overlay of user vs reference pitch
- **Color-Coded Segments**: Green (good), Orange (moderate), Red (poor)

### Feedback System
- **Overall Summary**: General performance assessment
- **Segment-Specific Feedback**: Detailed analysis of each 5-second segment
- **Recommendations**: Actionable advice for improvement
- **Practice Suggestions**: Focus on worst-performing segments

## 🔐 Security Features

### Password Security
- **PBKDF2 Hashing**: Industry-standard password hashing
- **Salt Generation**: Unique salt for each password
- **Minimum Requirements**: 8+ characters required
- **Secure Storage**: Passwords never stored in plain text

### Session Management
- **Secure Sessions**: Session state management
- **Automatic Logout**: Session timeout functionality
- **User Isolation**: Users can only access their own data
- **Token Expiration**: Password reset tokens expire after 24 hours

### Data Protection
- **SQLite Database**: Local data storage
- **User Isolation**: Data separated by user ID
- **Secure Queries**: Parameterized queries prevent SQL injection
- **File Cleanup**: Temporary files automatically removed

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### Reset Tokens Table
```sql
CREATE TABLE reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### User Analyses Table
```sql
CREATE TABLE user_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reference_file TEXT,
    user_file TEXT,
    analysis_data TEXT,  -- JSON data
    summary_stats TEXT,  -- JSON data
    segments_data TEXT,  -- JSON data for 5s segments
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_enhanced_system.py
```

The test suite covers:
- ✅ User authentication (registration, login, password reset)
- ✅ 5-second segment analysis
- ✅ Data persistence and retrieval
- ✅ Audio processing and pitch extraction

## 🚀 Deployment

### Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Set main file to `enhanced_frontend.py`
4. Deploy

### Other Platforms
See `deployment_guide.md` for detailed instructions on:
- Heroku deployment
- DigitalOcean App Platform
- AWS EC2 setup
- Docker containerization

## 🔧 Configuration

### Environment Variables
```bash
# Email configuration (optional)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Database configuration
DATABASE_URL=sqlite:///users.db  # Default
# DATABASE_URL=postgresql://user:pass@localhost/db  # Production
```

### Customization
- **Feedback Threshold**: Adjust sensitivity (10-100 Hz)
- **Segment Duration**: Modify segment length (default: 5 seconds)
- **Email Settings**: Configure SMTP for password reset emails
- **Database**: Switch to PostgreSQL for production

## 📈 Performance Optimization

### Audio Processing
- **FFmpeg Integration**: Efficient audio format conversion
- **Memory Management**: Temporary files cleaned up automatically
- **Parallel Processing**: Segment analysis can be parallelized
- **Caching**: Analysis results cached for repeated access

### Database Optimization
- **Indexing**: User ID and date indexes for fast queries
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Minimal data transfer
- **Backup Strategy**: Regular database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements_enhanced.txt
pip install pytest black flake8

# Run tests
python test_enhanced_system.py

# Format code
black *.py

# Check linting
flake8 *.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Librosa**: Audio processing and pitch extraction
- **Streamlit**: Web application framework
- **SQLite**: Database management
- **FFmpeg**: Audio format conversion
- **YouTube-DL**: YouTube audio extraction

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the deployment guide
- Review the test suite for examples
- Consult the inline documentation

## 🔮 Future Enhancements

### Planned Features
- **Real-time Analysis**: Live pitch feedback during recording
- **Advanced Analytics**: Machine learning-based progress prediction
- **Social Features**: Share analyses and compare with others
- **Mobile App**: Native mobile application
- **API Access**: REST API for third-party integrations

### Technical Improvements
- **Microservices**: Separate authentication and analysis services
- **Load Balancing**: Distribute traffic across multiple instances
- **Caching**: Redis for session and analysis caching
- **CDN**: Content delivery network for static assets

---

**QIRAT AI Enhanced** - Making pitch analysis accessible and actionable for everyone! 🎵 