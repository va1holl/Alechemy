"""
Caching utilities for events app.
Provides cached access to frequently queried static data like scenarios and drinks.
"""
from django.core.cache import cache
from functools import wraps


# Cache timeouts (in seconds)
SCENARIO_CACHE_TIMEOUT = 60 * 15  # 15 minutes
DRINK_CACHE_TIMEOUT = 60 * 15  # 15 minutes
CATEGORY_CACHE_TIMEOUT = 60 * 60  # 1 hour


def get_cached_scenarios():
    """
    Get all scenarios with prefetched drinks from cache.
    Falls back to database query if cache miss.
    """
    cache_key = 'all_scenarios_with_drinks'
    scenarios = cache.get(cache_key)
    
    if scenarios is None:
        from .models import Scenario
        scenarios = list(
            Scenario.objects.prefetch_related('drinks')
            .order_by('name')
        )
        cache.set(cache_key, scenarios, SCENARIO_CACHE_TIMEOUT)
    
    return scenarios


def get_cached_drinks():
    """
    Get all drinks with category from cache.
    Falls back to database query if cache miss.
    """
    cache_key = 'all_drinks_with_category'
    drinks = cache.get(cache_key)
    
    if drinks is None:
        from .models import Drink
        drinks = list(
            Drink.objects.select_related('category')
            .prefetch_related('tags')
            .order_by('name')
        )
        cache.set(cache_key, drinks, DRINK_CACHE_TIMEOUT)
    
    return drinks


def get_cached_drink_categories():
    """
    Get all drink categories from cache.
    """
    cache_key = 'drink_categories'
    categories = cache.get(cache_key)
    
    if categories is None:
        from .models import DrinkCategory
        categories = list(DrinkCategory.objects.all().order_by('name'))
        cache.set(cache_key, categories, CATEGORY_CACHE_TIMEOUT)
    
    return categories


def invalidate_scenario_cache():
    """Call this when scenarios are modified."""
    cache.delete('all_scenarios_with_drinks')


def invalidate_drink_cache():
    """Call this when drinks are modified."""
    cache.delete('all_drinks_with_category')
    cache.delete('drink_categories')


# Signal handlers for cache invalidation
def setup_cache_invalidation_signals():
    """
    Connect signals to automatically invalidate cache when models change.
    Call this from apps.py ready() method.
    """
    from django.db.models.signals import post_save, post_delete
    from .models import Scenario, Drink, DrinkCategory
    
    post_save.connect(lambda **kwargs: invalidate_scenario_cache(), sender=Scenario)
    post_delete.connect(lambda **kwargs: invalidate_scenario_cache(), sender=Scenario)
    
    post_save.connect(lambda **kwargs: invalidate_drink_cache(), sender=Drink)
    post_delete.connect(lambda **kwargs: invalidate_drink_cache(), sender=Drink)
    
    post_save.connect(lambda **kwargs: invalidate_drink_cache(), sender=DrinkCategory)
    post_delete.connect(lambda **kwargs: invalidate_drink_cache(), sender=DrinkCategory)
