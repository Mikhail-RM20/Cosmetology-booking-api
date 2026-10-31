from fastapi import FastAPI

from routes import (
    delete_entries_route_delete,
    get_all_entry_route,
    get_procedures_route,
    login_route,
    new_entry_route,
    registration_route,
    rotation_route,
)

app = FastAPI()

app.include_router(delete_entries_route_delete)
app.include_router(get_all_entry_route)
app.include_router(get_procedures_route)
app.include_router(login_route)
app.include_router(new_entry_route)
app.include_router(registration_route)
app.include_router(rotation_route)
