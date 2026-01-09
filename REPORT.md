# Fynd AI Intern – Take Home Assessment 2.0
## Technical Report

**Author:** Yashika Tirkey  
**Email:** riyashika20@gmail.com  
**GitHub Repository:** https://github.com/yashikart/AI-Feedback-System.git

---

## Executive Summary

This report documents the implementation of two interconnected tasks: (1) Rating Prediction via Prompting using multiple LLM approaches, and (2) a production-ready Two-Dashboard AI Feedback System. The project demonstrates proficiency in prompt engineering, web application development, and system architecture design.

**Key Achievements:**
- Implemented and evaluated three distinct prompting approaches for rating prediction
- Built a fully functional web application with separate User and Admin dashboards
- Deployed both dashboards on Render with persistent data storage
- Integrated AI-powered features including rating prediction, summarization, and action recommendations

---

## Table of Contents

1. [Task 1: Rating Prediction via Prompting](#task-1-rating-prediction-via-prompting)
2. [Task 2: Two-Dashboard AI Feedback System](#task-2-two-dashboard-ai-feedback-system)
3. [Overall Architecture](#overall-architecture)
4. [Design Decisions](#design-decisions)
5. [Evaluation and Results](#evaluation-and-results)
6. [System Behavior and Trade-offs](#system-behavior-and-trade-offs)
7. [Limitations and Future Work](#limitations-and-future-work)
8. [Conclusion](#conclusion)

---

## Task 1: Rating Prediction via Prompting

### Problem Statement

Design and evaluate multiple prompting approaches to classify Yelp reviews into 1-5 star ratings, returning structured JSON output with explanations.

### Dataset

- **Source:** Yelp Reviews dataset from Kaggle
- **Sample Size:** 200 reviews (balanced across all 5 rating classes)
- **Preprocessing:** Balanced sampling to ensure equal representation of each rating class

### Approach and Methodology

I implemented three distinct prompting strategies, each with different design philosophies:

#### Approach 0: Zero-Shot Prompting

**Design Philosophy:** Direct classification without examples, relying on the model's pre-trained knowledge.

**Prompt Structure:**
```
You are a sentiment analysis expert.

Classify the Yelp review into a star rating from 1 to 5.

1 = Very negative
2 = Mostly negative
3 = Neutral or mixed
4 = Mostly positive
5 = Extremely positive

Return ONLY one number (1–5). No explanation.

Review: [review_text]
Answer:
```

**Model:** Mistral-7B-Instruct (via OpenRouter)

**Rationale:** This baseline approach tests the model's inherent understanding of sentiment and rating scales without any guidance or examples.

**Results:**
- **Accuracy:** 0.630 (63.0%)
- **JSON Validity:** N/A (returns single number)
- **Reliability:** Medium

**Analysis:** The model showed reasonable performance but struggled with nuanced reviews where sentiment doesn't directly map to ratings. For instance, a review mentioning "good food but slow service" could be interpreted as either 3 or 4 stars depending on emphasis.

---

#### Approach 1: Few-Shot Prompting

**Design Philosophy:** Provide labeled examples to guide the model's understanding of rating criteria.

**Prompt Structure:**
```
You are classifying Yelp reviews into star ratings.

IMPORTANT:
Yelp stars are NOT only sentiment.
They represent customer satisfaction relative to expectations.

Use these rules STRICTLY:
- 5 stars: extremely positive, no complaints at all
- 4 stars: positive overall, but mentions any minor issue
- 3 stars: mixed, average, or "okay"
- 2 stars: mostly negative but not terrible
- 1 star: very negative, angry, or warning others

Examples:

Review: "Amazing food and great service!"
Stars: 5

Review: "Food was great but service was slow."
Stars: 4

Review: "It was okay, nothing special."
Stars: 3

Review: "Disappointing experience, not worth the price."
Stars: 2

Review: "Worst experience ever. Never coming back."
Stars: 1

Now classify this review using the SAME logic.

Review: [review_text]
Return ONLY one number (1–5).
Answer:
```

**Model:** Mistral-7B-Instruct (via OpenRouter)

**Rationale:** By providing concrete examples, the model learns the distinction between sentiment and actual rating criteria. The examples demonstrate that 4-star reviews can have positive sentiment but include minor complaints.

**Results:**
- **Accuracy:** 0.610 (61.0%)
- **JSON Validity:** N/A (returns single number)
- **Reliability:** Medium

**Analysis:** Surprisingly, few-shot prompting performed slightly worse than zero-shot. This suggests that the examples may have been too simplistic or that Mistral-7B-Instruct doesn't benefit significantly from few-shot examples for this task. The model may have overfitted to the examples rather than learning the general pattern.

---

#### Approach 2: Reasoning-Guided JSON Prompting

**Design Philosophy:** Force structured reasoning and explicit explanation through JSON output format.

**Prompt Structure:**
```
You are a strict JSON generator.

TASK:
Classify the Yelp review into a star rating from 1 to 5.

Star scale:
1 = Very negative
2 = Mostly negative
3 = Neutral or mixed
4 = Mostly positive with minor issues
5 = Extremely positive with no issues

RULES:
- Return ONLY valid JSON
- Do NOT include any text outside JSON
- Do NOT add markdown
- Explanation must be ONE short sentence

OUTPUT FORMAT (exact):
{"predicted_stars": 4, "explanation": "Short justification"}

Review: """[review_text]"""
```

**Model:** GPT-3.5-Turbo (via OpenRouter)

**Rationale:** 
1. **Structured Output:** JSON format ensures parseable, consistent responses
2. **Explanation Requirement:** Forces the model to reason through its decision
3. **Strict Formatting:** Reduces parsing errors and improves reliability
4. **Model Choice:** GPT-3.5-Turbo has better JSON generation capabilities than Mistral-7B

**Results:**
- **Accuracy:** 0.635 (63.5%)
- **JSON Validity:** 1.0 (100%)
- **Reliability:** High

**Analysis:** This approach achieved the highest accuracy and perfect JSON validity. The requirement for explanation likely improved the model's reasoning process. The structured format also made error handling more robust.

---

### Prompt Iterations and Improvements

#### Iteration 1: Initial Zero-Shot Attempt
- **Issue:** Model sometimes returned explanations along with numbers
- **Fix:** Added explicit instruction "Return ONLY one number (1–5). No explanation."

#### Iteration 2: Few-Shot Refinement
- **Issue:** Examples were too generic
- **Fix:** Added specific examples showing edge cases (e.g., positive sentiment with minor issues = 4 stars)

#### Iteration 3: JSON Format Introduction
- **Issue:** Parsing errors with free-form text responses
- **Fix:** Switched to strict JSON format with explicit schema
- **Enhancement:** Added explanation field to force reasoning

#### Iteration 4: Model Selection
- **Issue:** Mistral-7B struggled with JSON formatting
- **Fix:** Switched to GPT-3.5-Turbo for better JSON generation
- **Result:** Achieved 100% JSON validity rate

---

### Evaluation Methodology

#### Dataset Preparation
1. Loaded Yelp Reviews dataset
2. Balanced sampling: 40 reviews per rating class (1-5 stars)
3. Total evaluation set: 200 reviews
4. Random seed: 42 (for reproducibility)

#### Metrics
1. **Accuracy:** Percentage of correctly predicted ratings
2. **JSON Validity Rate:** Percentage of responses that are valid JSON
3. **Reliability:** Qualitative assessment based on consistency and error handling

#### Evaluation Process
- Each approach tested on the same 200-review dataset
- Results compared using classification reports
- Error analysis performed on misclassified examples

---

### Results Comparison

| Approach | Prompt Design | Model Used | Accuracy | JSON Validity Rate | Reliability |
|----------|---------------|------------|----------|-------------------|-------------|
| 0 | Zero-shot Prompting | Mistral-7B-Instruct | 0.630 | N/A | Medium |
| 1 | Few-shot Prompting | Mistral-7B-Instruct | 0.610 | N/A | Medium |
| 2 | Reasoning-guided JSON Prompting | GPT-3.5-Turbo | 0.635 | 1.0 | High |

### Discussion of Results

**Key Findings:**

1. **Zero-Shot vs Few-Shot:** Contrary to expectations, few-shot prompting performed worse. This suggests that for this specific task and model, explicit examples may have introduced confusion rather than clarity.

2. **JSON Format Advantage:** The reasoning-guided JSON approach achieved:
   - Highest accuracy (63.5%)
   - Perfect JSON validity (100%)
   - Highest reliability due to structured output

3. **Model Selection Impact:** GPT-3.5-Turbo's superior JSON generation capabilities were crucial for Approach 2's success.

4. **Explanation Requirement:** Requiring explanations likely improved accuracy by forcing the model to reason through its decisions rather than making quick judgments.

**Trade-offs:**

- **Approach 0 (Zero-shot):** Fast and simple but less reliable
- **Approach 1 (Few-shot):** More context but potentially confusing examples
- **Approach 2 (JSON):** Most reliable but requires more tokens and processing time

**Selected Approach for Task 2:**

Approach 2 (Reasoning-guided JSON Prompting) was selected for integration into Task 2 due to its:
- Highest accuracy
- Perfect JSON validity (critical for production systems)
- High reliability
- Structured output format

---

## Task 2: Two-Dashboard AI Feedback System

### Problem Statement

Build a production-ready web application with two dashboards (User and Admin) that collect, process, and display customer feedback using AI-powered features.

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Dashboard                        │
│                    (Next.js Static Site)                     │
│  • Star Rating Selection (1-5)                                │
│  • Review Text Input                                          │
│  • AI Response Display                                        │
│  • Rating Prediction Comparison                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP POST /api/submit
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    Backend API (FastAPI)                      │
│                    (Render Web Service)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  LLM Processing Layer                                 │   │
│  │  • Rating Prediction (Task 1 Approach 2)             │   │
│  │  • User Response Generation                           │   │
│  │  • Review Summarization                               │   │
│  │  • Recommended Actions                                │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Database Layer (SQLite)                             │   │
│  │  • Submissions Storage                               │   │
│  │  • Rating Predictions                                │   │
│  │  • AI Responses                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP GET /api/submissions
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                      Admin Dashboard                          │
│                    (Next.js Static Site)                     │
│  • Live Submissions List                                     │
│  • Analytics Dashboard                                       │
│  • Rating Filters                                            │
│  • Auto-refresh (5 seconds)                                  │
│  • Mismatch Detection                                        │
└─────────────────────────────────────────────────────────────┘
```

### Design Decisions

#### 1. Technology Stack

**Backend: FastAPI (Python)**
- **Rationale:** 
  - Fast, modern Python framework
  - Automatic API documentation
  - Built-in validation with Pydantic
  - Easy deployment on Render
  - Excellent async support for LLM calls

**Frontend: Next.js (React)**
- **Rationale:**
  - Production-optimized React framework
  - Static export capability for Render
  - Server-side rendering support (if needed)
  - Easy deployment
  - Modern React patterns

**Database: SQLite**
- **Rationale:**
  - Simple file-based storage
  - No external dependencies
  - Perfect for MVP
  - Easy to upgrade to PostgreSQL later
  - Automatic migrations supported

**LLM Provider: OpenRouter**
- **Rationale:**
  - Consistent with Task 1
  - Free tier available
  - Multiple model support
  - Reliable API
  - Same API key for both tasks

#### 2. Architecture Patterns

**Separation of Concerns:**
- Frontend: Pure presentation layer, no business logic
- Backend: All LLM processing, data persistence, API logic
- Database: Data storage and retrieval

**Server-Side LLM Processing:**
- All LLM calls made from backend
- Protects API keys
- Centralized error handling
- Cost control
- Consistent with requirements

**RESTful API Design:**
- Clear endpoint structure (`/api/submit`, `/api/submissions`)
- JSON request/response schemas
- Proper HTTP methods
- Error handling with status codes

#### 3. User Dashboard Design

**Features Implemented:**
1. **Star Rating Selector:** Interactive 5-star rating system
2. **Review Input:** Textarea with character counter (max 5000)
3. **Form Validation:** Client-side validation before submission
4. **AI Response Display:** Shows personalized response after submission
5. **Rating Prediction:** Displays AI-predicted rating vs user-selected rating
6. **Comparison Indicator:** Visual feedback for rating matches/mismatches
7. **Error Handling:** Clear error messages for various failure scenarios

**User Experience Considerations:**
- Immediate visual feedback
- Loading states during processing
- Success/error state management
- Responsive design for mobile devices

#### 4. Admin Dashboard Design

**Features Implemented:**
1. **Live Submissions List:** All submissions with full details
2. **Analytics Dashboard:** Total reviews and breakdown by rating
3. **Rating Filters:** Click on stat cards to filter by rating
4. **Auto-refresh:** Updates every 5 seconds (toggleable)
5. **Mismatch Detection:** Highlights when user rating ≠ AI prediction
6. **AI Insights:** Summary, response, and recommended actions for each review
7. **Manual Refresh:** Button to manually refresh data

**Admin Experience Considerations:**
- Real-time monitoring capability
- Easy filtering and navigation
- Clear visual indicators for important information
- Performance optimization (auto-refresh toggle)

#### 5. Backend API Design

**Endpoints:**

1. **POST /api/submit**
   - Accepts: `{rating: int, review_text: string}`
   - Returns: Full submission with AI-generated content
   - Processing:
     - Predicts rating using Task 1's Approach 2
     - Generates user response
     - Creates summary
     - Suggests recommended actions
     - Stores in database

2. **GET /api/submissions**
   - Returns: All submissions with statistics
   - Includes: Rating breakdown, total count
   - Ordered by: Most recent first

3. **GET /api/health**
   - Health check endpoint
   - Used for monitoring

**Error Handling:**
- Input validation (Pydantic models)
- LLM call timeouts (30 seconds)
- Database error handling
- JSON parsing errors
- Graceful fallbacks for each AI function

#### 6. Database Schema

```sql
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rating INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    predicted_rating INTEGER,
    prediction_explanation TEXT,
    ai_response TEXT,
    ai_summary TEXT,
    ai_recommended_actions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Design Rationale:**
- Stores both user rating and AI prediction for comparison
- Includes prediction explanation for transparency
- All AI-generated content stored for admin review
- Timestamps for temporal analysis

---

### Implementation Details

#### Rating Prediction Integration

The system uses Task 1's Approach 2 (Reasoning-guided JSON Prompting) for rating prediction:

```python
def predict_rating(review_text: str, retries: int = 3) -> Tuple[Optional[int], Optional[str]]:
    """
    Predict star rating from review text using Task 1's reasoning JSON approach.
    Returns (predicted_rating, explanation) or (None, None) on failure.
    """
    prompt = f"""
    You are a strict JSON generator.
    
    TASK:
    Classify the Yelp review into a star rating from 1 to 5.
    
    Star scale:
    1 = Very negative
    2 = Mostly negative
    3 = Neutral or mixed
    4 = Mostly positive with minor issues
    5 = Extremely positive with no issues
    
    RULES:
    - Return ONLY valid JSON
    - Do NOT include any text outside JSON
    - Do NOT add markdown
    - Explanation must be ONE short sentence
    
    OUTPUT FORMAT (exact):
    {{"predicted_stars": 4, "explanation": "Short justification"}}
    
    Review: \"\"\"{review_text}\"\"\"
    """
    
    # Implementation with retry logic and error handling
```

**Integration Benefits:**
- Consistent with Task 1 evaluation
- Proven accuracy (63.5%)
- 100% JSON validity
- Reliable error handling

#### AI Response Generation

Three distinct AI functions generate different types of content:

1. **User Response:** Personalized, empathetic response based on rating
2. **Summary:** One-sentence concise summary
3. **Recommended Actions:** Actionable business improvement suggestions

Each function has:
- Specific prompt design for its purpose
- Error handling with fallback responses
- Timeout protection (30 seconds)
- Logging for debugging

#### Frontend-Backend Communication

**Request Flow:**
1. User submits review from frontend
2. Frontend sends POST request to `/api/submit`
3. Backend processes (predicts rating, generates responses)
4. Backend stores in database
5. Backend returns complete response
6. Frontend displays results

**Response Flow:**
1. Admin dashboard requests `/api/submissions`
2. Backend queries database
3. Backend returns all submissions with statistics
4. Frontend displays and auto-refreshes

---

### Deployment Architecture

#### Backend Deployment (Render Web Service)

**Configuration:**
- **Platform:** Render
- **Type:** Web Service
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:** `OPENROUTER_API_KEY`

**Deployment URL:** `https://ai-feedback-backend.onrender.com` (Backend API endpoint)

#### Frontend Deployment (Render Static Site)

**Configuration:**
- **Platform:** Render
- **Type:** Static Site
- **Root Directory:** `frontend`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `out`
- **Environment Variables:** `NEXT_PUBLIC_API_URL`

**Deployment URL:** `https://ai-feedback-system-frontend-yashika.onrender.com`

**Dashboard URLs:**
- **User Dashboard:** https://ai-feedback-system-frontend-yashika.onrender.com/
- **Admin Dashboard:** https://ai-feedback-system-frontend-yashika.onrender.com/admin

**Static Export Configuration:**
- Next.js configured with `output: 'export'`
- Images set to `unoptimized: true`
- All client-side code (no server components)

---

## Overall Architecture

### System Flow

```
User Action → Frontend → Backend API → LLM Processing → Database → Response → Frontend Display
```

### Component Interactions

1. **User submits review:**
   - Frontend validates input
   - Sends POST request to backend
   - Backend processes with LLM
   - Stores in database
   - Returns response
   - Frontend displays results

2. **Admin views submissions:**
   - Frontend requests all submissions
   - Backend queries database
   - Returns submissions with statistics
   - Frontend displays and auto-refreshes

3. **Rating prediction:**
   - Integrated into submission flow
   - Uses Task 1's Approach 2
   - Stores prediction and explanation
   - Displayed for comparison

### Data Flow

```
User Input → Validation → LLM Processing → Database Storage → Response Generation → User Display
                                                                    ↓
                                                           Admin Dashboard Display
```

---

## Design Decisions

### Why FastAPI?

1. **Performance:** Fast, async-capable framework
2. **Documentation:** Automatic OpenAPI/Swagger docs
3. **Validation:** Built-in Pydantic validation
4. **Type Safety:** Python type hints support
5. **Deployment:** Easy deployment on Render

### Why Next.js?

1. **Production Ready:** Optimized for production
2. **Static Export:** Can be deployed as static site
3. **React Ecosystem:** Modern React patterns
4. **Developer Experience:** Great tooling and hot reload
5. **Performance:** Built-in optimizations

### Why SQLite?

1. **Simplicity:** No external database needed
2. **Portability:** Single file database
3. **Sufficient:** Meets MVP requirements
4. **Upgradeable:** Easy to migrate to PostgreSQL
5. **Zero Configuration:** Works out of the box

### Why OpenRouter?

1. **Consistency:** Same provider as Task 1
2. **Free Tier:** Available for testing
3. **Model Choice:** Access to multiple models
4. **Reliability:** Stable API
5. **Cost Effective:** Pay-per-use model

### Why Server-Side LLM Processing?

1. **Security:** API keys never exposed to client
2. **Cost Control:** Centralized usage tracking
3. **Error Handling:** Consistent error management
4. **Performance:** Can cache responses
5. **Requirements:** Mandatory per assignment

---

## Evaluation and Results

### Task 1 Evaluation

**Dataset:** 200 balanced reviews (40 per rating class)

**Results Summary:**
- **Best Approach:** Reasoning-guided JSON Prompting (63.5% accuracy)
- **JSON Validity:** 100% for Approach 2
- **Reliability:** Highest for structured JSON approach

**Key Insights:**
- Structured output improves reliability
- Explanation requirement enhances accuracy
- Model selection critical for JSON generation
- Few-shot not always better than zero-shot

### Task 2 Evaluation

**Functional Testing:**
- ✅ User dashboard: All features working
- ✅ Admin dashboard: All features working
- ✅ Rating prediction: Integrated and functional
- ✅ Error handling: Comprehensive coverage
- ✅ Data persistence: Working across refreshes

**Performance Testing:**
- Response time: 5-15 seconds (LLM processing)
- Database queries: < 100ms
- Frontend load: < 2 seconds
- Auto-refresh: Smooth, no performance issues

**User Experience Testing:**
- Form validation: Working correctly
- Error messages: Clear and helpful
- Loading states: Appropriate feedback
- Responsive design: Works on mobile

---

## System Behavior and Trade-offs

### System Behavior

#### Normal Operation Flow

1. **User Submission:**
   - User selects rating and writes review
   - Frontend validates (rating selected, review not empty, length < 5000)
   - Request sent to backend with 60-second timeout
   - Backend processes:
     - Predicts rating (5-10 seconds)
     - Generates user response (3-5 seconds)
     - Creates summary (2-3 seconds)
     - Suggests actions (3-5 seconds)
   - Total processing: 15-25 seconds
   - Response returned to frontend
   - User sees results with rating comparison

2. **Admin Monitoring:**
   - Admin dashboard loads
   - Requests all submissions
   - Displays with statistics
   - Auto-refreshes every 5 seconds
   - Shows new submissions as they arrive

#### Error Scenarios

1. **LLM API Failure:**
   - System uses fallback responses
   - User still sees a response (generic but functional)
   - Error logged for debugging
   - System continues operating

2. **Network Timeout:**
   - Frontend shows timeout error
   - User can retry submission
   - No data loss (transaction not committed)

3. **Database Error:**
   - Error caught and logged
   - User sees error message
   - System remains stable
   - No partial data saved

4. **Empty/Long Review:**
   - Client-side validation prevents submission
   - Clear error message shown
   - No unnecessary API calls

### Trade-offs

#### 1. SQLite vs PostgreSQL

**Chosen: SQLite**
- **Pros:** Simple, no setup, sufficient for MVP
- **Cons:** Not ideal for high concurrency, limited scalability
- **Trade-off:** Chose simplicity over scalability for MVP

#### 2. Static Site vs Server-Side Rendering

**Chosen: Static Site**
- **Pros:** Fast, CDN-hosted, simple deployment
- **Cons:** No server-side features, larger bundle size
- **Trade-off:** Chose deployment simplicity over SSR features

#### 3. Auto-Refresh Interval

**Chosen: 5 seconds**
- **Pros:** Near real-time updates
- **Cons:** Higher API call frequency
- **Trade-off:** Chose user experience over API efficiency (acceptable for MVP)

#### 4. Error Handling Strategy

**Chosen: Graceful Degradation**
- **Pros:** System always functional, user always gets response
- **Cons:** May hide underlying issues
- **Trade-off:** Chose user experience over strict error reporting

#### 5. LLM Processing Time

**Chosen: Sequential Processing**
- **Pros:** Simpler code, easier debugging
- **Cons:** Slower total response time
- **Trade-off:** Chose code simplicity over performance optimization

---

## Limitations and Future Work

### Current Limitations

1. **Database Scalability:**
   - SQLite not suitable for high concurrency
   - No connection pooling
   - Single-file database

2. **No Authentication:**
   - Admin dashboard is public
   - No user accounts
   - No access control

3. **Rate Limiting:**
   - No rate limiting implemented
   - Vulnerable to abuse
   - No usage quotas

4. **CORS Configuration:**
   - Currently allows all origins
   - Should be restricted in production
   - Security concern

5. **Error Monitoring:**
   - Basic logging only
   - No error tracking service
   - No alerting system

6. **Performance:**
   - Sequential LLM calls (could be parallel)
   - No caching of responses
   - No database indexing optimization

7. **Free Tier Limitations:**
   - Render free tier spins down after inactivity
   - Requires uptime monitoring
   - Cold start delays

### Future Improvements

1. **Database Upgrade:**
   - Migrate to PostgreSQL
   - Add connection pooling
   - Implement database indexing

2. **Authentication System:**
   - Add user authentication
   - Implement admin access control
   - Add role-based permissions

3. **Rate Limiting:**
   - Implement per-IP rate limiting
   - Add usage quotas
   - Monitor and prevent abuse

4. **Performance Optimization:**
   - Parallelize LLM calls
   - Implement response caching
   - Add database query optimization

5. **Monitoring and Logging:**
   - Integrate error tracking (Sentry)
   - Add performance monitoring
   - Implement alerting system

6. **Enhanced Features:**
   - Search functionality
   - Export capabilities (CSV/JSON)
   - Email notifications
   - Real-time updates (WebSockets)

7. **Deployment Improvements:**
   - Upgrade to paid Render tier (always-on)
   - Implement CI/CD pipeline
   - Add automated testing

---

## Conclusion

This project successfully demonstrates:

1. **Prompt Engineering Skills:** Three distinct approaches evaluated with clear methodology
2. **Web Development Proficiency:** Production-ready application with modern stack
3. **System Design Ability:** Well-architected solution with clear separation of concerns
4. **Problem-Solving:** Addressed all requirements with thoughtful trade-offs
5. **Deployment Expertise:** Successfully deployed on Render with proper configuration

**Key Achievements:**
- ✅ Implemented and evaluated 3 prompting approaches
- ✅ Built fully functional two-dashboard system
- ✅ Integrated Task 1 approach into Task 2
- ✅ Deployed both dashboards publicly
- ✅ Comprehensive error handling
- ✅ Clean, maintainable codebase

**Learning Outcomes:**
- Deep understanding of prompt engineering techniques
- Experience with production web application development
- Knowledge of deployment best practices
- Appreciation for system design trade-offs
- Proficiency in modern web technologies

The system is production-ready with room for scalability improvements. All requirements have been met, and the codebase is well-documented and maintainable.

---

## Deployment Links

**User Dashboard:** https://ai-feedback-system-frontend-yashika.onrender.com/  
**Admin Dashboard:** https://ai-feedback-system-frontend-yashika.onrender.com/admin  
**Backend API:** https://ai-feedback-backend.onrender.com  
**API Documentation:** https://ai-feedback-backend.onrender.com/docs

### Access Instructions

- **User Dashboard:** Visit the main URL to submit reviews and receive AI-generated responses
- **Admin Dashboard:** Navigate to `/admin` route to view all submissions, analytics, and AI insights
- Both dashboards are fully functional and accessible without local setup

---

## References

- Yelp Reviews Dataset: https://www.kaggle.com/datasets/omkarsabnis/yelp-reviews-dataset
- OpenRouter API: https://openrouter.ai/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Next.js Documentation: https://nextjs.org/docs
- Render Documentation: https://render.com/docs

---

**Report Prepared By:** Yashika Tirkey  
**Date:** January 2026  
**Assignment:** Fynd AI Intern – Take Home Assessment 2.0
