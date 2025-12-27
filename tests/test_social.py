"""
Tests for social features - friendships, friend requests.
"""
import pytest
from django.urls import reverse
from django.test import Client

from accounts.models import FriendRequest


class TestFriendships:
    """Tests for friendship functionality."""
    
    def test_friends_list_requires_auth(self, client):
        """Friends list requires authentication."""
        url = reverse('social:friends_list')
        response = client.get(url)
        assert response.status_code == 302
    
    def test_friends_list_accessible(self, authenticated_client):
        """Authenticated user can view friends list."""
        url = reverse('social:friends_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200
    
    def test_accepted_friends_shown(self, authenticated_client, friend_request, other_user):
        """Accepted friends are shown in friends list."""
        url = reverse('social:friends_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        # Check that friend is in the response
        content = response.content.decode()
        assert other_user.email in content or other_user.first_name in content


class TestFriendRequests:
    """Tests for friend request functionality."""
    
    def test_send_friend_request(self, authenticated_client, other_user, adult_user, db):
        """User can send friend request."""
        # Remove any existing friend requests
        FriendRequest.objects.filter(from_user=adult_user, to_user=other_user).delete()
        FriendRequest.objects.filter(from_user=other_user, to_user=adult_user).delete()
        
        url = reverse('social:send_friend_request', kwargs={'user_id': other_user.pk})
        response = authenticated_client.post(url)
        
        # Should redirect after action
        assert response.status_code == 302
        
        # Check friend request was created
        assert FriendRequest.objects.filter(
            from_user=adult_user,
            to_user=other_user,
            status=FriendRequest.Status.PENDING
        ).exists()
    
    def test_accept_friend_request_post_only(self, client, adult_user, other_user, user_data, db):
        """Accept friend request requires POST."""
        # Create pending request from other_user
        friend_req = FriendRequest.objects.create(
            from_user=other_user,
            to_user=adult_user,
            status=FriendRequest.Status.PENDING,
        )
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('social:accept_friend_request', kwargs={'req_id': friend_req.pk})
        
        # GET should not work (should be POST)
        response = client.get(url)
        assert response.status_code in [302, 405]  # Redirect or Method Not Allowed
    
    def test_accept_friend_request(self, client, adult_user, other_user, user_data, db):
        """User can accept friend request."""
        # Create pending request from other_user
        friend_req = FriendRequest.objects.create(
            from_user=other_user,
            to_user=adult_user,
            status=FriendRequest.Status.PENDING,
        )
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('social:accept_friend_request', kwargs={'req_id': friend_req.pk})
        response = client.post(url)
        
        assert response.status_code == 302
        
        friend_req.refresh_from_db()
        assert friend_req.status == FriendRequest.Status.ACCEPTED
    
    def test_reject_friend_request(self, client, adult_user, other_user, user_data, db):
        """User can reject friend request."""
        # Create pending request from other_user
        friend_req = FriendRequest.objects.create(
            from_user=other_user,
            to_user=adult_user,
            status=FriendRequest.Status.PENDING,
        )
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('social:reject_friend_request', kwargs={'req_id': friend_req.pk})
        response = client.post(url)
        
        assert response.status_code == 302
        
        friend_req.refresh_from_db()
        assert friend_req.status == FriendRequest.Status.REJECTED
    
    def test_cannot_accept_others_request(self, client, adult_user, other_user, user_data, db):
        """User cannot accept request not addressed to them."""
        # Create a third user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        third_user = User.objects.create_user(
            username='thirduser',
            email='third@example.com',
            password='ThirdPass123!',
        )
        
        # Create request between other_user and third_user
        friend_req = FriendRequest.objects.create(
            from_user=other_user,
            to_user=third_user,
            status=FriendRequest.Status.PENDING,
        )
        
        # Try to accept as adult_user (should fail)
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('social:accept_friend_request', kwargs={'req_id': friend_req.pk})
        response = client.post(url)
        
        # Should get 404 or 403
        assert response.status_code in [403, 404]
        
        friend_req.refresh_from_db()
        assert friend_req.status == FriendRequest.Status.PENDING


class TestRemoveFriend:
    """Tests for removing friends."""
    
    def test_reject_removes_friend(self, client, adult_user, other_user, user_data, db):
        """User can reject/remove friend by rejecting request."""
        # Create accepted friend request
        friend_req = FriendRequest.objects.create(
            from_user=other_user,
            to_user=adult_user,
            status=FriendRequest.Status.ACCEPTED,
        )
        
        client.login(email=user_data['email'], password=user_data['password'])
        url = reverse('social:reject_friend_request', kwargs={'req_id': friend_req.pk})
        response = client.post(url)
        
        assert response.status_code == 302
        
        # FriendRequest should be rejected
        friend_req.refresh_from_db()
        assert friend_req.status == FriendRequest.Status.REJECTED
