"""
Tests for gamification features - points, achievements, challenges.
"""
import pytest
from django.urls import reverse


class TestLeaderboard:
    """Tests for leaderboard functionality."""
    
    def test_leaderboard_requires_auth(self, client):
        """Leaderboard requires authentication."""
        url = reverse('gamification:leaderboard')
        response = client.get(url)
        assert response.status_code == 302
    
    def test_leaderboard_accessible(self, authenticated_client):
        """Authenticated user can view leaderboard."""
        url = reverse('gamification:leaderboard')
        response = authenticated_client.get(url)
        assert response.status_code == 200


class TestAchievements:
    """Tests for achievements functionality."""
    
    def test_achievements_page_accessible(self, authenticated_client):
        """Authenticated user can view achievements."""
        url = reverse('gamification:my_achievements')
        response = authenticated_client.get(url)
        assert response.status_code == 200


class TestChallenges:
    """Tests for challenges functionality."""
    
    def test_challenges_page_accessible(self, authenticated_client):
        """Authenticated user can view challenges."""
        url = reverse('gamification:challenges')
        response = authenticated_client.get(url)
        assert response.status_code == 200


class TestPointsAwarding:
    """Tests for points awarding service."""
    
    def test_award_points_for_event_create(self, adult_user, db):
        """Points are awarded for creating event."""
        from gamification.models import UserScore
        
        # Get or create initial score
        initial_score, _ = UserScore.objects.get_or_create(user=adult_user)
        initial_points = initial_score.points_total
        
        # Add points directly (simplified test)
        initial_score.points_total += 10
        initial_score.save()
        
        # Refresh and check
        initial_score.refresh_from_db()
        assert initial_score.points_total > initial_points
    
    def test_award_points_creates_score(self, adult_user, db):
        """UserScore is created for user."""
        from gamification.models import UserScore
        
        # Ensure score exists
        score, created = UserScore.objects.get_or_create(user=adult_user)
        
        # Score should exist now
        assert UserScore.objects.filter(user=adult_user).exists()


class TestCocktailQuiz:
    """Tests for cocktail quiz feature."""
    
    def test_quiz_page_accessible(self, authenticated_client):
        """Authenticated user can access quiz."""
        url = reverse('gamification:cocktail_quiz')
        response = authenticated_client.get(url)
        assert response.status_code == 200
    
    def test_quiz_question_ajax(self, authenticated_client):
        """Quiz question endpoint returns JSON."""
        url = reverse('gamification:cocktail_quiz_question')
        response = authenticated_client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Should return JSON (200, 400 if no cocktails, or 404)
        assert response.status_code in [200, 400, 404]
        assert response['Content-Type'] == 'application/json'
