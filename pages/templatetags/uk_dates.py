"""
Custom template filters for Ukrainian date formatting.
"""
from django import template
from django.utils.translation import get_language

register = template.Library()

MONTHS_UK = {
    1: 'Січень',
    2: 'Лютий',
    3: 'Березень',
    4: 'Квітень',
    5: 'Травень',
    6: 'Червень',
    7: 'Липень',
    8: 'Серпень',
    9: 'Вересень',
    10: 'Жовтень',
    11: 'Листопад',
    12: 'Грудень',
}

MONTHS_UK_SHORT = {
    1: 'Січ',
    2: 'Лют',
    3: 'Бер',
    4: 'Кві',
    5: 'Тра',
    6: 'Чер',
    7: 'Лип',
    8: 'Сер',
    9: 'Вер',
    10: 'Жов',
    11: 'Лис',
    12: 'Гру',
}

MONTHS_EN = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}

MONTHS_EN_SHORT = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec',
}


@register.filter
def uk_month(date):
    """
    Returns the month name in Ukrainian or English based on current language.
    Usage: {{ date|uk_month }}
    Returns: "Грудень, 2025" or "December, 2025"
    """
    if not date:
        return ''
    
    lang = get_language()
    if lang == 'en':
        month_name = MONTHS_EN.get(date.month, '')
    else:
        month_name = MONTHS_UK.get(date.month, '')
    
    return f"{month_name}, {date.year}"


@register.filter
def uk_date_short(date):
    """
    Returns date with short month name in Ukrainian or English.
    Usage: {{ date|uk_date_short }}
    Returns: "Гру 26, 2025" or "Dec 26, 2025"
    """
    if not date:
        return ''
    
    lang = get_language()
    if lang == 'en':
        month_name = MONTHS_EN_SHORT.get(date.month, '')
    else:
        month_name = MONTHS_UK_SHORT.get(date.month, '')
    
    return f"{month_name} {date.day}, {date.year}"


@register.filter
def uk_day_month(date):
    """
    Returns day and short month name in Ukrainian or English.
    Usage: {{ date|uk_day_month }}
    Returns: "26 Гру" or "26 Dec"
    """
    if not date:
        return ''
    
    lang = get_language()
    if lang == 'en':
        month_name = MONTHS_EN_SHORT.get(date.month, '')
    else:
        month_name = MONTHS_UK_SHORT.get(date.month, '')
    
    return f"{date.day} {month_name}"


@register.filter
def uk_month_name(date):
    """
    Returns only the month name in Ukrainian or English.
    Usage: {{ date|uk_month_name }}
    """
    if not date:
        return ''
    
    lang = get_language()
    if lang == 'en':
        return MONTHS_EN.get(date.month, '')
    return MONTHS_UK.get(date.month, '')


@register.filter
def uk_day_month_year(date):
    """
    Returns date with day, short month and year in Ukrainian or English.
    Usage: {{ date|uk_day_month_year }}
    Returns: "26 Гру 2025" or "26 Dec 2025"
    """
    if not date:
        return ''
    
    lang = get_language()
    if lang == 'en':
        month_name = MONTHS_EN_SHORT.get(date.month, '')
    else:
        month_name = MONTHS_UK_SHORT.get(date.month, '')
    
    return f"{date.day} {month_name} {date.year}"


@register.filter
def uk_day_month_time(date):
    """
    Returns date with day, short month and time in Ukrainian or English.
    Usage: {{ date|uk_day_month_time }}
    Returns: "26 Гру, 14:30" or "26 Dec, 14:30"
    """
    if not date:
        return ''
    
    lang = get_language()
    if lang == 'en':
        month_name = MONTHS_EN_SHORT.get(date.month, '')
    else:
        month_name = MONTHS_UK_SHORT.get(date.month, '')
    
    time_str = date.strftime("%H:%M") if hasattr(date, 'strftime') else ''
    return f"{date.day} {month_name}, {time_str}"
