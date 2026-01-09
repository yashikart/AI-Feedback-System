'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Submission {
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

interface SubmissionListResponse {
  submissions: Submission[]
  total: number
  by_rating: { [key: number]: number }
}

export default function AdminDashboard() {
  const [data, setData] = useState<SubmissionListResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string>('')
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true)
  const [filterRating, setFilterRating] = useState<number | null>(null)

  const fetchSubmissions = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/submissions`, {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json'
        }
      })
      setData(response.data)
      setError('')
    } catch (err: any) {
      if (err.code === 'ECONNABORTED') {
        setError('Request timed out. Please try again.')
      } else if (err.response) {
        setError(err.response?.data?.detail || 'Failed to load submissions')
      } else if (err.request) {
        setError('Cannot connect to server. Please check if the backend is running.')
      } else {
        setError('Failed to load submissions. Please try again.')
      }
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSubmissions()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchSubmissions()
    }, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [autoRefresh])

  const filteredSubmissions = filterRating
    ? data?.submissions.filter(s => s.rating === filterRating) || []
    : data?.submissions || []

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1 style={{ color: '#333' }}>Admin Dashboard</h1>
          <div>
            <button
              className="button"
              onClick={fetchSubmissions}
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
            <button
              className={`button ${autoRefresh ? 'refresh-button' : ''}`}
              onClick={() => setAutoRefresh(!autoRefresh)}
              style={{ marginLeft: '0.5rem' }}
            >
              {autoRefresh ? '⏸ Auto-Refresh ON' : '▶ Auto-Refresh OFF'}
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {loading && !data ? (
          <div className="loading">Loading submissions...</div>
        ) : (
          <>
            {/* Statistics */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number">{data?.total || 0}</div>
                <div className="stat-label">Total Reviews</div>
              </div>
              {[5, 4, 3, 2, 1].map((rating) => (
                <div key={rating} className="stat-card" style={{ cursor: 'pointer' }} onClick={() => setFilterRating(filterRating === rating ? null : rating)}>
                  <div className="stat-number">{data?.by_rating[rating] || 0}</div>
                  <div className="stat-label">{rating} Star{rating !== 1 ? 's' : ''}</div>
                </div>
              ))}
            </div>

            {/* Filter */}
            {filterRating && (
              <div style={{ marginBottom: '1rem', padding: '1rem', background: '#fff3cd', borderRadius: '8px' }}>
                <strong>Filtering by: {filterRating} star rating</strong>
                <button
                  onClick={() => setFilterRating(null)}
                  style={{ marginLeft: '1rem', padding: '0.25rem 0.75rem', background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                  Clear Filter
                </button>
              </div>
            )}

            {/* Submissions List */}
            <h2 style={{ marginBottom: '1rem', color: '#333' }}>
              All Submissions ({filteredSubmissions.length})
            </h2>

            {filteredSubmissions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
                No submissions found.
              </div>
            ) : (
              filteredSubmissions.map((submission) => (
                <div key={submission.id} className="submission-item">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <div>
                      <span className="rating-badge">{submission.rating} ★</span>
                      {submission.predicted_rating && (
                        <span 
                          className="rating-badge" 
                          style={{ 
                            background: submission.predicted_rating === submission.rating ? '#28a745' : '#ffc107',
                            marginLeft: '0.5rem'
                          }}
                        >
                          AI: {submission.predicted_rating} ★
                        </span>
                      )}
                      <span style={{ color: '#666', fontSize: '0.9rem', marginLeft: '0.5rem' }}>
                        {formatDate(submission.created_at)}
                      </span>
                    </div>
                    <span style={{ color: '#666', fontSize: '0.9rem' }}>ID: {submission.id}</span>
                  </div>

                  {/* Rating Comparison */}
                  {submission.predicted_rating && submission.predicted_rating !== submission.rating && (
                    <div style={{ 
                      marginBottom: '1rem', 
                      padding: '0.75rem', 
                      background: '#fff3cd', 
                      borderRadius: '8px',
                      borderLeft: '4px solid #ffc107'
                    }}>
                      <strong>⚠️ Rating Mismatch:</strong> User selected {submission.rating} stars, but AI predicted {submission.predicted_rating} stars.
                      {submission.prediction_explanation && (
                        <div style={{ marginTop: '0.25rem', fontSize: '0.9rem', color: '#856404' }}>
                          <em>AI Reasoning: {submission.prediction_explanation}</em>
                        </div>
                      )}
                    </div>
                  )}

                  <div style={{ marginBottom: '1rem' }}>
                    <strong>Review:</strong>
                    <p style={{ marginTop: '0.5rem', color: '#555', lineHeight: '1.6' }}>
                      {submission.review_text}
                    </p>
                  </div>

                  <div className="ai-response-box">
                    <h4>AI Summary</h4>
                    <p>{submission.ai_summary}</p>
                  </div>

                  <div className="ai-response-box" style={{ marginTop: '0.5rem' }}>
                    <h4>AI Response</h4>
                    <p>{submission.ai_response}</p>
                  </div>

                  <div className="ai-actions">
                    <h4>Recommended Actions</h4>
                    <ul>
                      {submission.ai_recommended_actions.split('\n').filter(line => line.trim()).map((action, idx) => (
                        <li key={idx}>{action.replace(/^[-•]\s*/, '')}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))
            )}
          </>
        )}
      </div>

      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <a href="/" style={{ color: 'white', textDecoration: 'underline' }}>
          ← User Dashboard
        </a>
      </div>
    </div>
  )
}
