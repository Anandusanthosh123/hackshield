# HackShield

HackShield is a comprehensive, gamified cyber security learning platform built with Django. It provides an interactive environment for users to learn ethical hacking, cyber security concepts, and practical skills through courses, challenges, hands-on labs, and mini-games.

## 🚀 Features

### Core Learning Platform
- **Courses & Lessons**: Structured learning paths with video, image, and text content
- **Interactive Quizzes**: Course-specific quizzes with scoring and certificates
- **CTF Challenges**: Capture The Flag challenges with difficulty levels
- **Hacking Labs**: Docker-based virtual labs with Kali Linux and Ubuntu targets
- **Mini-Games**: Gamified learning experiences

### Gamification System
- **XP & Levels**: Earn experience points and level up
- **Badges**: Achievement system for milestones
- **Streaks**: Daily activity tracking
- **Leaderboard**: Competitive ranking system
- **Certificates**: PDF certificates for course completion

### User Management
- **Custom User Profiles**: Avatars, cover photos, social links
- **Two-Factor Authentication**: Enhanced security with OTP
- **Progress Tracking**: Detailed analytics and heatmaps
- **Cyber Coins**: Virtual currency system

### Content & Feeds
- **Cybersecurity News**: Real-time news aggregation
- **Job Board**: Cybersecurity job listings
- **AI Assistant**: Ollama-powered lab guidance

### Technical Features
- **Docker Integration**: Containerized hacking environments
- **Background Tasks**: Celery-powered async operations
- **Caching System**: Offline-ready content
- **Admin Panel**: Jazzmin-themed Django admin

## 🛠️ Tech Stack

- **Backend**: Django 4.x
- **Database**: MySQL
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **Frontend**: HTML5, CSS3, JavaScript
- **Containerization**: Docker
- **AI**: Ollama (Dolphin-Phi model)
- **Admin Theme**: Jazzmin

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+
- Redis Server
- Docker & Docker Compose
- Node.js (for frontend assets, optional)
- Ollama (for AI features)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hackshield.git
cd hackshield
```

### 2. Create Virtual Environment
```bash
python -m venv hackshield_env
source hackshield_env/bin/activate  # On Windows: hackshield_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE hackshield;
EXIT;

# Run migrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Configure Environment
Update `hackshield/settings.py` with your configurations:
- Database credentials
- Redis URL
- Docker socket path
- API keys (NewsData.io for news feed)

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://user:password@localhost:3306/hackshield
REDIS_URL=redis://localhost:6379/0
DOCKER_SOCKET=npipe:////./pipe/docker_engine
OLLAMA_URL=http://127.0.0.1:11434
```

### Docker Setup
Ensure Docker is running and accessible. For Windows, update the `DOCKER_SOCK` setting in `settings.py`.

### Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull dolphin-phi
```

## 🏃‍♂️ Running the Application

### Development Server
```bash
python manage.py runserver
```

### With Celery (Background Tasks)
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A hackshield worker --loglevel=info

# Terminal 3: Celery beat (optional)
celery -A hackshield beat --loglevel=info
```

### With Docker Labs
Ensure Docker daemon is running for lab functionality.

## 📖 Usage

### User Registration & Login
1. Visit the homepage and register a new account
2. Complete your profile with avatar and details
3. Start learning through the dashboard

### Learning Path
1. **Courses**: Browse and enroll in structured courses
2. **Lessons**: Complete lessons sequentially
3. **Quizzes**: Pass course quizzes to earn certificates
4. **Challenges**: Solve CTF challenges for XP
5. **Labs**: Practice in Docker-based environments

### Admin Panel
Access `/admin/` with superuser credentials to:
- Manage courses, lessons, and quizzes
- Create challenges and badges
- View user progress and analytics
- Configure system settings

## 🏗️ Project Structure

```
hackshield/
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin configurations
│   ├── tasks.py            # Celery tasks
│   ├── docker_utils.py     # Docker lab utilities
│   ├── badge_system.py     # Badge logic
│   ├── ai_prompts.py       # AI system prompts
│   ├── utils/              # Utility functions
│   └── management/         # Custom management commands
├── hackshield/             # Django project settings
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
├── hackshield-images/      # Docker lab images
└── requirements.txt        # Python dependencies
```

## 🔧 API Endpoints

### REST API Endpoints
- `GET /api/quiz/` - Fetch quiz questions
- `POST /api/quiz/complete/` - Submit quiz results
- `GET /api/news/items/` - Fetch news feed
- `GET /api/jobs/items/` - Fetch job listings

### AJAX Endpoints
- `/web-shell/<slug>/` - Execute commands in lab containers
- `/lab-ai-guide/` - AI assistance for labs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Django best practices
- Write comprehensive tests
- Update documentation
- Ensure code quality with linting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Cybersecurity researchers and educators
- Open-source contributors

## 📞 Support

For support, email support@hackshield.com or join our Discord community.

## 🔄 Updates

### Version 4.0
- Docker-based hacking labs
- AI-powered lab assistance
- Enhanced gamification system
- Real-time news and job feeds
- Certificate generation system

---

**Happy Hacking! 🛡️**
