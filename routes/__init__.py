from .route_delete_entries import router as delete_entries_route_delete
from .route_get_all_entry import router as get_all_entry_route
from .route_get_procedures import router as get_procedures_route
from .route_login import router as login_route
from .route_new_entry import router as new_entry_route
from .route_registration import router as registration_route
from .route_rotation import router as rotation_route

__all__ = [
    "delete_entries_route_delete",
    "get_all_entry_route",
    "get_procedures_route",
    "login_route",
    "new_entry_route",
    "registration_route",
    "rotation_route",
]
