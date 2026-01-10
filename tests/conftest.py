"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def assistant():
    """Create ModernAssistant instance for testing"""
    from ai_assistant.core.assistant import ModernAssistant
    return ModernAssistant()

@pytest.fixture
def app_client():
    """Create Flask test client"""
    import os
    os.environ['TESTING'] = 'true'
    
    # Import after setting env var
    from ai_assistant.services.modern_web_backend import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(app_client):
    """Get authentication headers for testing"""
    # Login and get token
    response = app_client.post('/api/auth/login', json={'pin': '1234'})
    if response.status_code == 200:
        data = response.get_json()
        token = data.get('access_token')
        return {'Authorization': f'Bearer {token}'}
    return {}
