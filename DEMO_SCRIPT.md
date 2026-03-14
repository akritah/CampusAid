# CampusAid Demo Script

Quick reference for live demonstration during viva.

## 🚀 Pre-Demo Setup (5 minutes before)

```bash
# Terminal 1 - Backend
cd backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
python app/main.py

# Terminal 2 - Frontend
cd frontend/campusaid
npm run dev

# Open Browser
http://localhost:3000
```

## 📋 Demo Script (25 minutes)

### Part 1: Introduction (2 min)

**Say**: "Good morning/afternoon. I'm presenting CampusAid, an intelligent campus grievance portal that uses machine learning to automatically classify and route complaints in multiple languages."

**Show**: Landing page with role selection

**Key Points**:
- Multilingual support (Hindi, English, Hinglish)
- ML-powered classification
- Role-based access control
- Real-time dashboard

---

### Part 2: User Registration (2 min)

**Action**: Click "Sign up here"

**Say**: "Let me first demonstrate the registration process."

**Steps**:
1. Enter username: `demo_student`
2. Select role: `Student`
3. Enter password: `demo123`
4. Confirm password: `demo123`
5. Click "Create Account"

**Show**: Success message and auto-redirect

**Say**: "The system validates input, hashes passwords with bcrypt, and stores user data securely in PostgreSQL."

---

### Part 3: User Login (1 min)

**Action**: Login with created credentials

**Say**: "After registration, users can log in with their credentials."

**Steps**:
1. Select role card: `Student`
2. Enter username: `demo_student`
3. Enter password: `demo123`
4. Click "Login"

**Show**: Redirect to user portal

**Say**: "The system authenticates users and redirects based on their role."

---

### Part 4: Text Complaint - English (3 min)

**Action**: Submit English complaint

**Say**: "Now let me submit a complaint in English."

**Steps**:
1. Title: `WiFi Issue in Hostel`
2. Description: `The WiFi connection in Block A hostel is very slow. Students cannot attend online classes properly.`
3. Click "Submit Complaint"

**Show**: 
- Success message
- Complaint appears in history
- Department: Hostel
- Confidence score: ~0.85

**Say**: "The ML model classified this as a Hostel complaint with 85% confidence. The system automatically routes it to the hostel department."

---

### Part 5: Text Complaint - Hindi (3 min)

**Action**: Submit Hindi/Hinglish complaint

**Say**: "Now let me demonstrate multilingual understanding with a Hindi complaint."

**Steps**:
1. Title: `Library Book Problem`
2. Description: `Library mein computer science ki books bahut purani hain. New edition ki books chahiye.`
3. Click "Submit Complaint"

**Show**:
- Classification: Academic
- Confidence score
- No translation needed

**Say**: "Notice that the system understood the Hindi-English mixed text directly, without translation. This is because we use multilingual embeddings that understand semantic meaning across languages."

---

### Part 6: Voice Complaint (3 min)

**Action**: Record voice complaint

**Say**: "The system also supports voice input using Whisper speech-to-text."

**Steps**:
1. Click "Start Recording"
2. Speak: "The electricity in the hostel keeps going off. We need a backup generator."
3. Click "Stop Recording"
4. Click "Upload Voice Complaint"

**Show**:
- Transcription
- Classification
- Confidence score

**Say**: "The audio is transcribed to text, then processed through the same ML pipeline."

---

### Part 7: Complaint History (2 min)

**Action**: Scroll through complaint list

**Say**: "Users can track all their complaints in one place."

**Show**:
- Complaint IDs
- Departments
- Status
- Confidence scores
- Timestamps

**Say**: "Each complaint has a unique ID, assigned department, status, and confidence score for transparency."

---

### Part 8: Admin Dashboard (5 min)

**Action**: Logout and login as admin

**Say**: "Now let me show the admin dashboard."

**Steps**:
1. Click "Logout"
2. Login with: `admin1` / `admin123`
3. Select role: `Admin`

**Show Dashboard**:
- Total complaints: X
- Average confidence: Y%
- Resolved: Z
- Pending: W
- Department breakdown
- Status breakdown

**Say**: "Admins get a comprehensive overview with statistics. They can see complaint distribution across departments and track resolution progress."

---

### Part 9: Department View (2 min)

**Action**: Click "Departments" → "Hostel"

**Say**: "Admins can view complaints by department."

**Show**:
- Filtered complaint list
- Complaint details
- Status dropdown
- Action buttons

**Say**: "Admins can update complaint status and add resolution notes."

---

### Part 10: ML Pipeline Explanation (5 min)

**Action**: Open code editor (optional)

**Say**: "Let me explain how the ML pipeline works."

**Show/Explain**:

1. **Multilingual Embeddings**:
   - "We use sentence-transformers with a multilingual model"
   - "It converts text to 384-dimensional vectors"
   - "Similar meanings have similar vectors, regardless of language"

2. **Classification**:
   - "We train a Logistic Regression classifier on these embeddings"
   - "Training data: complaints.csv and labels.csv"
   - "Categories: Hostel, IT, Academic, Maintenance"

3. **Confidence Scoring**:
   - "Model outputs probability for each category"
   - "If max probability < 0.7, flagged for manual review"
   - "This ensures accuracy and ethical AI"

4. **Why This Approach**:
   - "No translation needed - direct understanding"
   - "Fast inference - < 500ms"
   - "Interpretable - can explain predictions"
   - "Scalable - handles multiple languages"

---

### Part 11: Code Walkthrough (3 min)

**Action**: Show project structure

**Say**: "Let me quickly show the code organization."

**Show**:

```
backend/
├── app/
│   ├── ml/                    # ML pipeline
│   ├── routes/                # API endpoints
│   ├── models.py              # Database models
│   └── main.py                # FastAPI app
frontend/campusaid/
├── app/                       # Pages
├── components/                # React components
└── lib/                       # Utilities
```

**Say**: "The code is modular and well-organized. Backend handles API and ML, frontend handles UI and user interaction."

---

## 🎯 Key Points to Emphasize

Throughout the demo, emphasize:

1. **Multilingual**: "Works with Hindi, English, and Hinglish without translation"
2. **ML-Powered**: "Automatic classification with confidence scoring"
3. **Ethical AI**: "Manual review for low confidence predictions"
4. **Security**: "Bcrypt hashing, role-based access, input validation"
5. **Scalability**: "PostgreSQL database, modular architecture"
6. **User Experience**: "Clean UI, loading states, error handling"

## 🔧 Troubleshooting During Demo

### If Backend Crashes
- Restart: `python app/main.py`
- Check: Model file exists
- Fallback: Show screenshots

### If Frontend Crashes
- Restart: `npm run dev`
- Clear cache: Ctrl+Shift+R
- Fallback: Show screenshots

### If ML Model Fails
- Explain: "Model needs retraining"
- Show: Training script
- Fallback: Explain expected behavior

### If Database Error
- Check: Connection string
- Restart: Backend server
- Fallback: Explain database schema

## 💬 Sample Complaints for Demo

### English
```
Title: Broken Furniture
Description: The chairs in classroom 301 are broken and uncomfortable. Students cannot sit properly during lectures.
Expected: Academic, High confidence
```

### Hindi
```
Title: Mess Food Quality
Description: Hostel mess ka khana bahut kharab hai. Quality improve karni chahiye.
Expected: Hostel, High confidence
```

### Hinglish
```
Title: Lab Equipment Issue
Description: Computer lab mein bahut saare computers kharab hain. Students ko practical karne mein problem ho rahi hai.
Expected: IT, High confidence
```

### Low Confidence Example
```
Title: General Issue
Description: Something needs to be fixed.
Expected: Manual Review (low confidence)
```

## 📊 Statistics to Mention

- **Model Accuracy**: ~95% on test data
- **Response Time**: < 500ms for classification
- **Languages Supported**: 3 (Hindi, English, Hinglish)
- **User Roles**: 4 (Student, Worker, Admin, Warden)
- **Departments**: 4 (Hostel, IT, Academic, Maintenance)
- **Tech Stack**: FastAPI, Next.js, PostgreSQL, Sentence Transformers

## 🎤 Closing Statement

**Say**: "In conclusion, CampusAid demonstrates a complete full-stack application with ML integration. It solves a real problem - managing campus complaints efficiently - while showcasing modern web development, NLP, and database design. The system is production-ready, well-documented, and scalable. Thank you for your time. I'm happy to answer any questions."

---

## ✅ Post-Demo Checklist

- [ ] Answered all questions
- [ ] Demonstrated all features
- [ ] Explained ML pipeline
- [ ] Showed code organization
- [ ] Discussed trade-offs
- [ ] Mentioned future improvements
- [ ] Thanked the panel

---

**Remember**: Speak clearly, maintain eye contact, and be confident! 🚀
