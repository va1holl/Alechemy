"""
Tests for events app - Events, scenarios, drinks, and alcohol logging.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from events.models import (
    Event, Scenario, Drink, DrinkCategory, 
    AlcoholLog, Ingredient, IngredientUnit
)

User = get_user_model()


class ScenarioModelTests(TestCase):
    """Tests for Scenario model."""
    
    def test_create_scenario(self):
        """Test creating a scenario."""
        scenario = Scenario.objects.create(
            slug='test-scenario',
            name='Тестовий сценарій',
            description='Опис тестового сценарію',
            category=Scenario.Category.PARTY
        )
        
        self.assertEqual(str(scenario), 'Тестовий сценарій')
        self.assertEqual(scenario.category, Scenario.Category.PARTY)
    
    def test_scenario_with_stage_texts(self):
        """Test scenario with prep/during/after texts."""
        scenario = Scenario.objects.create(
            slug='full-scenario',
            name='Повний сценарій',
            prep_text='Підготовка до події',
            during_text='Під час події',
            after_text='Після події'
        )
        
        self.assertTrue(scenario.prep_text)
        self.assertTrue(scenario.during_text)
        self.assertTrue(scenario.after_text)


class DrinkModelTests(TestCase):
    """Tests for Drink model."""
    
    def setUp(self):
        self.category = DrinkCategory.objects.create(
            slug='wine',
            name='Вино'
        )
    
    def test_create_drink(self):
        """Test creating a drink."""
        drink = Drink.objects.create(
            slug='red-wine',
            name='Червоне вино',
            category=self.category,
            abv=Decimal('12.5'),
            strength=Drink.Strength.REGULAR
        )
        
        self.assertEqual(str(drink), 'Червоне вино')
        self.assertEqual(drink.abv, Decimal('12.5'))
    
    def test_drink_strength_choices(self):
        """Test drink strength choices."""
        drink_strong = Drink.objects.create(
            slug='whisky',
            name='Віскі',
            abv=Decimal('40.0'),
            strength=Drink.Strength.STRONG
        )
        
        self.assertEqual(drink_strong.strength, Drink.Strength.STRONG)


class EventModelTests(TestCase):
    """Tests for Event model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123!'
        )
        self.scenario = Scenario.objects.create(
            slug='test-party',
            name='Тестова вечірка'
        )
    
    def test_create_event(self):
        """Test creating an event."""
        event = Event.objects.create(
            user=self.user,
            title='Моя вечірка',
            scenario=self.scenario,
            date=timezone.now().date(),
            people_count=10,
            duration_hours=5
        )
        
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.scenario, self.scenario)
        self.assertEqual(event.people_count, 10)
    
    def test_event_string_representation(self):
        """Test event __str__ method."""
        event = Event.objects.create(
            user=self.user,
            title='День народження',
            scenario=self.scenario,
            date=timezone.now().date()
        )
        
        # Event __str__ likely includes date or title
        self.assertIsNotNone(str(event))


class AlcoholLogTests(TestCase):
    """Tests for AlcoholLog model and BAC calculation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123!'
        )
        # Set up profile with weight and sex
        self.user.profile.weight_kg = 70
        self.user.profile.sex = 'm'
        self.user.profile.save()
        
        self.drink = Drink.objects.create(
            slug='beer',
            name='Пиво',
            abv=Decimal('5.0')
        )
    
    def test_create_alcohol_log(self):
        """Test creating an alcohol log entry."""
        log = AlcoholLog.objects.create(
            user=self.user,
            drink=self.drink,
            volume_ml=500
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.drink, self.drink)
        self.assertEqual(log.volume_ml, 500)
    
    def test_bac_calculation(self):
        """Test BAC is calculated on save."""
        log = AlcoholLog.objects.create(
            user=self.user,
            drink=self.drink,
            volume_ml=500
        )
        
        # BAC should be calculated
        self.assertIsNotNone(log.bac_estimate)
        self.assertGreater(log.bac_estimate, Decimal('0'))
    
    def test_bac_without_weight(self):
        """Test BAC is None when user has no weight."""
        self.user.profile.weight_kg = None
        self.user.profile.save()
        
        log = AlcoholLog.objects.create(
            user=self.user,
            drink=self.drink,
            volume_ml=500
        )
        
        self.assertIsNone(log.bac_estimate)


class EventViewTests(TestCase):
    """Tests for event views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123!'
        )
        # Set all required profile fields to pass adult_required decorator
        self.user.profile.is_adult_confirmed = True
        self.user.profile.gdpr_consent = True
        from datetime import date
        self.user.profile.birth_date = date(2000, 1, 1)  # Required by adult_required decorator
        self.user.profile.save()
        
        self.scenario = Scenario.objects.create(
            slug='test-scenario',
            name='Тестовий сценарій'
        )
    
    def test_event_list_requires_login(self):
        """Test that event list requires authentication."""
        response = self.client.get(reverse('events:event_list'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_event_list_for_authenticated_user(self):
        """Test event list for logged in user."""
        self.client.login(username='test@example.com', password='testpass123!')
        response = self.client.get(reverse('events:event_list'))
        
        self.assertEqual(response.status_code, 200)
    
    def test_scenario_list_available(self):
        """Test scenario list is accessible for logged in user."""
        self.client.login(username='test@example.com', password='testpass123!')
        response = self.client.get(reverse('events:scenario_list'))
        
        self.assertEqual(response.status_code, 200)


class IngredientTests(TestCase):
    """Tests for Ingredient model."""
    
    def test_create_ingredient(self):
        """Test creating an ingredient."""
        ingredient = Ingredient.objects.create(
            name='Помідори',
            category='food',
            default_unit=IngredientUnit.G
        )
        
        self.assertEqual(str(ingredient), 'Помідори')
        self.assertEqual(ingredient.default_unit, IngredientUnit.G)
    
    def test_ingredient_units(self):
        """Test ingredient unit choices."""
        self.assertEqual(IngredientUnit.PCS, 'pcs')
        self.assertEqual(IngredientUnit.G, 'g')
        self.assertEqual(IngredientUnit.ML, 'ml')
