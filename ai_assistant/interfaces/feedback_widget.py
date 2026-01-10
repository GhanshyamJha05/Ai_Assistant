"""
Feedback Widget UI Component
Provides thumbs up/down, star ratings, and preference comparison for user feedback

Integrates with AdvancedFeedbackLearning system
"""

from flask import Blueprint, render_template_string, request, jsonify
from ai_assistant.ai.advanced_feedback_learning import FeedbackCollector, FeedbackEntry, FeedbackType
from datetime import datetime
import uuid

feedback_widget_bp = Blueprint('feedback_widget', __name__)

# Initialize feedback collector
try:
    feedback_collector = FeedbackCollector(db_path='data/feedback.db')
except Exception as e:
    print(f"⚠️ Feedback collector initialization: {e}")
    feedback_collector = None


# HTML/CSS/JS for feedback widget
FEEDBACK_WIDGET_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Feedback Widget</title>
    <style>
        .feedback-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 20px;
            max-width: 350px;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .feedback-header {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        
        .feedback-section {
            margin-bottom: 20px;
        }
        
        .feedback-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .thumbs-container {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        
        .thumb-btn {
            width: 60px;
            height: 60px;
            border: 2px solid #e0e0e0;
            border-radius: 50%;
            background: white;
            cursor: pointer;
            font-size: 28px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .thumb-btn:hover {
            transform: scale(1.1);
            border-color: #4CAF50;
        }
        
        .thumb-btn.active-up {
            background: #4CAF50;
            border-color: #4CAF50;
            transform: scale(1.15);
        }
        
        .thumb-btn.active-down {
            background: #f44336;
            border-color: #f44336;
            transform: scale(1.15);
        }
        
        .stars-container {
            display: flex;
            gap: 8px;
            justify-content: center;
        }
        
        .star {
            font-size: 32px;
            cursor: pointer;
            color: #ddd;
            transition: color 0.2s;
        }
        
        .star:hover,
        .star.active {
            color: #FFD700;
        }
        
        .feedback-textarea {
            width: 100%;
            min-height: 80px;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
        }
        
        .submit-btn {
            width: 100%;
            padding: 12px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .submit-btn:hover {
            background: #1976D2;
        }
        
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .success-message {
            background: #4CAF50;
            color: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            margin-top: 10px;
            display: none;
        }
        
        .response-preview {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 13px;
            color: #555;
            max-height: 100px;
            overflow-y: auto;
        }
        
        .toggle-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #2196F3;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            z-index: 9998;
        }
    </style>
</head>
<body>
    <!-- Toggle button -->
    <div class="toggle-widget" id="toggleBtn" onclick="toggleWidget()">
        💬
    </div>
    
    <!-- Feedback widget -->
    <div class="feedback-widget" id="feedbackWidget" style="display: none;">
        <div class="feedback-header">
            How was this response?
        </div>
        
        <!-- Response preview -->
        <div class="response-preview" id="responsePreview">
            Last AI response will appear here...
        </div>
        
        <!-- Thumbs up/down -->
        <div class="feedback-section">
            <div class="feedback-label">Quick Feedback</div>
            <div class="thumbs-container">
                <button class="thumb-btn" id="thumbsUp" onclick="submitThumbs('up')">
                    👍
                </button>
                <button class="thumb-btn" id="thumbsDown" onclick="submitThumbs('down')">
                    👎
                </button>
            </div>
        </div>
        
        <!-- Star rating -->
        <div class="feedback-section">
            <div class="feedback-label">Rating</div>
            <div class="stars-container" id="starsContainer">
                <span class="star" onclick="setRating(1)">★</span>
                <span class="star" onclick="setRating(2)">★</span>
                <span class="star" onclick="setRating(3)">★</span>
                <span class="star" onclick="setRating(4)">★</span>
                <span class="star" onclick="setRating(5)">★</span>
            </div>
        </div>
        
        <!-- Text feedback -->
        <div class="feedback-section">
            <div class="feedback-label">Additional Comments (Optional)</div>
            <textarea class="feedback-textarea" id="feedbackText" 
                      placeholder="Tell us more about your experience..."></textarea>
        </div>
        
        <!-- Submit button -->
        <button class="submit-btn" onclick="submitFeedback()">
            Submit Feedback
        </button>
        
        <!-- Success message -->
        <div class="success-message" id="successMessage">
            ✅ Thank you! Your feedback helps improve the AI.
        </div>
    </div>
    
    <script>
        let currentRating = 0;
        let currentThumbs = null;
        let lastPrompt = "";
        let lastResponse = "";
        
        // Toggle widget visibility
        function toggleWidget() {
            const widget = document.getElementById('feedbackWidget');
            const toggle = document.getElementById('toggleBtn');
            
            if (widget.style.display === 'none') {
                widget.style.display = 'block';
                toggle.style.display = 'none';
            } else {
                widget.style.display = 'none';
                toggle.style.display = 'flex';
            }
        }
        
        // Submit thumbs feedback
        function submitThumbs(direction) {
            currentThumbs = direction;
            
            // Visual feedback
            document.getElementById('thumbsUp').classList.remove('active-up');
            document.getElementById('thumbsDown').classList.remove('active-down');
            
            if (direction === 'up') {
                document.getElementById('thumbsUp').classList.add('active-up');
            } else {
                document.getElementById('thumbsDown').classList.add('active-down');
            }
            
            // Auto-submit simple thumbs feedback
            sendFeedback('thumbs', {thumbs: direction});
        }
        
        // Set star rating
        function setRating(stars) {
            currentRating = stars;
            const starElements = document.querySelectorAll('.star');
            
            starElements.forEach((star, index) => {
                if (index < stars) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });
            
            // Auto-submit rating
            sendFeedback('rating', {rating: stars});
        }
        
        // Submit full feedback
        function submitFeedback() {
            const text = document.getElementById('feedbackText').value;
            
            sendFeedback('full', {
                thumbs: currentThumbs,
                rating: currentRating,
                text: text
            });
        }
        
        // Send feedback to server
        function sendFeedback(type, data) {
            const endpoint = type === 'thumbs' ? '/api/feedback/thumbs' :
                            type === 'rating' ? '/api/feedback/rating' :
                            '/api/feedback/full';
            
            fetch(endpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    prompt: lastPrompt,
                    response: lastResponse,
                    session_id: sessionStorage.getItem('session_id'),
                    ...data
                })
            })
            .then(response => response.json())
            .then(data => {
                showSuccess();
            })
            .catch(error => console.error('Feedback error:', error));
        }
        
        // Show success message
        function showSuccess() {
            const msg = document.getElementById('successMessage');
            msg.style.display = 'block';
            
            setTimeout(() => {
                msg.style.display = 'none';
            }, 3000);
        }
        
        // Update response preview (call this from main chat)
        function updateResponsePreview(prompt, response) {
            lastPrompt = prompt;
            lastResponse = response;
            document.getElementById('responsePreview').textContent = 
                response.substring(0, 200) + (response.length > 200 ? '...' : '');
        }
        
        // Make function available globally
        window.updateResponsePreview = updateResponsePreview;
    </script>
</body>
</html>
"""


@feedback_widget_bp.route('/widget')
def feedback_widget():
    """Render feedback widget"""
    return render_template_string(FEEDBACK_WIDGET_HTML)


@feedback_widget_bp.route('/api/feedback/thumbs', methods=['POST'])
def api_thumbs_feedback():
    """API endpoint for thumbs feedback"""
    if not feedback_collector:
        return jsonify({'error': 'Feedback system not initialized'}), 500
    
    data = request.json
    
    try:
        entry = FeedbackEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            feedback_type=FeedbackType.THUMBS_UP if data.get('thumbs') == 'up' else FeedbackType.THUMBS_DOWN,
            prompt=data.get('prompt', ''),
            response=data.get('response', ''),
            feedback_value={'thumbs': data.get('thumbs')},
            context=data.get('context', {}),
            session_id=data.get('session_id')
        )
        
        feedback_collector.record_feedback(entry)
        
        return jsonify({'status': 'success', 'message': 'Feedback recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@feedback_widget_bp.route('/api/feedback/rating', methods=['POST'])
def api_rating_feedback():
    """API endpoint for star rating"""
    if not feedback_collector:
        return jsonify({'error': 'Feedback system not initialized'}), 500
    
    data = request.json
    
    try:
        entry = FeedbackEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            feedback_type=FeedbackType.STAR_RATING,
            prompt=data.get('prompt', ''),
            response=data.get('response', ''),
            feedback_value={'rating': data.get('rating', 3)},
            context=data.get('context', {}),
            session_id=data.get('session_id')
        )
        
        feedback_collector.record_feedback(entry)
        
        return jsonify({'status': 'success', 'message': 'Rating recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@feedback_widget_bp.route('/api/feedback/full', methods=['POST'])
def api_full_feedback():
    """API endpoint for full feedback with text"""
    if not feedback_collector:
        return jsonify({'error': 'Feedback system not initialized'}), 500
    
    data = request.json
    
    try:
        # Determine feedback type
        if data.get('thumbs'):
            feedback_type = FeedbackType.THUMBS_UP if data['thumbs'] == 'up' else FeedbackType.THUMBS_DOWN
        elif data.get('rating'):
            feedback_type = FeedbackType.STAR_RATING
        else:
            feedback_type = FeedbackType.NATURAL_LANGUAGE
        
        entry = FeedbackEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            prompt=data.get('prompt', ''),
            response=data.get('response', ''),
            feedback_value={
                'thumbs': data.get('thumbs'),
                'rating': data.get('rating'),
                'text': data.get('text')
            },
            context=data.get('context', {}),
            session_id=data.get('session_id')
        )
        
        feedback_collector.record_feedback(entry)
        
        return jsonify({'status': 'success', 'message': 'Feedback recorded'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@feedback_widget_bp.route('/api/feedback/stats', methods=['GET'])
def api_feedback_stats():
    """Get feedback statistics"""
    if not feedback_collector:
        return jsonify({'error': 'Feedback system not initialized'}), 500
    
    try:
        recent = feedback_collector.get_recent_feedback(limit=100)
        
        thumbs_up = sum(1 for f in recent if f.feedback_type == FeedbackType.THUMBS_UP)
        thumbs_down = sum(1 for f in recent if f.feedback_type == FeedbackType.THUMBS_DOWN)
        
        ratings = [f.feedback_value.get('rating', 0) for f in recent 
                   if f.feedback_type == FeedbackType.STAR_RATING]
        
        return jsonify({
            'total_feedback': len(recent),
            'thumbs_up': thumbs_up,
            'thumbs_down': thumbs_down,
            'satisfaction_rate': round(thumbs_up / max(thumbs_up + thumbs_down, 1) * 100, 1),
            'average_rating': round(sum(ratings) / max(len(ratings), 1), 1),
            'total_ratings': len(ratings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
