"""
Events views package.

Imports all views from submodules for backwards compatibility.
"""

# Scenarios
from .scenarios import (
    scenario_list,
    toggle_favorite_scenario,
    scenario_detail,
)

# Events CRUD
from .events import (
    event_list,
    event_create_from_scenario,
    event_edit,
    event_delete,
    event_detail,
    event_recommendations_preview,
    event_location,
    event_feedback,
    event_discussion,
    event_search_api,
)

# Diary
from .diary import (
    diary_list,
    diary_detail,
    diary_add,
    get_diary_stats_for_user,
)

# Participants
from .participants import (
    event_participants,
    event_invite_friend,
    event_remove_participant,
    event_invitation_response,
    event_toggle_admin,
    event_finish,
    my_invitations,
    event_leave,
)

# Utilities (for use in other modules)
from .utils import (
    _get_accessible_event_or_404,
    _get_admin_event_or_404,
    _get_owner_event_or_404,
    _can_access_event,
    _is_event_admin,
    _get_user_role,
    build_recommendations_placeholder,
    build_recovery_advice,
)

__all__ = [
    # Scenarios
    'scenario_list',
    'toggle_favorite_scenario',
    'scenario_detail',
    # Events
    'event_list',
    'event_create_from_scenario',
    'event_edit',
    'event_delete',
    'event_detail',
    'event_recommendations_preview',
    'event_location',
    'event_feedback',
    'event_discussion',
    # Diary
    'diary_list',
    'diary_detail',
    'diary_add',
    'get_diary_stats_for_user',
    # Participants
    'event_participants',
    'event_invite_friend',
    'event_remove_participant',
    'event_invitation_response',
    'event_toggle_admin',
    'event_finish',
    'my_invitations',
    'event_leave',
    # Utils
    '_get_accessible_event_or_404',
    '_get_admin_event_or_404',
    '_get_owner_event_or_404',
    '_can_access_event',
    '_is_event_admin',
    '_get_user_role',
    'build_recommendations_placeholder',
    'build_recovery_advice',
]
