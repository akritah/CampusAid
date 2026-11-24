# 🔧 CORE ALGORITHMS & PSEUDOCODE - CampusAid

## Overview
CampusAid processes complaints through a **4-stage pipeline**:
1. **Input Stage**: Accept text or voice complaints
2. **Conversion Stage**: Speech → Text (if needed)
3. **ML Stage**: Text → Category with confidence scoring
4. **Output Stage**: Return result or flag for manual review

---

## 🌐 MAIN API PIPELINE: Submit Complaint (Text or Voice)

### High-Level Flow
```
User Complaint (Text or Voice)
    ↓
    ├─→ If Voice: Speech-to-Text Conversion
    ↓
    └─→ Get text
    ↓
Generate Embeddings (Vector representation)
    ↓
Feed to Classifier (Predict category + confidence)
    ↓
Check Confidence Threshold
    ├─→ If confidence ≥ 60%: Auto-classify ✅
    └─→ If confidence < 60%: Flag for manual review ⚠️
    ↓
Store in Database & Return Result
```

---

## 📊 STAGE 1: INPUT HANDLING

### Algorithm: Handle Text or Voice Input
```
INPUT: complaint_source (text_string OR audio_file)

FUNCTION process_complaint_input(complaint_source):
    
    IF complaint_source is AUDIO_FILE:
        complaint_text ← convert_audio_to_text(audio_file)
    ELSE:
        complaint_text ← complaint_source (already text)
    
    RETURN complaint_text
```

### Pseudocode Example
```python
def submit_complaint_endpoint(
    complaint_text: Optional[str],
    audio_file: Optional[UploadFile]
):
    # Step 1: Determine input type
    if audio_file is provided:
        # Voice input path
        complaint_text = transcribe_voice(audio_file)
    else if complaint_text is provided:
        # Text input path (already have text)
        pass
    else:
        # Error: neither text nor audio provided
        return ERROR("Provide text or audio")
    
    # Step 2: Continue to next stage with complaint_text
    return classify_complaint(complaint_text)
```

---

## 🎤 STAGE 2: SPEECH-TO-TEXT CONVERSION (Optional)

### Algorithm: Convert Audio to Text using Whisper

```
INPUT: audio_file (MP3, WAV, M4A, etc.)

FUNCTION speech_to_text(audio_file):
    
    STEP 1: Load Whisper Model
        model ← Load "small" or "base" pretrained Whisper model
        (Model prefers faster-whisper variant for CPU efficiency)
    
    STEP 2: Load & Process Audio
        audio ← Load audio_file from disk
        audio ← Resample to 16kHz (standard for speech recognition)
    
    STEP 3: Transcribe Using Whisper
        transcription ← model.transcribe(
            audio,
            language = "auto"  // Auto-detect Hindi/English/Hinglish
            initial_prompt = "Campus complaint context"
        )
    
    STEP 4: Extract Text
        text ← transcription["text"]
    
    RETURN text
```

### Why Whisper?
- ✅ Supports Hindi, English, Hinglish, and 99+ languages
- ✅ Can run locally (no internet, free)
- ✅ Good accuracy on Indian accents
- ✅ Open-source

### Example Flow
```
Audio file (voice complaint) 
    ↓
[Whisper Model loads]
    ↓
[Audio resampled to 16kHz]
    ↓
[Whisper processes: "Water problem in hostel"]
    ↓
Text output: "Water problem in hostel"
```

---

## 🧠 STAGE 3: EMBEDDING GENERATION (The Core!)

### Algorithm: Convert Text to Numerical Vector (Embedding)

```
INPUT: complaint_text (in Hindi/English/Hinglish)

FUNCTION generate_embedding(complaint_text):
    
    STEP 1: Load Multilingual Embedding Model
        model ← Load "paraphrase-multilingual-MiniLM-L12-v2"
        (Pretrained model from sentence-transformers)
    
    STEP 2: Tokenize Text
        tokens ← model.tokenizer(complaint_text)
        // Converts text → numerical tokens the model understands
    
    STEP 3: Forward Pass Through Model
        embedding ← model.encode(complaint_text)
        // Processes tokens through 12 transformer layers
        // Output: 384-dimensional vector
    
    STEP 4: Normalize Embedding
        embedding ← normalize(embedding)  // L2 normalization
        // Makes all embeddings comparable
    
    RETURN embedding (384-dimensional vector)
```

### Why This Works Across Languages
```
Text in different languages with SAME MEANING:
├─ English: "Water not available in hostel"
├─ Hindi: "हॉस्टल में पानी नहीं है"
└─ Hinglish: "Hostel mein paani nahi hai"

ALL convert to:
embedding = [0.23, -0.45, 0.67, ..., 0.12]  // SAME or VERY SIMILAR

✓ Similarity score between any two: > 0.85
```

### Key Concept: Pretraining
```
We DON'T train this model ourselves because:
- Training requires: 100M+ text samples
- Training time: Weeks on GPU
- Cost: ₹10+ lakhs
- Expertise: PhD-level

Instead: Use PRETRAINED model → Trained by experts on billions of texts
         Then fine-tune or use as-is for our task (we use as-is)
```

---

## 🎯 STAGE 4: CLASSIFICATION WITH CONFIDENCE

### Algorithm: Predict Category Using Logistic Regression

```
INPUT: embedding (384-dimensional vector from STAGE 3)

FUNCTION classify_complaint(embedding):
    
    STEP 1: Load Trained Classifier
        classifier ← Load "complaint_classifier.pkl"
        // Logistic Regression trained on 500+ labeled complaints
    
    STEP 2: Generate Predictions
        category ← classifier.predict(embedding)
        // Returns single category (e.g., "Hostel", "IT")
        
        probabilities ← classifier.predict_proba(embedding)
        // Returns probability for each category:
        // {Hostel: 0.87, IT: 0.05, Academic: 0.08}
    
    STEP 3: Extract Confidence Score
        confidence = MAX(probabilities)
        // Max probability = confidence of predicted category
        // Example: 0.87 = 87% confident in "Hostel"
    
    STEP 4: Check Against Threshold
        THRESHOLD = 0.6 (60%)
        
        IF confidence >= THRESHOLD:
            flag_for_review = FALSE
            ✓ Result: AUTO-CLASSIFIED
        ELSE:
            flag_for_review = TRUE
            ⚠️ Result: MARKED FOR MANUAL REVIEW
    
    RETURN {
        category: category,
        confidence: confidence,
        needs_review: flag_for_review,
        all_probabilities: probabilities
    }
```

### Why Logistic Regression?
```
Simple linear model: P(category) = 1 / (1 + e^(-w·x + b))

Advantages:
✓ Fast (microseconds per prediction)
✓ Interpretable (easy to explain in viva)
✓ Works well with embeddings
✓ Low memory (small model file)

Alternatives considered (but not used):
✗ SVM: More complex, slower
✗ Neural Network: Overkill, needs more data
✗ Random Forest: Black-box, harder to explain
```

### Confidence Threshold Logic
```
              Threshold = 60%
                    ↓
Confidence   0%    20%   40%   60%   80%  100%
            |------|------|------|------|------|
Result      LOW                  HIGH
            │ MANUAL REVIEW      │ AUTO-CLASSIFY
            
Examples:
- Confidence 87% → "This is definitely Hostel" → Auto-classify ✓
- Confidence 55% → "Not sure... could be Hostel or Admin" → Manual review ⚠️
- Confidence 45% → "Very confused prediction" → Definitely manual review ⚠️
```

---

## 🔄 FULL PIPELINE PSEUDOCODE: End-to-End Example

### Scenario 1: Text Complaint in Hinglish
```
API CALL:
POST /submit-complaint
{
    "complaint_text": "Hostel ka paani nahi aa raha aaj se 2 din se"
}

EXECUTION:
1. Input Processing
   ├─ Input is text ✓
   └─ complaint_text = "Hostel ka paani nahi aa raha aaj se 2 din se"

2. Embedding Generation
   ├─ Load multilingual model
   ├─ Encode text → 384-dim vector
   └─ embedding = [0.12, -0.34, 0.56, ..., -0.89]

3. Classification
   ├─ Load pretrained Logistic Regression
   ├─ Predict: category = "Hostel"
   ├─ Confidence = 0.91 (91%)
   └─ Probabilities: {Hostel: 0.91, Infrastructure: 0.05, Admin: 0.04}

4. Threshold Check
   ├─ 0.91 >= 0.60? YES ✓
   └─ needs_review = FALSE

5. Database Storage
   ├─ Save complaint record
   ├─ Save prediction: Hostel, 91%, Auto-classified
   └─ Status: CLASSIFIED

RESPONSE:
{
    "complaint_id": 12345,
    "predicted_category": "Hostel",
    "confidence_score": 0.91,
    "needs_review": false,
    "status": "CLASSIFIED",
    "message": "Complaint auto-classified as Hostel"
}
```

### Scenario 2: Voice Complaint in Hindi
```
API CALL:
POST /voice-complaint
Files: 
    - complaint_audio: audio_file.mp3

EXECUTION:
1. Input Processing
   ├─ Input is audio ✓
   └─ complaint_text = None, audio_file = audio_file.mp3

2. Speech-to-Text Conversion
   ├─ Load Whisper model (small variant)
   ├─ Load & resample audio to 16kHz
   ├─ Transcribe with Hindi language detection
   └─ complaint_text = "पानी की समस्या है" → "Water problem"

3. Embedding Generation
   ├─ Load multilingual model
   ├─ Encode "Water problem" → 384-dim vector
   └─ embedding = [0.34, -0.12, 0.78, ..., 0.45]

4. Classification
   ├─ Load Logistic Regression
   ├─ Predict: category = "Hostel"
   ├─ Confidence = 0.73 (73%)
   └─ Probabilities: {Hostel: 0.73, Infrastructure: 0.15, IT: 0.12}

5. Threshold Check
   ├─ 0.73 >= 0.60? YES ✓
   └─ needs_review = FALSE

6. Database Storage
   ├─ Save complaint with transcribed text
   ├─ Save prediction: Hostel, 73%
   └─ Status: CLASSIFIED

RESPONSE:
{
    "complaint_id": 12346,
    "transcribed_text": "Water problem",
    "predicted_category": "Hostel",
    "confidence_score": 0.73,
    "needs_review": false,
    "status": "CLASSIFIED"
}
```

### Scenario 3: Ambiguous Complaint (Needs Manual Review)
```
API CALL:
POST /submit-complaint
{
    "complaint_text": "System not working"
}

EXECUTION:
1-2. Input & Embedding: [Same as before]

3. Classification
   ├─ Load Logistic Regression
   ├─ Predict: category = "IT"
   ├─ Confidence = 0.52 (52%)
   └─ Probabilities: {IT: 0.52, Infrastructure: 0.35, Academic: 0.13}
       (Could be IT system, infrastructure system, or academic system)

4. Threshold Check
   ├─ 0.52 >= 0.60? NO ✗
   ├─ confidence (52%) < threshold (60%)
   └─ needs_review = TRUE  ⚠️

5. Database Storage
   ├─ Save complaint
   ├─ Save prediction: IT, 52%, Low confidence
   └─ Status: PENDING_REVIEW

RESPONSE:
{
    "complaint_id": 12347,
    "predicted_category": "IT",
    "confidence_score": 0.52,
    "needs_review": true,
    "status": "PENDING_REVIEW",
    "message": "Low confidence prediction. Marked for manual review.",
    "all_probabilities": {"IT": 0.52, "Infrastructure": 0.35, "Academic": 0.13}
}

ADMIN VIEW:
[Shows "PENDING_REVIEW" complaints for human decision]
Admin can:
├─ Accept AI prediction: "IT"
├─ Override with correct category: "Infrastructure"
└─ Add notes: "Vague complaint, needs clarification"
```

---

## 📚 TRAINING PIPELINE (Offline - One-Time)

### Algorithm: Train the Logistic Regression Classifier

```
INPUT: 
    - complaints.csv (complaint texts)
    - labels.csv (correct categories for each complaint)

FUNCTION train_classifier():
    
    STEP 1: Load Data
        complaints ← READ complaints.csv
        labels ← READ labels.csv
        
    STEP 2: Generate Embeddings for All Complaints
        embeddings = []
        FOR EACH complaint IN complaints:
            emb ← model.encode(complaint)
            embeddings.APPEND(emb)
        
        // Result: N × 384 matrix (N = number of complaints)
    
    STEP 3: Split Data
        (X_train, X_test, y_train, y_test) ← 
            train_test_split(embeddings, labels, test_size=0.2)
        
        // 80% for training, 20% for testing
        // Uses stratified split (balanced classes)
    
    STEP 4: Train Logistic Regression
        classifier ← LogisticRegression(
            max_iterations=1000,
            regularization="L2",  // Prevent overfitting
            solver="LBFGS"
        )
        
        classifier.fit(X_train, y_train)
        // Learn weights: w (384-dim) and bias: b
    
    STEP 5: Evaluate on Test Set
        predictions ← classifier.predict(X_test)
        
        accuracy = COUNT(predictions == y_test) / LEN(y_test)
        // Example: 85% correct predictions
        
        PRINT classification_report(y_test, predictions)
        // Shows precision, recall, F1 for each category
    
    STEP 6: Save Model
        SAVE classifier TO "models/complaint_classifier.pkl"
        // ~1MB file, can be loaded in milliseconds
    
    RETURN accuracy, classification_report
```

### Training Data Structure
```
complaints.csv:
┌────┬─────────────────────────────────────┐
│ ID │ complaint_text                      │
├────┼─────────────────────────────────────┤
│  1 │ "Hot water not available"           │
│  2 │ "WiFi not working in room 301"      │
│  3 │ "Teacher syllabus incomplete"       │
│ ...│ ...                                 │
└────┴─────────────────────────────────────┘

labels.csv:
┌────┬──────────────┐
│ ID │ category     │
├────┼──────────────┤
│  1 │ "Hostel"     │
│  2 │ "IT"         │
│  3 │ "Academic"   │
│ ...│ ...          │
└────┴──────────────┘

After embedding:
┌────┬────────────────────────────────────────┬──────────────┐
│ ID │ embedding (384-dim vector)             │ category     │
├────┼────────────────────────────────────────┼──────────────┤
│  1 │ [0.23, -0.45, 0.67, ..., 0.12]        │ "Hostel"     │
│  2 │ [-0.12, 0.34, -0.56, ..., 0.89]       │ "IT"         │
│  3 │ [0.45, 0.12, -0.34, ..., -0.67]       │ "Academic"   │
│ ...│ ...                                    │ ...          │
└────┴────────────────────────────────────────┴──────────────┘
```

### Mathematical Formula: Logistic Regression

For each category:
```
P(category_i | complaint) = 

         1
    ──────────────────────────────────
    1 + e^(-(w_i · x + b_i))

where:
- w_i = learned weights for category_i (384 values)
- x = complaint embedding (384 values)
- b_i = learned bias for category_i (1 value)
- · = dot product (sum of element-wise products)
```

---

## 🔗 DATA FLOW DIAGRAM

```
┌──────────────────────────┐
│   USER INPUT             │
├──────────────────────────┤
│ ├─ Text complaint       │
│ └─ Voice complaint      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ SPEECH-TO-TEXT           │
│ (if voice input)         │
├──────────────────────────┤
│ Whisper model            │
│ Audio → Text             │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ EMBEDDING GENERATION     │
├──────────────────────────┤
│ Sentence Transformer     │
│ Text → 384-dim vector    │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ CLASSIFICATION           │
├──────────────────────────┤
│ Logistic Regression      │
│ Embedding → Category     │
│ + Confidence score       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ CONFIDENCE CHECK         │
├──────────────────────────┤
│ confidence >= 60%?       │
├──────────────────────────┤
│ YES: Auto-classify ✓     │
│ NO: Manual review ⚠️      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ DATABASE STORAGE         │
├──────────────────────────┤
│ Save complaint           │
│ Save prediction          │
│ Save status              │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ API RESPONSE             │
├──────────────────────────┤
│ Return result to user    │
└──────────────────────────┘
```

---

## ⚡ COMPLEXITY ANALYSIS

### Time Complexity (Per Complaint)

| Stage | Operation | Time | Notes |
|-------|-----------|------|-------|
| 1 | Input validation | O(1) | Constant |
| 2 | Speech-to-text | O(n) | n = audio duration (seconds) |
| 3 | Embedding generation | O(m) | m = text length (tokens) |
| 4 | Classification | O(1) | Simple dot product |
| 5 | Threshold check | O(1) | Constant |
| **Total** | **Full pipeline** | **O(m + n)** | Dominated by Whisper & embedding |

### Practical Times (Average Complaint)
```
Text complaint: ~50-100ms
├─ Embedding: 30-50ms
├─ Classification: 1ms
└─ DB storage: 10-30ms

Voice complaint (5 sec audio): ~2-5 seconds
├─ Whisper transcription: 1.5-3s
├─ Embedding: 30-50ms
├─ Classification: 1ms
└─ DB storage: 10-30ms
```

### Space Complexity
```
Embedder model: ~420MB (downloaded once, loaded in RAM)
Classifier model: ~1MB (pickled Logistic Regression)
Per complaint:
├─ Embedding vector: 384 floats = ~1.5KB
├─ Text storage: ~500 bytes
└─ Metadata: ~200 bytes
```

---

## 🎓 Key Concepts Summary

| Concept | What | Why | How |
|---------|------|-----|-----|
| **Embeddings** | Text → Numbers | Computers need numbers | Sentence Transformer (pretrained) |
| **Multilingual** | Same embedding for similar text in different languages | No translation needed | Trained on billions of sentences |
| **Logistic Regression** | Simple linear classifier | Fast, interpretable, works well with embeddings | sklearn implementation |
| **Confidence Threshold** | Quality control | Flag uncertain predictions | 60% threshold = balance accuracy & review load |
| **Whisper** | Audio → Text | Support voice input | OpenAI open-source model |

---

## 📖 Algorithm Complexity & Efficiency

### Why This Architecture Works

1. **Pretrained Models**: No need to train from scratch
   - Embedding model: Trained on billions of multilingual sentences
   - Saves weeks of computation and millions in compute costs

2. **Simple Classifier**: Logistic Regression is perfect for embeddings
   - Embeddings capture semantic meaning
   - Linear model sufficient for classification
   - Much faster than deep neural networks

3. **Confidence Threshold**: Ethical AI practice
   - Uncertain predictions → Human review
   - Prevents wrong categorizations
   - Maintains system trustworthiness

4. **Single Pipeline**: Text and Voice use same core logic
   - Whisper converts voice → text
   - Rest of pipeline identical
   - Code reuse and maintainability

---

## 🔧 Implementation Checklist

### For Production Use
- [ ] Model files cached and loaded efficiently
- [ ] Batch processing for high-volume submissions
- [ ] Async/await for I/O operations
- [ ] Error handling for edge cases
- [ ] Logging for debugging
- [ ] Rate limiting and security checks
- [ ] Database transactions for data consistency
- [ ] Monitoring and alerts for low confidence scores

### For Viva/Presentation
- [ ] Understand each stage thoroughly
- [ ] Know mathematical principles behind Logistic Regression
- [ ] Be able to explain why pretrained models are used
- [ ] Understand confidence threshold purpose
- [ ] Have examples ready (text, voice, ambiguous cases)
- [ ] Be prepared to draw the pipeline diagram
