from .auth_views import (
    about,
    home,
    user_register,
    user_login,
    auth_login,
    user_dashboard,
    auth_dashboard,
    user_logout,
    auth_logout,
    save_location,
    get_locations,
    delete_location,
)
from .chatbot_views import chatbot_api
from .report_views import (
    submit_garbage_report,
    user_reports,
    download_report_zip,
    get_report_media,
    update_report_status,
)
from .analytics_views import analytics_dashboard
from .cctv_views import (
    live_camera_feed,
    cctv_detected_events,
    cctv_events,
    cctv_event_detail,
    api_cctv_events,
)

__all__ = [
    'about',
    'home',
    'user_register',
    'user_login',
    'auth_login',
    'user_dashboard',
    'auth_dashboard',
    'user_logout',
    'auth_logout',
    'save_location',
    'get_locations',
    'delete_location',
    'chatbot_api',
    'submit_garbage_report',
    'user_reports',
    'download_report_zip',
    'get_report_media',
    'update_report_status',
    'analytics_dashboard',
    'live_camera_feed',
    'cctv_detected_events',
    'cctv_events',
    'cctv_event_detail',
    'api_cctv_events',
]