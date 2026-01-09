"""
FastAPI Backend for AI Feedback System
Handles review submissions, AI processing, and admin data retrieval
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Tuple
from datetime import datetime
import sqlite3
import os
import json
import time
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Feedback System API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenRouter client
api_key = os.environ.get("OPENROUTER_API_KEY", "")
if not api_key:
    logger.error("OPENROUTER_API_KEY not found in environment variables!")
    logger.error("Please set OPENROUTER_API_KEY in Render environment variables")
    # Don't create client if no key - will fail gracefully
    client = None
else:
    logger.info(f"OpenRouter API key found (length: {len(api_key)}, starts with: {api_key[:10]}...)")
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

# Database setup
DB_PATH = "feedback.db"

def init_db():
    """Initialize SQLite database with migration support"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
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
    """)
    
    # Migrate existing table if needed (add new columns if they don't exist)
    # Check if columns exist before adding
    cursor.execute("PRAGMA table_info(submissions)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    if 'predicted_rating' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE submissions ADD COLUMN predicted_rating INTEGER")
            logger.info("Added predicted_rating column")
        except sqlite3.OperationalError as e:
            logger.warning(f"Could not add predicted_rating column: {e}")
    
    if 'prediction_explanation' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE submissions ADD COLUMN prediction_explanation TEXT")
            logger.info("Added prediction_explanation column")
        except sqlite3.OperationalError as e:
            logger.warning(f"Could not add prediction_explanation column: {e}")
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

init_db()

# =========================
# REQUEST/RESPONSE SCHEMAS
# =========================

class ReviewSubmission(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    review_text: str = Field(..., min_length=1, max_length=5000, description="Review text")
    
    @field_validator('review_text')
    @classmethod
    def validate_review_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Review text cannot be empty")
        return v.strip()

class AIResponse(BaseModel):
    message: str = Field(..., description="AI-generated response to the user")
    summary: str = Field(..., description="AI-generated summary of the review")
    recommended_actions: str = Field(..., description="AI-suggested recommended actions")

class SubmissionResponse(BaseModel):
    id: int
    rating: int
    review_text: str
    predicted_rating: Optional[int] = None
    prediction_explanation: Optional[str] = None
    ai_response: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_recommended_actions: Optional[str] = None
    created_at: str

class SubmissionListResponse(BaseModel):
    submissions: List[SubmissionResponse]
    total: int
    by_rating: dict

# =========================
# LLM PROMPT FUNCTIONS
# =========================

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

Review:
\"\"\"{review_text}\"\"\"
"""
    
    if not client:
        logger.error("OpenRouter client not initialized - API key missing")
        return None, None
    
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to predict rating (attempt {attempt+1}/{retries})")
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=150
            )
            
            text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            
            # Parse JSON strictly
            data = json.loads(text)
            
            if (
                "predicted_stars" in data
                and "explanation" in data
                and 1 <= int(data["predicted_stars"]) <= 5
            ):
                return int(data["predicted_stars"]), str(data["explanation"])
            
            raise ValueError("Invalid JSON schema")
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(1)
            continue
        except Exception as e:
            logger.warning(f"Prediction error (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(1)
            continue
    
    logger.error("Failed to predict rating after all retries")
    return None, None

def generate_user_response(rating: int, review_text: str, retries: int = 3) -> str:
    """Generate a user-facing response based on the review"""
    prompt = f"""
You are a warm and professional customer service representative responding to a customer review.

Customer gave us {rating} out of 5 stars.
Their review: "{review_text}"

Write a personalized, natural response (2-3 sentences) that:
- Specifically mentions something from their review (food quality, service, atmosphere, etc.)
- Shows genuine appreciation
- If {rating} stars (low rating): Express sincere concern, acknowledge the issues they mentioned, and offer to make it right
- If {rating} stars (high rating): Thank them warmly, mention what they liked, and invite them back
- If {rating} stars (neutral): Acknowledge their balanced feedback and show you value their input

Make it sound natural and human, not robotic. Reference specific details from their review.

Write ONLY the response, nothing else.
"""
    
    if not client:
        logger.error("OpenRouter client not initialized - API key missing")
        return f"[API Key Not Configured] Thank you for your {rating}-star review. We appreciate your feedback."
    
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to generate user response (attempt {attempt+1}/{retries})")
            
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a warm, empathetic customer service representative who writes natural, personalized responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=250
            )
            
            result = response.choices[0].message.content.strip()
            if result and len(result) > 20:  # Ensure we got a real response
                logger.info(f"Successfully generated user response: {result[:100]}...")
                return result
            else:
                logger.warning(f"Received empty or too short response: {result}")
                raise ValueError(f"Empty or invalid response from API: {result}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"User response generation error (attempt {attempt+1}/{retries}): {error_msg}")
            logger.error(f"Error type: {type(e).__name__}")
            if "api" in error_msg.lower() or "key" in error_msg.lower():
                logger.error("Possible API key or authentication issue")
            if attempt < retries - 1:
                time.sleep(2)  # Longer wait between retries
                continue
    
    # Fallback if all retries fail
    logger.error("All user response generation attempts failed, using fallback")
    logger.error(f"Rating: {rating}, Review length: {len(review_text)}")
    logger.error(f"API Key present: {bool(os.environ.get('OPENROUTER_API_KEY'))}")
    # Return a message indicating failure so we know it's not AI-generated
    return f"[AI Response Generation Failed - Check Logs] Thank you for your {rating}-star review. We appreciate your feedback."

def generate_summary(review_text: str, retries: int = 3) -> str:
    """Generate a concise summary of the review"""
    prompt = f"""
Read this customer review and create a natural, concise one-sentence summary (15-25 words) that captures the main points.

Review: "{review_text}"

Focus on: what they liked/disliked, key issues mentioned, overall sentiment.
Make it sound natural, not robotic.

Write ONLY the summary sentence, nothing else.
"""
    
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to generate summary (attempt {attempt+1}/{retries})")
            logger.info(f"Review text preview: {review_text[:100]}...")
            
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating natural, concise summaries that capture the essence of customer feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=80
            )
            
            result = response.choices[0].message.content.strip()
            if result and len(result) > 10:  # Ensure we got a real response
                logger.info(f"Successfully generated summary: {result}")
                return result
            else:
                logger.warning(f"Received empty or too short response: {result}")
                raise ValueError(f"Empty or invalid response from API: {result}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Summary generation error (attempt {attempt+1}/{retries}): {error_msg}")
            logger.error(f"Error type: {type(e).__name__}")
            if "api" in error_msg.lower() or "key" in error_msg.lower():
                logger.error("Possible API key or authentication issue")
            if attempt < retries - 1:
                time.sleep(2)  # Longer wait between retries
                continue
    
    # If all retries failed, log detailed error
    logger.error("All summary generation attempts failed, using fallback")
    logger.error(f"Review text length: {len(review_text)}")
    logger.error(f"API Key present: {bool(os.environ.get('OPENROUTER_API_KEY'))}")
    # Don't use hardcoded fallback - return error message so we know it failed
    return f"[AI Summary Generation Failed - Check Logs] Review about: {review_text[:50]}..."

def generate_recommended_actions(rating: int, review_text: str, retries: int = 3) -> str:
    """Generate recommended actions based on the review"""
    prompt = f"""
Analyze this customer review and suggest 2-3 specific, actionable steps the business should take.

Customer Rating: {rating}/5 stars
Review: "{review_text}"

Based on what the customer mentioned, provide practical recommendations:
- If rating is 4-5 stars: Suggest ways to maintain excellence and enhance what they loved
- If rating is 1-2 stars: Suggest concrete steps to address the specific issues mentioned
- If rating is 3 stars: Suggest improvements to move from "okay" to "great"

Format as a bulleted list (each action on a new line, start with "-").
Be specific - reference what they mentioned (service speed, food quality, wait times, etc.).
Make actions practical and implementable.

Write ONLY the bulleted list, nothing else.
"""
    
    if not client:
        logger.error("OpenRouter client not initialized - API key missing")
        return "[API Key Not Configured] - Review feedback internally\n- Follow up with customer if needed"
    
    for attempt in range(retries):
        try:
            logger.info(f"Attempting to generate recommended actions (attempt {attempt+1}/{retries})")
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert business consultant who provides specific, actionable recommendations based on customer feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=250
            )
            result = response.choices[0].message.content.strip()
            if result:
                logger.info(f"Successfully generated recommended actions")
                return result
            else:
                raise ValueError("Empty response from API")
        except Exception as e:
            logger.warning(f"Recommended actions generation error (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(1)
                continue
    
    # Fallback if all retries fail
    logger.error("All recommended actions generation attempts failed, using fallback")
    return "- Review feedback internally\n- Follow up with customer if needed\n- Implement improvements based on feedback"

# =========================
# API ENDPOINTS
# =========================

@app.post("/api/submit", response_model=SubmissionResponse)
async def submit_review(submission: ReviewSubmission):
    """
    Submit a new review and generate AI responses including rating prediction
    """
    try:
        # Validate API key
        if not os.environ.get("OPENROUTER_API_KEY"):
            logger.error("OPENROUTER_API_KEY not set")
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: API key not configured"
            )
        
        # Predict rating using Task 1 approach
        logger.info("Predicting rating for review...")
        predicted_rating, prediction_explanation = predict_rating(submission.review_text)
        
        if predicted_rating is None:
            logger.warning("Rating prediction failed, continuing without prediction")
        
        # Generate AI responses (with error handling for each)
        logger.info("Generating AI responses...")
        # These functions handle their own errors and retries, so we don't need try-except here
        ai_response = generate_user_response(submission.rating, submission.review_text)
        ai_summary = generate_summary(submission.review_text)
        ai_actions = generate_recommended_actions(submission.rating, submission.review_text)
        
        # Store in database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO submissions 
                (rating, review_text, predicted_rating, prediction_explanation, 
                 ai_response, ai_summary, ai_recommended_actions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                submission.rating,
                submission.review_text,
                predicted_rating,
                prediction_explanation,
                ai_response,
                ai_summary,
                ai_actions
            ))
            
            submission_id = cursor.lastrowid
            conn.commit()
            
            # Use explicit column names to avoid order issues
            # Check which columns exist first
            cursor.execute("PRAGMA table_info(submissions)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Build SELECT query with only existing columns
            select_columns = []
            for col in ['id', 'rating', 'review_text', 'predicted_rating', 'prediction_explanation',
                       'ai_response', 'ai_summary', 'ai_recommended_actions', 'created_at']:
                if col in column_names:
                    select_columns.append(col)
            
            query = f"SELECT {', '.join(select_columns)} FROM submissions WHERE id = ?"
            cursor.execute(query, (submission_id,))
            row = cursor.fetchone()
            conn.close()
            
            logger.info(f"Successfully saved submission {submission_id}")
            
            # Build a dictionary from column names and values
            row_dict = dict(zip(select_columns, row))
            
            # Build response with explicit column mapping
            return SubmissionResponse(
                id=row_dict['id'],
                rating=row_dict['rating'],
                review_text=row_dict['review_text'],
                predicted_rating=row_dict.get('predicted_rating') or predicted_rating,
                prediction_explanation=row_dict.get('prediction_explanation') or prediction_explanation,
                ai_response=row_dict.get('ai_response'),
                ai_summary=row_dict.get('ai_summary'),
                ai_recommended_actions=row_dict.get('ai_recommended_actions'),
                created_at=row_dict.get('created_at', datetime.now().isoformat())
            )
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save submission to database"
            )
            
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing submission: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing submission: {str(e)}"
        )

@app.get("/api/submissions", response_model=SubmissionListResponse)
async def get_submissions():
    """
    Get all submissions for admin dashboard
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check which columns exist
        cursor.execute("PRAGMA table_info(submissions)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Build SELECT query with only existing columns
        select_columns = []
        for col in ['id', 'rating', 'review_text', 'predicted_rating', 'prediction_explanation',
                   'ai_response', 'ai_summary', 'ai_recommended_actions', 'created_at']:
            if col in column_names:
                select_columns.append(col)
        
        query = f"SELECT {', '.join(select_columns)} FROM submissions ORDER BY created_at DESC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        submissions = []
        by_rating = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for row in rows:
            # Build dictionary from column names and values
            row_dict = dict(zip(select_columns, row))
            
            submissions.append(SubmissionResponse(
                id=row_dict['id'],
                rating=row_dict['rating'],
                review_text=row_dict['review_text'],
                predicted_rating=row_dict.get('predicted_rating'),
                prediction_explanation=row_dict.get('prediction_explanation'),
                ai_response=row_dict.get('ai_response'),
                ai_summary=row_dict.get('ai_summary'),
                ai_recommended_actions=row_dict.get('ai_recommended_actions'),
                created_at=row_dict.get('created_at', datetime.now().isoformat())
            ))
            by_rating[row_dict['rating']] += 1
        
        logger.info(f"Retrieved {len(submissions)} submissions")
        return SubmissionListResponse(
            submissions=submissions,
            total=len(submissions),
            by_rating=by_rating
        )
    except sqlite3.Error as e:
        logger.error(f"Database error fetching submissions: {e}")
        raise HTTPException(status_code=500, detail="Database error while fetching submissions")
    except Exception as e:
        logger.error(f"Unexpected error fetching submissions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching submissions: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    api_key_status = "configured" if os.environ.get("OPENROUTER_API_KEY") else "missing"
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "api_key": api_key_status
    }

@app.get("/api/test-ai")
async def test_ai():
    """Test AI generation endpoint"""
    try:
        test_review = "The food was amazing and service was excellent!"
        
        # Test summary generation
        logger.info("Testing AI summary generation...")
        summary = generate_summary(test_review, retries=1)
        
        # Test user response
        logger.info("Testing AI user response generation...")
        response = generate_user_response(5, test_review, retries=1)
        
        return {
            "status": "success",
            "summary": summary,
            "response": response,
            "api_key_present": bool(os.environ.get("OPENROUTER_API_KEY"))
        }
    except Exception as e:
        logger.error(f"AI test failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "api_key_present": bool(os.environ.get("OPENROUTER_API_KEY"))
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Feedback System API",
        "endpoints": {
            "submit": "/api/submit",
            "submissions": "/api/submissions",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
