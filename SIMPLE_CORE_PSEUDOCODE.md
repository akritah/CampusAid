# 🔧 SIMPLE CORE FUNCTIONALITY PSEUDOCODE - CampusAid

---

## 📌 Main Pipeline (4 Steps)

```
User Complaint (Text or Voice)
         ↓
    Speech-to-Text (if voice)
         ↓
    Generate Embeddings
         ↓
    Predict Category
         ↓
    Check Confidence
         ↓
    Store & Return Result
```

---

## STEP 1: Accept Input

```python
FUNCTION accept_complaint(input_text OR audio_file):
    
    IF input is TEXT:
        complaint_text = input_text
    
    ELSE IF input is AUDIO:
        complaint_text = convert_audio_to_text(audio_file)
    
    RETURN complaint_text
```

---

## STEP 2: Generate Embeddings (Text → Vector)

```python
FUNCTION generate_embedding(complaint_text):
    
    // Load pretrained multilingual model
    model = load_model("paraphrase-multilingual-MiniLM-L12-v2")
    
    // Convert text to 384-dimensional vector
    embedding = model.encode(complaint_text)
    
    RETURN embedding  // [0.23, -0.45, 0.67, ..., 0.12]
```

---

## STEP 3: Classify Complaint

```python
FUNCTION classify_complaint(embedding):
    
    // Load trained Logistic Regression model
    classifier = load_model("complaint_classifier.pkl")
    
    // Predict category
    category = classifier.predict(embedding)
    
    // Get confidence (probability)
    confidence = classifier.predict_proba(embedding).max()
    
    RETURN {
        category: category,          // "Hostel", "IT", etc.
        confidence: confidence       // 0 to 1
    }
```

---

## STEP 4: Check Confidence Threshold

```python
FUNCTION check_confidence(prediction):
    
    THRESHOLD = 0.6  // 60%
    
    IF prediction.confidence >= THRESHOLD:
        needs_review = FALSE  // Auto-classify ✓
    ELSE:
        needs_review = TRUE   // Flag for manual review ⚠️
    
    RETURN {
        category: prediction.category,
        confidence: prediction.confidence,
        needs_review: needs_review
    }
```

---

## STEP 5: Store in Database

```python
FUNCTION store_complaint(result):
    
    // Save to database
    complaint = create_record({
        text: complaint_text,
        category: result.category,
        confidence: result.confidence,
        needs_review: result.needs_review,
        created_at: NOW()
    })
    
    RETURN complaint
```

---

## COMPLETE FLOW - Example

```python
// User submits: "Hot water nahi available"

// STEP 1: Input
complaint_text = "Hot water nahi available"

// STEP 2: Embedding
embedding = [0.12, -0.34, 0.56, ..., -0.89]  // 384 numbers

// STEP 3: Classification
category = "Hostel"
confidence = 0.91  // 91%

// STEP 4: Threshold Check
91% >= 60%? YES ✓
needs_review = FALSE

// STEP 5: Store
Save to database with status: AUTO_CLASSIFIED

// RESULT:
{
    category: "Hostel",
    confidence: 0.91,
    needs_review: FALSE
}
```

---

## FOR VOICE COMPLAINTS - Add One Step

```python
// Between Step 1 and Step 2:

FUNCTION transcribe_voice(audio_file):
    
    // Load Whisper model
    model = load_model("whisper-small")
    
    // Convert audio to text
    text = model.transcribe(audio_file)
    
    RETURN text  // "Water problem in hostel"
```

---

## TRAINING - One-Time Setup

```python
FUNCTION train_classifier(complaints_list, labels_list):
    
    // Load embedder
    embedder = MultilingualEmbedder()
    
    // Convert all texts to embeddings
    embeddings = embedder.encode_batch(complaints_list)
    
    // Train Logistic Regression
    classifier = LogisticRegression()
    classifier.fit(embeddings, labels_list)
    
    // Save model
    save_model(classifier, "complaint_classifier.pkl")
```

---

## Key Variables

| Variable | Type | Example | Purpose |
|----------|------|---------|---------|
| complaint_text | String | "Hot water not available" | User's complaint |
| embedding | Vector (384 numbers) | [0.23, -0.45, ...] | Numerical representation |
| category | String | "Hostel" | Predicted department |
| confidence | Float (0-1) | 0.91 | How sure the model is |
| needs_review | Boolean | FALSE | Manual review needed? |
| THRESHOLD | Float | 0.6 | Confidence cutoff |

---

## That's It! 🎉

The entire system in 50 lines of pseudocode:
- Text/Voice Input
- Embedding Generation
- Category Prediction
- Confidence Check
- Database Storage
