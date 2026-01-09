'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface SubmissionResponse {
  id: number
  rating: number
  review_text: string
  predicted_rating?: number | null
  prediction_explanation?: string | null
  ai_response: string
  ai_summary: string
  ai_recommended_actions: string
  created_at: string
}

export default function UserDashboard() {
  const [rating, setRating] = useState<number>(0)
  const [hoveredRating, setHoveredRating] = useState<number>(0)
  const [reviewText, setReviewText] = useState<string>('')
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [submission, setSubmission] = useState<SubmissionResponse | null>(null)
  const [error, setError] = useState<string>('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (rating === 0) {
      setError('Please select a rating')
      return
    }
    
    if (!reviewText.trim()) {
      setError('Please enter a review')
      return
    }

    if (reviewText.length > 5000) {
      setError('Review is too long (max 5000 characters)')
      return
    }

    setIsSubmitting(true)
    setError('')
    setSubmission(null)

    try {
      const response = await axios.post(
        `${API_URL}/api/submit`,
        {
          rating,
          review_text: reviewText
        },
        {
          timeout: 60000, // 60 second timeout for LLM calls
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )

      setSubmission(response.data)
      setReviewText('')
      setRating(0)
    } catch (err: any) {
      if (err.code === 'ECONNABORTED') {
        setError('Request timed out. The AI is processing your review, please try again in a moment.')
      } else if (err.response) {
        // Server responded with error
        const errorDetail = err.response.data?.detail || err.response.data?.message || 'Unknown server error'
        setError(`Server error: ${errorDetail}`)
      } else if (err.request) {
        // Request made but no response
        setError('Cannot connect to server. Please check if the backend is running.')
      } else {
        // Something else happened
        setError('Failed to submit review. Please try again.')
      }
      console.error('Submission error:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: '#333' }}>
          Share Your Feedback
        </h1>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Rating *
            </label>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((star) => (
                <span
                  key={star}
                  className={`star ${rating >= star ? 'selected' : ''} ${hoveredRating >= star && rating < star ? 'hover' : ''}`}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoveredRating(star)}
                  onMouseLeave={() => setHoveredRating(0)}
                >
                  ★
                </span>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              Your Review *
            </label>
            <textarea
              className="textarea"
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              placeholder="Tell us about your experience..."
              maxLength={5000}
              rows={6}
            />
            <div style={{ textAlign: 'right', marginTop: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
              {reviewText.length} / 5000 characters
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div style={{ textAlign: 'center' }}>
            <button
              type="submit"
              className="button"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Review'}
            </button>
          </div>
        </form>

        {submission && (
          <div className="success-message" style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem', color: '#155724' }}>✓ Thank you for your feedback!</h3>
            
            {/* Rating Comparison */}
            {submission.predicted_rating && (
              <div style={{ 
                marginBottom: '1rem', 
                padding: '1rem', 
                background: submission.predicted_rating === submission.rating 
                  ? '#d4edda' 
                  : '#fff3cd', 
                borderRadius: '8px',
                border: `2px solid ${submission.predicted_rating === submission.rating ? '#28a745' : '#ffc107'}`
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <div>
                    <strong>Your Rating:</strong> <span style={{ fontSize: '1.2rem' }}>{submission.rating} ★</span>
                  </div>
                  <div>
                    <strong>AI Predicted:</strong> <span style={{ fontSize: '1.2rem' }}>{submission.predicted_rating} ★</span>
                  </div>
                </div>
                {submission.prediction_explanation && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#555' }}>
                    <em>Prediction: {submission.prediction_explanation}</em>
                  </div>
                )}
                {submission.predicted_rating !== submission.rating && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#856404' }}>
                    ⚠️ There's a difference between your rating and the AI's prediction.
                  </div>
                )}
              </div>
            )}
            
            <div className="ai-response-box">
              <h4>Our Response</h4>
              <p>{submission.ai_response}</p>
            </div>

            <div style={{ marginTop: '1rem', padding: '1rem', background: '#e7f3ff', borderRadius: '8px' }}>
              <strong>Your Review Summary:</strong> {submission.ai_summary}
            </div>
          </div>
        )}
      </div>

      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <a href="/admin" style={{ color: 'white', textDecoration: 'underline' }}>
          Admin Dashboard →
        </a>
      </div>
    </div>
  )
}
