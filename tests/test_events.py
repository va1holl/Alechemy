"""
Tests for events views - security, access control, CRUD operations.
"""
import pytest
from django.urls import reverse
from django.test import Client

from events.models import Event, EventParticipant


class TestEventAccessControl:
    """Tests for ID enumeration prevention and access control."""
    
    def test_event_detail_owner_can_access(self, authenticated_client, event):
        """Event owner can view their own event."""
        url = reverse('events:event_detail', kwargs={'pk': event.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
    
    def test_event_detail_returns_404_for_other_user(self, client, adult_user, other_event, user_data):
        """Other users get 404, not 403, to prevent ID enumeration."""
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_detail', kwargs={'pk': other_event.pk})
        response = client.get(url)
        assert response.status_code == 404
    
    def test_event_detail_anonymous_redirects_to_login(self, client, event):
        """Anonymous users are redirected to login."""
        url = reverse('events:event_detail', kwargs={'pk': event.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
    
    def test_participant_can_access_event(self, client, adult_user, other_event, other_user, user_data, db):
        """Accepted participant can access event."""
        # Add adult_user as participant
        EventParticipant.objects.create(
            event=other_event,
            participant=adult_user,
            status=EventParticipant.Status.ACCEPTED,
        )
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_detail', kwargs={'pk': other_event.pk})
        response = client.get(url)
        assert response.status_code == 200
    
    def test_pending_participant_cannot_access_event(self, client, adult_user, other_event, other_user, user_data, db):
        """Pending participant cannot access event details."""
        # Add adult_user as pending participant
        EventParticipant.objects.create(
            event=other_event,
            participant=adult_user,
            status=EventParticipant.Status.PENDING,
        )
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_detail', kwargs={'pk': other_event.pk})
        response = client.get(url)
        assert response.status_code == 404


class TestEventCRUD:
    """Tests for Event create, read, update, delete operations."""
    
    def test_event_list_shows_own_events(self, authenticated_client, event):
        """Event list shows user's own events."""
        url = reverse('events:event_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert event in response.context['events']
    
    def test_event_list_does_not_show_others_events(self, authenticated_client, other_event):
        """Event list does not show other users' events."""
        url = reverse('events:event_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert other_event not in response.context['events']
    
    def test_event_edit_owner_only(self, authenticated_client, event):
        """Only owner can access edit page."""
        url = reverse('events:event_edit', kwargs={'pk': event.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
    
    def test_event_edit_returns_404_for_non_owner(self, client, adult_user, other_event, user_data):
        """Non-owner gets 404 on edit page."""
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_edit', kwargs={'pk': other_event.pk})
        response = client.get(url)
        assert response.status_code == 404
    
    def test_event_delete_owner_only(self, authenticated_client, event):
        """Only owner can delete event."""
        url = reverse('events:event_delete', kwargs={'pk': event.pk})
        response = authenticated_client.post(url)
        assert response.status_code == 302  # Redirect after delete
        assert not Event.objects.filter(pk=event.pk).exists()
    
    def test_event_delete_returns_404_for_non_owner(self, client, adult_user, other_event, user_data):
        """Non-owner gets 404 on delete attempt."""
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_delete', kwargs={'pk': other_event.pk})
        response = client.post(url)
        assert response.status_code == 404
        # Event should still exist
        assert Event.objects.filter(pk=other_event.pk).exists()


class TestScenarioViews:
    """Tests for scenario views."""
    
    def test_scenario_list_requires_auth(self, client):
        """Scenario list requires authentication."""
        url = reverse('events:scenario_list')
        response = client.get(url)
        assert response.status_code == 302
    
    def test_scenario_list_authenticated(self, authenticated_client):
        """Authenticated user can view scenario list."""
        url = reverse('events:scenario_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200
    
    def test_scenario_detail(self, authenticated_client, scenario, drink, db):
        """User can view scenario detail."""
        # Add drink to scenario
        scenario.drinks.add(drink)
        
        url = reverse('events:scenario_detail', kwargs={'slug': scenario.slug})
        response = authenticated_client.get(url)
        assert response.status_code == 200
    
    def test_toggle_favorite_scenario(self, authenticated_client, scenario):
        """User can toggle favorite scenario (redirects after toggle)."""
        url = reverse('events:toggle_favorite', kwargs={'slug': scenario.slug})
        response = authenticated_client.post(url)
        # Either redirect or success
        assert response.status_code in [200, 302]


class TestEventParticipants:
    """Tests for participant management."""
    
    def test_participants_page_owner_access(self, authenticated_client, event):
        """Owner can access participants page."""
        url = reverse('events:event_participants', kwargs={'pk': event.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
    
    def test_participants_page_non_owner_404(self, client, adult_user, other_event, user_data, db):
        """Non-owner cannot access participants page."""
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_participants', kwargs={'pk': other_event.pk})
        response = client.get(url)
        assert response.status_code == 404
    
    def test_participant_can_access_participants_page(self, client, adult_user, other_event, user_data, db):
        """Accepted participant can access participants page."""
        # Add as regular participant
        EventParticipant.objects.create(
            event=other_event,
            participant=adult_user,
            status=EventParticipant.Status.ACCEPTED,
        )
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_participants', kwargs={'pk': other_event.pk})
        response = client.get(url)
        assert response.status_code == 200


class TestEventFinish:
    """Tests for event finishing functionality."""
    
    def test_finish_event_owner_only(self, authenticated_client, event):
        """Only owner can finish event."""
        url = reverse('events:event_finish', kwargs={'pk': event.pk})
        response = authenticated_client.post(url)
        assert response.status_code == 302
        
        event.refresh_from_db()
        assert event.is_finished is True
    
    def test_finish_event_non_owner_404(self, client, adult_user, other_event, user_data):
        """Non-owner cannot finish event."""
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('events:event_finish', kwargs={'pk': other_event.pk})
        response = client.post(url)
        assert response.status_code == 404
        
        other_event.refresh_from_db()
        assert other_event.is_finished is False
