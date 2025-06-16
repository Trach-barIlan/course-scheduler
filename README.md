# Course Scheduler 📚

A sophisticated AI-powered course scheduling application that automatically generates optimal weekly schedules based on your course requirements and personal constraints.

## ✨ Features

- **AI-Powered Constraint Parsing**: Natural language processing to understand scheduling preferences
- **Intelligent Schedule Generation**: Optimized algorithms to create conflict-free schedules
- **Interactive Schedule Management**: Drag-and-drop functionality to modify schedules
- **Multiple Schedule Preferences**: Choose between crammed or spaced-out scheduling
- **User Authentication**: Secure user accounts with profile management
- **Export & Share**: Download schedules as PDF or share via social media
- **Real-time Validation**: Instant feedback on scheduling conflicts
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/course-scheduler.git
   cd course-scheduler
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Download required spaCy models
   python3 -m spacy download en_core_web_md
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your Supabase credentials:
   SUPABASE_URL=...
   SUPABASE_ANON_KEY=...
   SECRET_KEY=...
   FLASK_ENV=...
   ```

3. **Frontend Setup**
   ```bash
   cd course-scheduler
   npm install
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5000`

2. **Start the Frontend Development Server**
   ```bash
   cd course-scheduler
   npm start
   ```
   The frontend will run on `http://localhost:3000`

3. **Build the Frontend for Production**
   ```bash
   cd course-scheduler
   npm run build
   ```

## 🏗️ Architecture

### Backend (Flask)
- **AI Model**: Custom NER model for constraint parsing
- **Schedule Logic**: Optimization algorithms using OR-Tools
- **Authentication**: Supabase integration for user management
- **API**: RESTful endpoints for schedule generation and user management

### Frontend (React)
- **Modern UI**: Clean, responsive design with CSS Grid/Flexbox
- **State Management**: React hooks for application state
- **Interactive Components**: Drag-and-drop schedule editing
- **Export Features**: PDF generation and social sharing

### Database (Supabase)
- **User Profiles**: Secure user authentication and profile management
- **Saved Schedules**: Persistent storage of user schedules
- **Row Level Security**: Fine-grained access control

## 📖 Usage

1. **Create an Account**: Sign up or log in to save your schedules
2. **Add Courses**: Enter course names, lecture times, and TA session times
3. **Set Constraints**: Use natural language to specify preferences:
   - "No classes before 9am"
   - "No classes on Tuesday"
   - "Avoid TA Smith"
   - "No classes after 5pm"
4. **Generate Schedule**: Click "Generate Schedule" to create your optimal schedule
5. **Customize**: Drag and drop classes to alternative time slots
6. **Export**: Download as PDF or share your schedule

## 🤖 AI Constraint Examples

The AI understands natural language constraints such as:

- **Time Constraints**: "No early morning classes before 10am"
- **Day Constraints**: "I can't attend Wednesday classes"
- **TA Preferences**: "Please avoid TA Johnson"
- **Combined Constraints**: "No classes before 9am and not on Friday"

## 🛠️ Development

### Adding New Constraint Types

1. Update the parse function in `backend/ai_model/ml_parser.py`
2. Add patterns in `backend/ai_model/patterns.py`
3. Add training data in `backend/ai_model/training_data.py`
4. Add test cases in `backend/ai_model/test_data.py`
5. Retrain the model by running `backend/ai_model/train_ner.py`

### Project Structure

```
course-scheduler/
├── backend/                 # Flask backend
│   ├── ai_model/           # NLP model and training
│   ├── auth/               # Authentication logic
│   ├── schedule/           # Scheduling algorithms
│   └── app.py              # Main Flask application
├── course-scheduler/        # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── styles/         # CSS styling
│   └── public/             # Static assets
└── supabase/               # Database migrations
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_auth.py
python test_email_validation.py
```

### Frontend Tests
```bash
cd course-scheduler
npm test
```

### Build Frontend
```bash
cd course-scheduler
npm run build
```

## 📦 Dependencies

### Backend
- **Flask**: Web framework
- **spaCy**: Natural language processing
- **OR-Tools**: Optimization algorithms
- **Supabase**: Database and authentication
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **React**: UI framework
- **html2canvas**: Screenshot generation
- **jsPDF**: PDF export functionality
- **React Router**: Client-side routing

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies and AI/ML frameworks
- Inspired by the need for intelligent academic planning tools
- Special thanks to the open-source community for the amazing libraries

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/course-scheduler/issues) page
2. Create a new issue with detailed information
3. Contact the development team

---

**Made with ❤️ for students everywhere**