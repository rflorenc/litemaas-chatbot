"""
Integration tests for Flask API endpoints
"""

import pytest
import json
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_check(self, client):
        """Test health endpoint returns 200 OK"""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'open-source-mentor-bot'
        assert 'version' in data


class TestRootEndpoint:
    """Tests for / endpoint"""

    def test_root_returns_html(self, client):
        """Test root endpoint returns HTML UI"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Open Source Mentor Bot' in response.data
        assert b'<!DOCTYPE html>' in response.data


class TestChatEndpoint:
    """Tests for /api/chat endpoint"""

    def test_chat_requires_json(self, client):
        """Test chat endpoint requires JSON payload"""
        response = client.post('/api/chat')
        assert response.status_code == 400

    def test_chat_requires_message(self, client):
        """Test chat endpoint requires message field"""
        response = client.post(
            '/api/chat',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_chat_rejects_empty_message(self, client):
        """Test chat endpoint rejects empty messages"""
        response = client.post(
            '/api/chat',
            data=json.dumps({'message': '   '}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_chat_rejects_too_long_message(self, client):
        """Test chat endpoint rejects messages that are too long"""
        long_message = 'a' * 1001
        response = client.post(
            '/api/chat',
            data=json.dumps({'message': long_message}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_chat_accepts_valid_message(self, client, mocker):
        """Test chat endpoint accepts valid messages"""
        # Mock the LiteMAAS client
        mocker.patch(
            'app.main.litemaas_client.get_completion',
            return_value='Mocked response'
        )

        response = client.post(
            '/api/chat',
            data=json.dumps({'message': 'Hello, bot!'}),
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'response' in data
        assert data['status'] == 'success'
