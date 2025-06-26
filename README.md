# Schedgic 📚

An intelligent AI-powered course scheduling application that automatically generates optimal weekly schedules based on your course requirements and personal constraints using advanced natural language processing.

## ✨ Key Features

### 🤖 AI-Powered Intelligence
- **Natural Language Constraint Parsing**: Tell us your preferences in plain English like "No classes before 9am" or "Avoid TA Smith"
- **Advanced NER Model**: Custom-trained Named Entity Recognition model for understanding scheduling constraints
- **Smart Optimization**: Intelligent algorithms that find the perfect balance between your preferences and requirements

### ⚡ Schedule Generation & Management
- **Instant Schedule Creation**: Generate conflict-free schedules in seconds
- **Multiple Preferences**: Choose between "crammed" (fewer days) or "spaced out" (distributed) scheduling styles
- **Interactive Editing**: Drag and drop classes to alternative time slots with real-time validation
- **Progress Tracking**: Visual progress indicators with estimated completion times during generation

### 📊 User Dashboard & Analytics
- **Personal Statistics**: Track schedules created, hours saved, success rates, and efficiency metrics
- **Recent Activity**: View your scheduling history and generation logs
- **Performance Insights**: Monitor your scheduling patterns and optimization trends
- **Real-time Updates**: Live statistics that update as you use the application

### 🔐 Secure Authentication System
- **Token-Based Authentication**: Secure session management with JWT-like tokens
- **User Profiles**: Complete profile management with statistics tracking
- **Session Management**: Automatic session cleanup and security monitoring
- **Password Security**: Industry-standard password hashing and validation

### 📱 Modern User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Interactive Guide**: Step-by-step onboarding for first-time users
- **Skeleton Loading**: Beautiful loading states with progress indicators
- **Real-time Feedback**: Instant validation and error handling
- **Accessibility**: WCAG-compliant design with keyboard navigation support

### 📄 Export & Sharing
- **PDF Export**: Download beautifully formatted schedule PDFs
- **Social Sharing**: Share schedules via WhatsApp and other platforms
- **Schedule Saving**: Save multiple schedules with custom names and descriptions
- **Visual Calendar**: Clean, professional schedule layout

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Supabase Account** (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/schedgic.git
   cd schedgic
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Download spaCy model
   python -m spacy download en_core_web_md
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Setup**
   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Run the migrations in `supabase/migrations/` to set up your database schema
   - Update your `.env` file with Supabase credentials

### Running the Application

1. **Start the Backend**
   ```bash
   cd backend
   python app.py
   ```
   Backend runs on `http://localhost:5001`

2. **Start the Frontend**
   ```bash
   cd frontend
   npm start
   ```
   Frontend runs on `http://localhost:3000`

## 🏗️ Architecture

### Backend (Flask + AI)
- **Flask API**: RESTful endpoints for schedule generation and user management
- **Custom NER Model**: spaCy-based model trained on scheduling constraints
- **Optimization Engine**: Advanced algorithms for schedule optimization
- **Supabase Integration**: Real-time database with Row Level Security
- **Statistics Tracking**: Comprehensive user analytics and performance metrics

### Frontend (React)
- **Modern React**: Hooks-based architecture with functional components
- **Responsive Design**: Mobile-first CSS with advanced animations
- **Real-time Updates**: Live statistics and activity feeds
- **Interactive Components**: Drag-and-drop schedule editing
- **Progressive Enhancement**: Works without JavaScript for basic functionality

### Database (Supabase PostgreSQL)
- **User Management**: Secure authentication with custom user profiles
- **Schedule Storage**: Efficient storage of schedules and constraints
- **Statistics Tracking**: Detailed analytics and usage patterns
- **Session Management**: Secure token-based authentication
- **Real-time Features**: Live updates and collaborative features ready

## 📖 How to Use

### 1. Create Your Account
Sign up with email and password to start tracking your scheduling progress and save your schedules.

### 2. Choose Your Style
Select between:
- **Crammed**: Fewer days with back-to-back classes
- **Spaced Out**: More days with better distribution

### 3. Add Your Courses
For each course, provide:
- Course name (e.g., "CS101", "Mathematics")
- Available lecture time slots
- Available TA/tutorial time slots

### 4. Set Your Constraints
Use natural language to specify preferences:
- **Time**: "No classes before 9am", "No classes after 5pm"
- **Days**: "No classes on Friday", "I can't attend Tuesday"
- **TAs**: "Avoid TA Smith", "Prefer TA Johnson"
- **Complex**: "No early morning classes before 10am and not on Monday"

### 5. Generate & Customize
- Click "Generate Schedule" and watch the AI work
- View your optimized schedule in a visual calendar
- Drag and drop classes to alternative time slots if needed
- Save your schedule with a custom name

### 6. Export & Share
- Download as a professional PDF
- Share via WhatsApp or other social platforms
- Access your saved schedules anytime from your dashboard

## 🤖 AI Constraint Examples

Our AI understands complex scheduling preferences:

```
Time Constraints:
• "No classes before 9am"
• "I prefer afternoon sessions"
• "Nothing after 6pm"

Day Constraints:
• "No Friday classes"
• "I can't attend Wednesday morning"
• "Prefer Monday, Wednesday, Friday"

TA Preferences:
• "Avoid TA Johnson"
• "I prefer TA Smith for CS101"
• "No TA sessions with Alex"

Complex Combinations:
• "No classes before 10am and not on Tuesday"
• "Prefer morning lectures but afternoon TA sessions"
• "Avoid early Friday classes and TA Brown"
```

## 📊 Dashboard Features

### Personal Statistics
- **Schedules Created**: Total and weekly counts
- **Hours Saved**: Time saved vs manual planning
- **Success Rate**: Percentage of successful generations
- **Efficiency Score**: Schedule optimization rating

### Recent Activity
- Schedule generation history
- Save and export activities
- Error tracking and resolution
- Performance metrics

### Quick Actions
- Create new schedules instantly
- Access saved schedules
- View scheduling guides
- Browse templates (coming soon)

## 🛠️ Development

### Project Structure
```
schedgic/
├── backend/                 # Flask backend
│   ├── ai_model/           # NLP model and training
│   ├── auth/               # Authentication system
│   ├── api/                # API endpoints
│   ├── schedule/           # Scheduling algorithms
│   └── app.py              # Main application
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── styles/         # CSS styling
│   └── public/             # Static assets
└── supabase/               # Database migrations
```

### Adding New Features

1. **New Constraint Types**: Update the NER model in `backend/ai_model/`
2. **UI Components**: Add to `frontend/src/components/`
3. **API Endpoints**: Extend `backend/api/`
4. **Database Changes**: Create new migrations in `supabase/migrations/`

### Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test

# Build for production
npm run build
```

## 🔧 Configuration

### Environment Variables
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### Customization Options
- **AI Model**: Retrain with your own constraint data
- **Styling**: Modify CSS variables in `frontend/src/styles/base.css`
- **Algorithms**: Adjust optimization parameters in `backend/schedule/logic.py`
- **Database**: Extend schema with custom migrations

## 🚀 Deployment

### Frontend (Netlify)
```bash
cd frontend
npm run build
# Deploy the build/ directory to Netlify
```

### Backend (Railway/Heroku)
```bash
cd backend
# Configure your deployment platform
# Set environment variables
# Deploy with your preferred service
```

### Database (Supabase)
- Production database is automatically managed
- Run migrations through Supabase dashboard
- Configure Row Level Security policies

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with proper tests
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new features
- Update documentation as needed
- Ensure responsive design for UI changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **spaCy** for natural language processing capabilities
- **Supabase** for backend infrastructure and real-time features
- **React** ecosystem for modern frontend development
- **Open Source Community** for the amazing libraries and tools

## 📞 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/schedgic/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/schedgic/discussions)
- **Email**: Contact the development team for enterprise inquiries

---

**Built with ❤️ for students everywhere**

*Making academic planning intelligent, efficient, and enjoyable.*