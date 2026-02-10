# 🎓 EdFast - Academic Management Platform

A modern, full-stack academic management platform built with Flask API and Next.js frontend, featuring AI-powered transcript analysis, LinkedIn integration, and comprehensive academic tools.

## 🚀 Features

### Core Academic Features
- **📊 AI-Powered Transcript Analysis** - Upload and analyze academic transcripts with intelligent insights
- **🤖 Academic Chatbot** - Get personalized academic advice and course recommendations
- **📅 Timetable Management** - Upload, filter, and analyze university timetables
- **💼 Resume Builder** - Generate professional resumes from academic data
- **📚 Course Explorer** - Browse and get information about university courses
- **👥 PeerHub** - Discussion forum for students to connect and share knowledge

### LinkedIn Integration
- **🔍 Job Search** - Search for LinkedIn jobs with advanced filtering
- **📱 Post Scraping** - Scrape LinkedIn posts for social media analysis
- **📈 Analytics** - Comprehensive statistics and insights

### Technical Features
- **🔐 JWT Authentication** - Secure user authentication and authorization
- **🗄️ Database Support** - SQLite and PostgreSQL database support
- **📱 Responsive Design** - Modern, mobile-friendly interface
- **🎨 Beautiful UI** - Built with Tailwind CSS and modern design principles

## 🏗️ Architecture

```
EdFast Platform
├── flask_api/           # Flask REST API Backend
│   ├── api/            # API endpoints
│   ├── middleware/     # Custom middleware
│   ├── utils/          # Utility functions
│   └── uploads/        # File uploads
├── edfast-frontend/    # Next.js Frontend
│   ├── src/app/        # App router pages
│   ├── src/components/ # React components
│   └── src/lib/        # Utilities and API client
├── linkedin/           # LinkedIn integration
├── database/           # Database models and config
├── auth/              # Authentication system
├── chat/              # AI chatbot functionality
├── data/              # Data processing
├── resume/            # Resume builder
├── timetable/         # Timetable management
└── peerhub/           # Discussion forum
```

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication
- **ChromaDB** - Vector database
- **LangChain** - AI/LLM integration
- **Google Gemini** - AI model
- **JobSpy** - LinkedIn job scraping
- **Selenium** - Web automation

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Zustand** - State management
- **React Hook Form** - Form handling
- **Axios** - API client

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Chrome WebDriver (for LinkedIn features)

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r flask_api/requirements.txt
   ```

2. **Start the Flask API:**
   ```bash
   cd flask_api
   python app.py
   ```
   API will be available at `http://localhost:5000`

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   cd edfast-frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

### LinkedIn Integration Setup

1. **Run the installation script:**
   ```bash
   python install_linkedin_integration.py
   ```

2. **Configure Google Drive (optional):**
   - Create a Google Cloud Project
   - Enable Google Drive API
   - Download service account credentials
   - Place `credentials.json` in the root directory

## 📖 Usage

### Academic Features
1. **Register/Login** - Create an account or sign in
2. **Upload Transcript** - Upload an image of your academic transcript
3. **Initialize System** - Set up AI components
4. **Ask Questions** - Use the chatbot for academic advice
5. **Manage Timetable** - Upload and filter your course schedule
6. **Build Resume** - Generate professional resumes

### LinkedIn Features
1. **Job Search** - Search for jobs with filters
2. **Post Scraping** - Scrape LinkedIn profiles/pages
3. **Analytics** - View statistics and insights

## 🔧 Configuration

### Environment Variables
```bash
# Flask Configuration
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=sqlite:///edfast.db

# AI Configuration
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=your-groq-api-key

# LinkedIn Integration (Optional)
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
CHROME_HEADLESS=false
```

## 📁 Project Structure

### Key Directories
- `flask_api/` - Flask REST API with 48+ endpoints
- `edfast-frontend/` - Next.js frontend application
- `linkedin/` - LinkedIn scraping functionality
- `database/` - Database models and configuration
- `auth/` - User authentication system
- `chat/` - AI chatbot implementation
- `data/` - Data processing and extraction
- `resume/` - Resume builder functionality
- `timetable/` - Timetable management
- `peerhub/` - Discussion forum system

### API Endpoints
- `/api/v1/auth/*` - Authentication
- `/api/v1/users/*` - User management
- `/api/v1/chatbot/*` - AI chatbot
- `/api/v1/timetable/*` - Timetable management
- `/api/v1/resume/*` - Resume builder
- `/api/v1/courses/*` - Course information
- `/api/v1/peerhub/*` - Discussion forum
- `/api/v1/linkedin/*` - LinkedIn integration
- `/api/v1/dashboard/*` - Dashboard data

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation and sanitization
- Rate limiting (recommended for production)

## 🚀 Deployment

### Backend Deployment
1. Set up a production WSGI server (Gunicorn)
2. Configure environment variables
3. Set up database (PostgreSQL recommended)
4. Configure reverse proxy (Nginx)

### Frontend Deployment
1. Build the Next.js application
2. Deploy to Vercel, Netlify, or similar
3. Configure environment variables
4. Update API endpoints

## 📚 Documentation

- [LinkedIn Integration Guide](LINKEDIN_INTEGRATION_GUIDE.md)
- [LinkedIn Integration Summary](LINKEDIN_INTEGRATION_SUMMARY.md)
- [API Documentation](flask_api/API_DOCUMENTATION.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the documentation
2. Review the troubleshooting guides
3. Open an issue on GitHub
4. Contact the development team

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Integration with more job platforms
- [ ] AI-powered career recommendations
- [ ] Real-time notifications
- [ ] Multi-language support

---

**EdFast** - Empowering students with intelligent academic management tools.