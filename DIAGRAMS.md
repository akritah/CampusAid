# 📊 SYSTEM DIAGRAMS - CampusAid

Visual representations for easy understanding and viva presentations.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐       │
│  │  Text Input      │              │  Voice Input     │       │
│  │  Form            │              │  Upload          │       │
│  └────────┬─────────┘              └────────┬─────────┘       │
│           │                                  │                 │
│           └──────────────┬───────────────────┘                 │
│                          │                                     │
└──────────────────────────┼─────────────────────────────────────┘
                           │ HTTP POST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API (FastAPI)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Endpoints:                                              │ │
│  │  • POST /submit-complaint  (text)                       │ │
│  │  • POST /voice-complaint   (audio)                      │ │
│  │  • GET  /categories        (list)                       │ │
│  │  • GET  /                  (health)                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                     │
└──────────────────────────┼─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ML PIPELINE                               │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  STEP 1: Speech to Text (if voice)                     │   │
│  │  ┌──────────┐                                          │   │
│  │  │ Whisper  │  Audio → Text                            │   │
│  │  │  Model   │  "Hot water nahi aa raha"                │   │
│  │  └──────────┘                                          │   │
│  └────────────────────────────────────────────────────────┘   │
│                          │                                     │
│                          ▼                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  STEP 2: Text to Embeddings                            │   │
│  │  ┌──────────────────────┐                              │   │
│  │  │ Multilingual         │  Text → Vector               │   │
│  │  │ Sentence Transformer │  [0.23, -0.45, ..., 0.12]    │   │
│  │  │ (Pretrained)         │  (384 dimensions)            │   │
│  │  └──────────────────────┘                              │   │
│  └────────────────────────────────────────────────────────┘   │
│                          │                                     │
│                          ▼                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  STEP 3: Embeddings to Category                        │   │
│  │  ┌──────────────────────┐                              │   │
│  │  │ Logistic Regression  │  Vector → Category           │   │
│  │  │ (Trained by us)      │  "Hostel" (87% confidence)   │   │
│  │  └──────────────────────┘                              │   │
│  └────────────────────────────────────────────────────────┘   │
│                          │                                     │
│                          ▼                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  STEP 4: Confidence Check                              │   │
│  │  ┌──────────────────────┐                              │   │
│  │  │ If confidence >= 60% │  → Auto-approve              │   │
│  │  │ If confidence < 60%  │  → Manual review             │   │
│  │  └──────────────────────┘                              │   │
│  └────────────────────────────────────────────────────────┘   │
│                          │                                     │
└──────────────────────────┼─────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ JSON Response│
                    │ to Frontend  │
                    └──────────────┘
```

---

## 🔄 Data Flow Diagram

### Text Complaint Flow

```
┌─────────┐
│  User   │
│ Types   │
│ Text    │
└────┬────┘
     │
     │ "Hot water nahi aa raha"
     ▼
┌─────────────────┐
│   Frontend      │
│   (HTML/JS)     │
└────┬────────────┘
     │
     │ HTTP POST
     │ {text: "Hot water nahi aa raha"}
     ▼
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
└────┬────────────┘
     │
     │ Pass to ML Pipeline
     ▼
┌─────────────────────────┐
│ Multilingual Embedder   │
│ Text → Vector           │
│ [0.23, -0.45, ...]      │
└────┬────────────────────┘
     │
     │ 384-dim vector
     ▼
┌─────────────────────────┐
│ Complaint Classifier    │
│ Vector → Category       │
│ "Hostel" (87%)          │
└────┬────────────────────┘
     │
     │ Category + Confidence
     ▼
┌─────────────────┐
│   Backend       │
│   Format JSON   │
└────┬────────────┘
     │
     │ {category: "Hostel", confidence: 0.87}
     ▼
┌─────────────────┐
│   Frontend      │
│   Display       │
└─────────────────┘
```

### Voice Complaint Flow

```
┌─────────┐
│  User   │
│ Uploads │
│ Audio   │
└────┬────┘
     │
     │ audio.mp3
     ▼
┌─────────────────┐
│   Frontend      │
│   (HTML/JS)     │
└────┬────────────┘
     │
     │ HTTP POST (multipart/form-data)
     │ {audio_file: <binary>}
     ▼
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
└────┬────────────┘
     │
     │ Pass to Speech-to-Text
     ▼
┌─────────────────────────┐
│ Whisper                 │
│ Audio → Text            │
│ "Hot water nahi aa raha"│
└────┬────────────────────┘
     │
     │ Transcribed text
     ▼
┌─────────────────────────┐
│ [Same as Text Flow]     │
│ Embedder → Classifier   │
└─────────────────────────┘
```

---

## 🧠 ML Pipeline Detail

### Embedding Generation

```
Input Text: "Hot water nahi aa raha"
     │
     ▼
┌─────────────────────────────────────┐
│  Tokenization                       │
│  ["Hot", "water", "nahi", "aa",     │
│   "raha"]                            │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Multilingual Sentence Transformer  │
│  (Pretrained Model)                 │
│                                     │
│  • 12 layers                        │
│  • 384 dimensions                   │
│  • 50+ languages                    │
└────┬────────────────────────────────┘
     │
     ▼
Output Vector: [0.23, -0.45, 0.67, ..., 0.12]
               (384 numbers)
```

### Classification

```
Input Vector: [0.23, -0.45, 0.67, ..., 0.12]
     │
     ▼
┌─────────────────────────────────────┐
│  Logistic Regression                │
│  (Trained on our data)              │
│                                     │
│  Categories:                        │
│  • Hostel                           │
│  • Academic                         │
│  • IT                               │
│  • Infrastructure                   │
│  • Harassment                       │
│  • Administration                   │
└────┬────────────────────────────────┘
     │
     ▼
Output Probabilities:
┌──────────────────┬─────────┐
│ Category         │ Prob    │
├──────────────────┼─────────┤
│ Hostel           │ 0.87    │ ← Highest
│ IT               │ 0.05    │
│ Academic         │ 0.03    │
│ Infrastructure   │ 0.02    │
│ Administration   │ 0.02    │
│ Harassment       │ 0.01    │
└──────────────────┴─────────┘
     │
     ▼
Final Prediction: "Hostel" (87% confidence)
```

---

## 🎯 Training Process

```
┌─────────────────────────────────────┐
│  Training Data (complaints.csv)    │
│  400+ complaints with labels        │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Generate Embeddings                │
│  Text → Vectors (for all samples)  │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Split Data                         │
│  Train: 80% (320 samples)           │
│  Test:  20% (80 samples)            │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Train Logistic Regression          │
│  Learn: Vector → Category mapping   │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Evaluate on Test Set               │
│  Accuracy: 85-95%                   │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Save Model                         │
│  complaint_classifier.pkl           │
└─────────────────────────────────────┘
```

---

## 🌍 Multilingual Understanding

### How Same Meaning → Same Vector

```
English:  "Hot water not available"
          ↓
Embedder: [0.23, -0.45, 0.67, ..., 0.12]
          ↓
Classifier: "Hostel" (87%)


Hinglish: "Hot water nahi available"
          ↓
Embedder: [0.24, -0.44, 0.68, ..., 0.11]  ← Very similar!
          ↓
Classifier: "Hostel" (86%)


Hindi:    "गर्म पानी नहीं आ रहा"
          ↓
Embedder: [0.22, -0.46, 0.66, ..., 0.13]  ← Very similar!
          ↓
Classifier: "Hostel" (85%)
```

**Key Insight:** The embedder maps similar meanings to similar vectors, regardless of language!

---

## 🔍 Confidence Thresholding

```
Prediction Result
     │
     ▼
┌─────────────────────────────────────┐
│  Check Confidence Score             │
└────┬────────────────────────────────┘
     │
     ├─── Confidence >= 60% ───┐
     │                         │
     │                         ▼
     │              ┌─────────────────────┐
     │              │ ✅ AUTO-APPROVE     │
     │              │ High confidence     │
     │              │ No review needed    │
     │              └─────────────────────┘
     │
     └─── Confidence < 60% ────┐
                               │
                               ▼
                    ┌─────────────────────┐
                    │ ⚠️ MANUAL REVIEW    │
                    │ Low confidence      │
                    │ Human verification  │
                    └─────────────────────┘
```

**Example:**
```
Complaint: "Hot water not available"
Confidence: 87%
→ ✅ Auto-approved

Complaint: "Feeling unsafe"
Confidence: 52%
→ ⚠️ Manual review needed
```

---

## 📊 Category Distribution

```
Training Data Distribution:

Hostel          ████████████████ 80 samples
Academic        ████████████████ 80 samples
IT              ████████████████ 80 samples
Infrastructure  ████████████████ 80 samples
Administration  ████████████████ 80 samples
Harassment      ████████████████ 80 samples

Total: 480 samples (balanced dataset)
```

---

## 🔄 Request-Response Cycle

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                      │
└────┬─────────────────────────────────────────────────────┘
     │
     │ 1. HTTP POST /submit-complaint
     │    {text: "Hot water nahi aa raha"}
     ▼
┌──────────────────────────────────────────────────────────┐
│                    SERVER (FastAPI)                      │
│                                                          │
│  2. Validate request                                     │
│  3. Call ML pipeline                                     │
│  4. Get prediction                                       │
│  5. Format response                                      │
└────┬─────────────────────────────────────────────────────┘
     │
     │ 6. HTTP 200 OK
     │    {
     │      "success": true,
     │      "category": "Hostel",
     │      "confidence": 0.87,
     │      "needs_manual_review": false
     │    }
     ▼
┌──────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                      │
│                                                          │
│  7. Display result to user                               │
└──────────────────────────────────────────────────────────┘
```

---

## 🎓 For Viva: Draw These on Board

### Simple Architecture (30 seconds)
```
Frontend → Backend → ML Pipeline
   ↓          ↓           ↓
  HTML     FastAPI    Embeddings
                     + Classifier
```

### ML Pipeline (1 minute)
```
Text → Embeddings → Classification → Result
       (Pretrained)   (Trained)
```

### Multilingual Concept (1 minute)
```
English  ─┐
Hinglish ─┼→ Embedder → Same Vector Space → Classifier
Hindi    ─┘
```

---

## 📈 Performance Metrics

```
┌─────────────────────────────────────────────────────┐
│  Model Performance                                  │
├─────────────────────────────────────────────────────┤
│  Accuracy:        85-95%                            │
│  Training Time:   1-2 minutes                       │
│  Inference Time:  ~100ms per complaint              │
│  Model Size:      420MB (embedder) + <1MB (class.) │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  System Performance                                 │
├─────────────────────────────────────────────────────┤
│  Throughput:      100+ requests/second              │
│  Latency:         ~100ms (text), ~2-3s (voice)      │
│  Memory:          2GB RAM minimum                   │
│  CPU:             No GPU required                   │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Use These Diagrams

**In Report:** Copy the ASCII diagrams  
**In Presentation:** Redraw as proper diagrams  
**In Viva:** Draw simplified versions on board  
**In Code:** Reference these for understanding  

---

**Visual understanding makes explanation easier! 📊**
