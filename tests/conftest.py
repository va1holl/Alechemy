"""
Pytest configuration and shared fixtures for Alechemy tests.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def user_data():
    """Basic user data for creating test users."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User',
    }


@pytest.fixture
def user(db, user_data):
    """Create a regular test user."""
    user = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
    )
    return user


@pytest.fixture
def adult_user(db, user):
    """Create an adult user with profile that passes adult_required checks."""
    from accounts.models import Profile
    
    # Create profile with all required fields for adult_required
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.age = 25  # Adult
    profile.gdpr_consent = True
    profile.is_adult_confirmed = True
    profile.save()
    return user


@pytest.fixture
def authenticated_client(client, adult_user, user_data):
    """Authenticated test client with adult user."""
    client.login(email=user_data['email'], password=user_data['password'])
    return client


@pytest.fixture
def admin_user(db):
    """Create a superuser."""
    return User.objects.create_superuser(
        username='adminuser',
        email='admin@example.com',
        password='AdminPass123!',
    )


@pytest.fixture
def other_user(db):
    """Create another regular adult user for testing access control."""
    user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='OtherPass123!',
        first_name='Other',
        last_name='User',
    )
    from accounts.models import Profile
    
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.age = 30
    profile.gdpr_consent = True
    profile.is_adult_confirmed = True
    profile.save()
    return user


@pytest.fixture
def scenario(db):
    """Create a test scenario."""
    from events.models import Scenario
    
    scenario = Scenario.objects.create(
        slug='test-scenario',
        name='Test Scenario',
        description='Test scenario description',
        category=Scenario.Category.PARTY,
    )
    return scenario


@pytest.fixture
def drink(db):
    """Create a test drink."""
    from events.models import Drink
    
    drink = Drink.objects.create(
        slug='test-beer',
        name='Test Beer',
        strength=Drink.Strength.REGULAR,
        abv=5.0,
    )
    return drink


@pytest.fixture
def dish(db):
    """Create a test dish."""
    from events.models import Dish
    
    dish = Dish.objects.create(
        name='Test Snacks',
    )
    return dish


@pytest.fixture
def event(db, adult_user, scenario, drink, dish):
    """Create a test event."""
    from datetime import date
    from events.models import Event
    
    event = Event.objects.create(
        user=adult_user,
        scenario=scenario,
        drink=drink,
        dish=dish,
        date=date.today(),
        people_count=4,
        duration_hours=3,
    )
    return event


@pytest.fixture
def other_event(db, other_user, scenario, drink, dish):
    """Create an event owned by another user."""
    from datetime import date
    from events.models import Event
    
    event = Event.objects.create(
        user=other_user,
        scenario=scenario,
        drink=drink,
        dish=dish,
        date=date.today(),
        people_count=2,
        duration_hours=2,
    )
    return event


@pytest.fixture
def friend_request(db, adult_user, other_user):
    """Create an accepted friend request between adult_user and other_user."""
    from accounts.models import FriendRequest
    
    friend_req = FriendRequest.objects.create(
        from_user=adult_user,
        to_user=other_user,
        status=FriendRequest.Status.ACCEPTED,
    )
    return friend_req
