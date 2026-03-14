# CampusAid - Intelligent Campus Grievance Portal

A full-stack multilingual complaint management system with ML-powered classification, built for Bennett University.

## 🎯 Features

- **Multilingual Support**: Hindi, English, and Hinglish complaint understanding
- **Voice Input**: Speech-to-text using Whisper for voice complaints
- **ML Classification**: Automatic department routing using sentence transformers
- **Role-Based Access**: Student, Worker, Admin, and Warden roles
- **Real-time Dashboard**: Statistics and complaint tracking
- **PostgreSQL Database**: Production-ready data persistence

## 🏗️ Architecture

```
Frontend (Next.js + TypeScript) → Backend (FastAPI + Python) → ML Pipeline
                                        ↓
                                  PostgreSQL Database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL (or use SQLite for development)

### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure database** (Optional - defaults to SQLite):
```bash
# For PostgreSQL, create .env file:
echo DATABASE_URL=postgresql://user:password@localhost/campusaid > .env
```

4. **Train ML model**:
```bash
python train_classifier.py
```

5. **Start backend server**:
```bash
python app/main.py
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend/campusaid
npm install
```

2. **Configure API URL** (Optional):
```bash
# Create .env.local file:
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
```

3. **Start development server**:
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 👥 Demo Users

The system automatically creates demo users on first startup:

| Username | Password | Role |
|----------|----------|------|
| student1 | student123 | Student |
| worker1 | worker123 | Worker |
| admin1 | admin123 | Admin |
| warden1 | warden123 | Warden |

## 🧪 Testing

### Test Backend Endpoints
```bash
python backend/test_endpoints.py
```

### Test Database
```bash
python backend/test_database.py
```

### Test Complete System
```bash
python backend/test_system.py
```

## 📁 Project Structure

```
campusaid/
├── backend/
│   ├── app/
│   │   ├── ml/                    # ML pipeline
│   │   │   ├── multilingual_embedder.py
│   │   │   ├── complaint_classifier.py
│   │   │   └── speech_to_text.py
│   │   ├── routes/                # API routes
│   │   │   ├── auth_router.py
│   │   │   ├── complaints_router.py
│   │   │   └── admin_router.py
│   │   ├── models.py              # Database models
│   │   ├── schemas.py             # Pydantic schemas
│   │   ├── database.py            # Database config
│   │   ├── auth.py                # Authentication
│   │   └── main.py                # FastAPI app
│   ├── models/                    # Trained ML models
│   ├── train_classifier.py        # Model training
│   └── requirements.txt
├── frontend/campusaid/
│   ├── app/                       # Next.js pages
│   │   ├── page.tsx               # Login page
│   │   ├── signup/                # Signup page
│   │   ├── user/                  # User portal
│   │   └── admin/                 # Admin dashboard
│   ├── components/                # React components
│   │   ├── auth/                  # Auth components
│   │   ├── ui/                    # UI components
│   │   ├── ComplaintForm.tsx
│   │   ├── ComplaintList.tsx
│   │   ├── VoiceRecorder.tsx
│   │   └── ComplaintTable.tsx
│   └── lib/
│       └── auth.ts                # Auth utilities
└── data/
    ├── complaints.csv             # Training data
    └── labels.csv
```

## 🎨 Design System

**Colors**:
- Deep Navy Blue: `#1a2332`
- Crimson Red: `#dc143c`
- White background with slate accents

**Theme**: Professional, institutional, clean

## 🔧 Configuration

### Backend Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost/campusaid
# Or leave empty for SQLite (default)
```

### Frontend Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 ML Pipeline

1. **Multilingual Embeddings**: Uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
2. **Classification**: Logistic Regression trained on complaint categories
3. **Confidence Threshold**: Low confidence complaints marked for manual review
4. **Categories**: Hostel, IT, Academic, Maintenance

## 🔐 Security

- Password hashing with bcrypt
- Role-based access control
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Complaints
- `POST /submit-complaint` - Submit text complaint
- `POST /voice-complaint` - Submit voice complaint
- `GET /complaints` - List complaints (with filters)
- `GET /complaints/{id}` - Get complaint by ID
- `PATCH /complaints/{id}` - Update complaint status (admin)

### Admin
- `GET /admin/stats` - Get statistics dashboard

### Health
- `GET /health` - Health check
- `GET /` - Service info

## 🎓 For Viva/Presentation

**Key Points to Explain**:

1. **Why Multilingual?** - Indian universities have diverse linguistic backgrounds
2. **Why No Translation?** - Multilingual embeddings understand meaning directly
3. **Why Manual Review?** - Ethical AI - human oversight for low confidence
4. **Why PostgreSQL?** - Production-ready, scalable, ACID compliant
5. **Why FastAPI?** - Modern, fast, automatic API documentation
6. **Why Next.js?** - Server-side rendering, TypeScript support, modern React

**Demo Flow**:
1. Show login with different roles
2. Submit complaint (text and voice)
3. Show ML classification with confidence
4. Show admin dashboard with statistics
5. Explain department routing logic

## 🐛 Troubleshooting

**Backend won't start**:
- Check if port 8000 is available
- Verify Python dependencies installed
- Check if ML model is trained

**Frontend won't start**:
- Check if port 3000 is available
- Verify Node dependencies installed
- Check API URL configuration

**ML model not working**:
- Run `python backend/train_classifier.py`
- Check if `backend/models/complaint_classifier.pkl` exists

**Database errors**:
- For PostgreSQL: Verify connection string
- For SQLite: Check file permissions

## 📚 Documentation

- [Project Structure](PROJECT_STRUCTURE.md)
- [Project Summary](PROJECT_SUMMARY.md)
- [Test Results](TEST_RESULTS.md)
- [Viva Guide](VIVA_GUIDE.md)
- [Diagrams](DIAGRAMS.md)

## 🤝 Contributing

This is a college project. For improvements:
1. Keep code simple and explainable
2. Add comments for complex logic
3. Test thoroughly before committing
4. Update documentation

## 📄 License

Educational project for Bennett University

## 👨‍💻 Authors

Bennett University Students - Major Project 2024

---

**Built with ❤️ for Bennett University**
