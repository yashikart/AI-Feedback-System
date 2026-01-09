# AI Feedback System

A production-ready web application with two dashboards for collecting and managing customer feedback using AI-powered responses and rating predictions.

**Author:** Yashika  
**Email:** riyashika20@gmail.com

---

## Project Overview

This project consists of two main tasks:

### Task 1: Rating Prediction via Prompting
- Implemented in `Task1.ipynb`
- Uses Yelp Reviews dataset (`yelp.csv`)
- Three different prompting approaches for rating prediction
- Evaluates accuracy, JSON validity, and consistency
- Uses OpenRouter API with reasoning-guided JSON prompts

### Task 2: Two-Dashboard AI Feedback System
- Production web application with User and Admin dashboards
- Real-time AI-powered feedback processing
- Rating prediction using Task 1's approach
- Fully deployed and accessible

---

## Project Structure

```
AI_Feedback_System/
├── Task1.ipynb              # Task 1: Rating Prediction via Prompting
├── yelp.csv                 # Yelp Reviews Dataset
├── README.md                # This file
├── backend/                 # FastAPI Backend
│   ├── main.py             # API server with LLM integration
│   ├── requirements.txt    # Python dependencies
│   ├── render.yaml         # Render deployment config
│   ├── Procfile           # Alternative deployment config
│   └── .env               # Environment variables (not in git)
└── frontend/               # Next.js Frontend
    ├── app/                # Next.js app directory
    │   ├── page.tsx        # User Dashboard
    │   ├── admin/          # Admin Dashboard
    │   │   └── page.tsx    # Admin page
    │   ├── layout.tsx      # Root layout
    │   └── globals.css     # Styling
    ├── package.json        # Node dependencies
    ├── vercel.json         # Vercel deployment config
    ├── next.config.js      # Next.js configuration
    └── .env.local          # Environment variables (not in git)
```

---

## Features

### User Dashboard
- ⭐ Star rating selection (1-5)
- 📝 Review text input with character counter (max 5000)
- 🤖 AI-generated personalized response
- 🎯 AI rating prediction with explanation
- 📊 Rating comparison (user vs AI prediction)
- ✅ Success/error state handling
- 📝 Review summary display

### Admin Dashboard
- 📋 Live-updating list of all submissions
- 📊 Analytics dashboard (total reviews, breakdown by rating)
- 🔍 Filter by rating (click on stat cards)
- 🔄 Auto-refresh functionality (every 5 seconds, toggleable)
- 🤖 AI-generated summaries and recommended actions
- ⚠️ Rating mismatch detection and warnings
- 📱 Responsive design

### Backend Features
- 🎯 Rating prediction using Task 1's reasoning JSON approach
- 🤖 Three AI functions: user response, summary, recommended actions
- 💾 SQLite database with automatic migrations
- 🔒 Server-side LLM processing (secure)
- ✅ Comprehensive error handling
- 📝 Logging for debugging
- 🚀 RESTful API with JSON schemas

---

## Technical Requirements Met

✅ **Web-based application** (not Streamlit/Gradio)  
✅ **Deployed on Vercel/Render**  
✅ **Persistent data storage** (SQLite database)  
✅ **Server-side LLM calls** (all AI processing in backend)  
✅ **Clear API endpoints** with JSON schemas  
✅ **Error handling** for empty reviews, long reviews, API failures  
✅ **Two separate dashboards** (User and Admin)  
✅ **Rating prediction** using Task 1's approach  
✅ **Rating comparison** and mismatch detection

---

## Setup Instructions

### Prerequisites
- Python 3.8+ (tested with Python 3.13)
- Node.js 18+
- OpenRouter API key (get one at https://openrouter.ai/ - free tier available)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variable:
   - Create `.env` file with:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```
   - Or set it in your system:
   ```bash
   export OPENROUTER_API_KEY=your_api_key_here
   ```

4. Run locally:
```bash
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set environment variable (create `.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run locally:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

## Deployment

### Backend Deployment (Render)

1. **Push code to GitHub**
   - Ensure your repository is on GitHub

2. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Sign up or log in

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `ai-feedback-backend`
     - **Root Directory**: `backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variable**
   - Key: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Your backend URL: `https://your-service-name.onrender.com`

**Note:** Render free tier spins down after 15 minutes of inactivity. Use UptimeRobot (free) to ping your service every 5 minutes to keep it alive.

### Frontend Deployment (Vercel)

1. **Push code to GitHub**
   - Ensure your repository is on GitHub

2. **Go to Vercel**
   - Visit https://vercel.com
   - Sign up or log in

3. **Import Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Next.js
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build` (auto-detected)
     - **Output Directory**: `.next` (auto-detected)

4. **Add Environment Variable**
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: Your Render backend URL (e.g., `https://your-backend-name.onrender.com`)

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment
   - Your frontend URL: `https://your-project-name.vercel.app`

### Update CORS (If Needed)

If you encounter CORS errors, update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.vercel.app",
        "http://localhost:3000"  # For local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend.

---

## API Endpoints

### POST `/api/submit`
Submit a new review and get AI-generated responses.

**Request:**
```json
{
  "rating": 5,
  "review_text": "I Love the food, Its sooo Delicious"
}
```

**Response:**
```json
{
  "id": 1,
  "rating": 5,
  "predicted_rating": 5,
  "prediction_explanation": "Extremely positive review expressing strong satisfaction",
  "review_text": "I Love the food, Its sooo Delicious",
  "ai_response": "Thank you for your wonderful review!...",
  "ai_summary": "Customer loves the delicious food.",
  "ai_recommended_actions": "- Continue maintaining high food quality...",
  "created_at": "2026-01-09T17:13:56"
}
```

### GET `/api/submissions`
Get all submissions for admin dashboard.

**Response:**
```json
{
  "submissions": [
    {
      "id": 1,
      "rating": 5,
      "predicted_rating": 5,
      "prediction_explanation": "...",
      "review_text": "...",
      "ai_response": "...",
      "ai_summary": "...",
      "ai_recommended_actions": "...",
      "created_at": "..."
    }
  ],
  "total": 10,
  "by_rating": {
    "1": 1,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 3
  }
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-09T17:13:56"
}
```

---

## Task 1: Rating Prediction

The rating prediction uses the same approach as implemented in `Task1.ipynb`:

### Approach: Reasoning-Guided JSON Prompt

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
```

**Features:**
- Uses OpenRouter API with GPT-3.5-turbo
- Returns structured JSON with rating and explanation
- Includes retry logic (3 attempts)
- Handles JSON parsing errors gracefully
- Falls back gracefully if prediction fails

---

## LLM Integration

The system uses OpenRouter API (same as Task 1) with GPT-3.5-turbo for:

1. **Rating Prediction**: Predicts star rating from review text (Task 1 approach)
2. **User Response Generation**: Personalized responses based on rating and review
3. **Review Summarization**: Concise one-sentence summaries
4. **Recommended Actions**: Actionable business improvement suggestions

All LLM calls are:
- **Server-side** for security and cost control
- **Timeout protected** (30 seconds)
- **Error handled** with graceful fallbacks
- **Logged** for debugging

---

## Design Decisions

1. **FastAPI Backend**: Fast, modern Python framework with automatic API docs
2. **Next.js Frontend**: React framework optimized for production, easy Vercel deployment
3. **SQLite Database**: Simple, file-based persistence suitable for MVP
4. **OpenRouter API**: Consistent with Task 1, supports multiple models, free tier available
5. **Auto-refresh**: Admin dashboard updates every 5 seconds for real-time monitoring
6. **Error Handling**: Comprehensive error handling with graceful degradation
7. **Rating Prediction**: Uses Task 1's proven approach for consistency

---

## Error Handling

The system handles various error scenarios:

- ✅ **Empty reviews**: Validation prevents submission
- ✅ **Long reviews**: Character limit (5000) enforced
- ✅ **LLM API failures**: Graceful fallbacks with default responses
- ✅ **Network timeouts**: 30-second timeout for LLM calls, clear error messages
- ✅ **Database errors**: Wrapped in try-catch with specific error messages
- ✅ **JSON parsing errors**: Retry logic with fallback
- ✅ **Missing API key**: Clear error message
- ✅ **CORS issues**: Configurable CORS middleware

---

## Limitations & Trade-offs

1. **SQLite**: Not ideal for high concurrency; can be upgraded to PostgreSQL
2. **Auto-refresh**: 5-second interval may be too frequent for high traffic
3. **No Authentication**: Admin dashboard is public (add auth for production)
4. **Rate Limiting**: Not implemented (add for production)
5. **CORS**: Currently allows all origins (restrict in production)
6. **Free Tier Limitations**: Render free tier spins down after inactivity

---

## Testing

### Local Testing

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:3000`
4. Submit a test review:
   - Rating: 5 stars
   - Review: "I Love the food, Its sooo Delicious"
5. Check Admin Dashboard: `http://localhost:3000/admin`

### Example Test Cases

- **Positive Review**: "Amazing food and excellent service!" → Should predict 4-5 stars
- **Negative Review**: "Terrible experience!" → Should predict 1-2 stars
- **Neutral Review**: "It was okay, nothing special" → Should predict 3 stars
- **Rating Mismatch**: User selects 2, but review is positive → AI predicts 3-4, shows warning

---

## Future Improvements

- [ ] Add authentication for admin dashboard
- [ ] Implement rate limiting
- [ ] Upgrade to PostgreSQL for better scalability
- [ ] Add pagination for large submission lists
- [ ] Implement search functionality
- [ ] Add export functionality (CSV/JSON)
- [ ] Add email notifications for new submissions
- [ ] Implement caching for better performance
- [ ] Add user authentication
- [ ] Implement real-time updates with WebSockets

---

## Deployment URLs

After deployment, you should have:

- **User Dashboard**: `https://your-frontend-url.vercel.app`
- **Admin Dashboard**: `https://your-frontend-url.vercel.app/admin`
- **Backend API**: `https://your-backend-url.onrender.com`
- **API Docs**: `https://your-backend-url.onrender.com/docs`

---

## Contact

**Author:** Yashika  
**Email:** riyashika20@gmail.com

---

## License

This project is created for educational purposes.

---

## Acknowledgments

- OpenRouter API for LLM access
- FastAPI for the backend framework
- Next.js for the frontend framework
- Yelp Reviews dataset from Kaggle
