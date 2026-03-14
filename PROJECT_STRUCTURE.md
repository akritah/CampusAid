# 📁 PROJECT STRUCTURE - CampusAid

Complete guide to understanding the project organization.

---

## 🌳 Directory Tree

```
campusaid/
│
├── backend/                          # Backend application
│   ├── app/                          # Main application package
│   │   ├── ml/                       # Machine Learning modules
│   │   │   ├── __init__.py          # Package initializer
│   │   │   ├── multilingual_embedder.py    # 🧠 Embeddings generator
│   │   │   ├── complaint_classifier.py     # 🎯 Classifier
│   │   │   └── speech_to_text.py           # 🎤 Voice to text
│   │   │
│   │   ├── routes/                   # API routes (existing)
│   │   ├── utils/                    # Utility functions (existing)
│   │   ├── __init__.py              # Package initializer
│   │   ├── main.py                  # 🌐 FastAPI application
│   │   ├── models.py                # Database models (existing)
│   │   ├── schemas.py               # Pydantic schemas (existing)
│   │   └── database.py              # Database config (existing)
│   │
│   ├── models/                       # Trained ML models
│   │   └── complaint_classifier.pkl  # 💾 Trained classifier
│   │
│   ├── train_classifier.py          # 🎓 Training script
│   ├── test_system.py               # 🧪 System tests
│   └── requirements.txt             # 📦 Python dependencies
│
├── data/                             # Training data
│   ├── complaints.csv               # 📊 Complaint dataset
│   └── labels.csv                   # (Optional) Label definitions
│
├── frontend/                         # Frontend application
│   ├── index.html                   # 🎨 Main UI (HTML/JS)
│   ├── App.jsx                      # ⚛️ React version (optional)
│   └── REACT_SETUP.md              # React setup guide
│
├── README.md                         # 📖 Main documentation
├── QUICKSTART.md                     # 🚀 Quick setup guide
├── INSTALLATION.md                   # 📦 Detailed installation
├── VIVA_GUIDE.md                     # 🎓 Viva preparation
├── PROJECT_SUMMARY.md                # 📊 Project overview
└── PROJECT_STRUCTURE.md              # 📁 This file
```

---

## 📂 Detailed File Descriptions

### Backend Files

#### `backend/app/main.py`
**Purpose:** Main FastAPI application with API endpoints

**Key Components:**
- FastAPI app initialization
- CORS middleware configuration
- ML model loading (global)
- API endpoints:
  - `GET /` - Health check
  - `POST /submit-complaint` - Text complaints
  - `POST /voice-complaint` - Voice complaints
  - `GET /categories` - List categories
  - `POST /batch-classify` - Batch processing

**Why Important:** This is the entry point for all API requests. Frontend talks to this file.

**Lines of Code:** ~300

---

#### `backend/app/ml/multilingual_embedder.py`
**Purpose:** Convert text to multilingual embeddings

**Key Components:**
- `MultilingualEmbedder` class
- `encode()` - Convert text to vector
- `similarity()` - Calculate text similarity
- `batch_encode()` - Process multiple texts

**Model Used:** `paraphrase-multilingual-MiniLM-L12-v2`

**Why Important:** This is the CORE of multilingual understanding. No translation needed!

**Lines of Code:** ~200

**Key Concept:**
```python
# Same meaning → Similar vectors
"Hot water not available"     → [0.23, -0.45, ...]
"Hot water nahi available"    → [0.24, -0.44, ...]  # Similar!
```

---

#### `backend/app/ml/complaint_classifier.py`
**Purpose:** Classify complaints into categories

**Key Components:**
- `ComplaintClassifier` class
- `train()` - Train the classifier
- `predict()` - Classify single complaint
- `predict_batch()` - Classify multiple complaints
- `save()` / `load()` - Model persistence

**Algorithm:** Logistic Regression

**Why Important:** Maps embeddings to categories. This is what we train!

**Lines of Code:** ~300

**Key Concept:**
```python
# Embedding → Category
[0.23, -0.45, ...] → "Hostel" (87% confidence)
```

---

#### `backend/app/ml/speech_to_text.py`
**Purpose:** Convert audio to text

**Key Components:**
- `SpeechToText` class
- `transcribe()` - Convert audio file to text
- `transcribe_from_bytes()` - Convert audio bytes to text
- Support for local Whisper and API

**Model Used:** Whisper (base model)

**Why Important:** Enables voice input. Voice → Text → Same pipeline!

**Lines of Code:** ~200

**Key Concept:**
```python
# Voice is just another input method
Audio → Whisper → Text → Embeddings → Category
```

---

#### `backend/train_classifier.py`
**Purpose:** Train the complaint classifier

**What It Does:**
1. Loads training data from CSV
2. Generates embeddings for all complaints
3. Splits data into train/test sets
4. Trains Logistic Regression
5. Evaluates accuracy
6. Saves trained model

**When to Run:** 
- Once before starting the server
- Whenever you add new training data
- When you want to retrain

**Output:** `models/complaint_classifier.pkl`

**Lines of Code:** ~150

---

#### `backend/test_system.py`
**Purpose:** Automated testing of all components

**What It Tests:**
1. Embedder functionality
2. Classifier loading and prediction
3. API imports

**When to Run:**
- After installation
- After training
- Before demo/viva

**Lines of Code:** ~200

---

#### `backend/requirements.txt`
**Purpose:** List of Python dependencies

**Key Packages:**
- `fastapi` - Web framework
- `sentence-transformers` - Embeddings
- `scikit-learn` - Classification
- `torch` - Deep learning
- `pandas` - Data processing

**Total Size:** ~1.5GB (including models)

---

### Data Files

#### `data/complaints.csv`
**Purpose:** Training data for classifier

**Format:**
```csv
id,text,language,category,source
1,"Hot water not available",en,Hostel,manual
2,"WiFi nahi working",hi-en,IT,manual
```

**Columns:**
- `id` - Unique identifier
- `text` - Complaint text
- `language` - en (English), hi (Hindi), hi-en (Hinglish)
- `category` - Target category
- `source` - Data source (manual, ai, kaggle)

**Size:** 400+ complaints

**Categories:** Hostel, Academic, IT, Infrastructure, Harassment, Administration

---

### Frontend Files

#### `frontend/index.html`
**Purpose:** Simple web UI for complaint submission

**Features:**
- Text complaint form
- Voice complaint form
- Result display
- No build tools needed!

**Technology:** Plain HTML + JavaScript

**Why This Approach:**
- Simple and easy to understand
- No npm, webpack, or build process
- Works by just opening the file
- Perfect for college projects

**Lines of Code:** ~400

**Key Sections:**
1. HTML structure
2. CSS styling
3. JavaScript for API calls

---

#### `frontend/App.jsx`
**Purpose:** React version of the frontend (optional)

**Features:**
- Component-based architecture
- State management with hooks
- Same functionality as HTML version

**Technology:** React + Axios

**Why Optional:**
- More complex setup
- Requires npm and build tools
- Better for those familiar with React

**Lines of Code:** ~300

---

### Documentation Files

#### `README.md`
**Purpose:** Main project documentation

**Contents:**
- System overview
- Features
- Architecture
- Installation
- Usage
- How it works
- Viva preparation

**Length:** ~500 lines

**Audience:** Everyone (students, professors, developers)

---

#### `QUICKSTART.md`
**Purpose:** Get started in 5 minutes

**Contents:**
- 3-step setup
- Quick tests
- Troubleshooting

**Length:** ~200 lines

**Audience:** Users who want to run the system quickly

---

#### `INSTALLATION.md`
**Purpose:** Detailed installation guide

**Contents:**
- Prerequisites
- Step-by-step installation
- Platform-specific notes
- Troubleshooting
- Docker setup

**Length:** ~400 lines

**Audience:** Users setting up for the first time

---

#### `VIVA_GUIDE.md`
**Purpose:** Viva preparation and Q&A

**Contents:**
- Core concepts explained
- Common questions and answers
- Demo script
- Technical specifications

**Length:** ~600 lines

**Audience:** Students preparing for viva

---

#### `PROJECT_SUMMARY.md`
**Purpose:** Complete project overview

**Contents:**
- Abstract
- Architecture
- Technologies
- Performance metrics
- Future enhancements

**Length:** ~500 lines

**Audience:** For project reports and presentations

---

#### `PROJECT_STRUCTURE.md`
**Purpose:** Understanding project organization (this file!)

**Contents:**
- Directory tree
- File descriptions
- Code organization
- Design decisions

**Length:** ~400 lines

**Audience:** Developers and reviewers

---

## 🎯 Key Design Decisions

### 1. Why Separate ML Modules?

**Decision:** ML code in `app/ml/` directory

**Reasons:**
- **Modularity:** Easy to test and modify
- **Reusability:** Can use in other projects
- **Clarity:** Clear separation of concerns
- **Maintainability:** Easy to find and update

---

### 2. Why Global Model Loading?

**Decision:** Load models once when server starts

**Code:**
```python
# In main.py
embedder = MultilingualEmbedder()  # Load once
classifier = ComplaintClassifier(embedder)  # Load once
```

**Reasons:**
- **Performance:** Loading is slow (~2 seconds)
- **Efficiency:** Don't reload for every request
- **Memory:** Share model across requests

---

### 3. Why Separate Training Script?

**Decision:** `train_classifier.py` separate from `main.py`

**Reasons:**
- **Clarity:** Training vs. inference are different
- **Flexibility:** Can train without running server
- **Safety:** Don't accidentally retrain in production

---

### 4. Why Plain HTML Frontend?

**Decision:** Provide both HTML and React versions

**Reasons:**
- **Simplicity:** HTML works without build tools
- **Accessibility:** Anyone can understand
- **Flexibility:** React for advanced users
- **Education:** Good for learning

---

### 5. Why Extensive Documentation?

**Decision:** Multiple documentation files

**Reasons:**
- **Different audiences:** Quick start vs. deep dive
- **Viva preparation:** Specific guide for students
- **Troubleshooting:** Common issues covered
- **Professionalism:** Shows thoroughness

---

## 📊 Code Statistics

### Backend
- **Total Lines:** ~1,500
- **Python Files:** 6
- **ML Modules:** 3
- **API Endpoints:** 5

### Frontend
- **HTML Version:** ~400 lines
- **React Version:** ~300 lines

### Documentation
- **Total Words:** ~15,000
- **Documentation Files:** 6
- **Code Comments:** ~500 lines

### Data
- **Training Samples:** 400+
- **Categories:** 6
- **Languages:** 3 (English, Hindi, Hinglish)

---

## 🔄 Data Flow Through Files

### Text Complaint Flow

```
1. frontend/index.html
   └─> User enters complaint
   
2. HTTP POST to backend/app/main.py
   └─> submit_text_complaint() endpoint
   
3. backend/app/ml/multilingual_embedder.py
   └─> encode() - Text to embedding
   
4. backend/app/ml/complaint_classifier.py
   └─> predict() - Embedding to category
   
5. backend/app/main.py
   └─> Return JSON response
   
6. frontend/index.html
   └─> Display result
```

### Voice Complaint Flow

```
1. frontend/index.html
   └─> User uploads audio
   
2. HTTP POST to backend/app/main.py
   └─> submit_voice_complaint() endpoint
   
3. backend/app/ml/speech_to_text.py
   └─> transcribe() - Audio to text
   
4. [Same as text flow from step 3]
```

### Training Flow

```
1. data/complaints.csv
   └─> Training data
   
2. backend/train_classifier.py
   └─> Load data
   
3. backend/app/ml/multilingual_embedder.py
   └─> Generate embeddings
   
4. backend/app/ml/complaint_classifier.py
   └─> Train classifier
   
5. backend/models/complaint_classifier.pkl
   └─> Save trained model
```

---

## 🎓 Learning Path

### For Understanding the System

**Recommended Reading Order:**
1. `README.md` - Overview
2. `PROJECT_STRUCTURE.md` - This file
3. `backend/app/ml/multilingual_embedder.py` - Core concept
4. `backend/app/ml/complaint_classifier.py` - Classification
5. `backend/app/main.py` - API
6. `frontend/index.html` - UI

### For Running the System

**Recommended Order:**
1. `INSTALLATION.md` - Setup
2. `QUICKSTART.md` - Quick start
3. `backend/test_system.py` - Verify
4. `frontend/index.html` - Test

### For Viva Preparation

**Recommended Order:**
1. `VIVA_GUIDE.md` - Q&A
2. `PROJECT_SUMMARY.md` - Overview
3. `backend/app/ml/` - Understand ML code
4. Practice demo

---

## 🔧 Customization Guide

### Add New Category

**Files to Modify:**
1. `data/complaints.csv` - Add training data
2. Run `backend/train_classifier.py` - Retrain
3. Done! No code changes needed

### Change Confidence Threshold

**Files to Modify:**
1. `backend/train_classifier.py` - Change `CONFIDENCE_THRESHOLD`
2. Retrain model

### Add New API Endpoint

**Files to Modify:**
1. `backend/app/main.py` - Add endpoint function
2. `frontend/index.html` - Add UI and API call

### Change Frontend Styling

**Files to Modify:**
1. `frontend/index.html` - Modify CSS section

---

## ✅ File Checklist

### Essential Files (Must Have)
- [x] `backend/app/main.py`
- [x] `backend/app/ml/multilingual_embedder.py`
- [x] `backend/app/ml/complaint_classifier.py`
- [x] `backend/train_classifier.py`
- [x] `backend/requirements.txt`
- [x] `data/complaints.csv`
- [x] `frontend/index.html`
- [x] `README.md`

### Optional Files (Nice to Have)
- [x] `backend/app/ml/speech_to_text.py` (for voice)
- [x] `backend/test_system.py` (for testing)
- [x] `frontend/App.jsx` (React version)
- [x] All documentation files

### Generated Files (Created During Setup)
- [ ] `backend/models/complaint_classifier.pkl` (after training)
- [ ] `backend/__pycache__/` (Python cache)
- [ ] `backend/app/__pycache__/` (Python cache)

---

**Understanding the project structure helps you navigate, modify, and explain the system effectively! 📁**
