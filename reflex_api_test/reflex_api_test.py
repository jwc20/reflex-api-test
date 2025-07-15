import reflex as rx
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List, Dict, Any
import asyncio

# Create a FastAPI app with additional endpoints
fastapi_app = FastAPI(title="Reflex + FastAPI Integration", version="1.0.0")

# Mock data store
items_store = {
    "items": ["Apple", "Banana", "Cherry", "Date", "Elderberry"],
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    ],
}

# OAuth2 scheme for authentication demo
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# FastAPI Routes
@fastapi_app.get("/api/items")
async def get_items():
    """Get all items from the store."""
    return {"items": items_store["items"]}


@fastapi_app.post("/api/items")
async def add_item(item: Dict[str, str]):
    """Add a new item to the store."""
    new_item = item.get("name", "").strip()
    if not new_item:
        raise HTTPException(status_code=400, detail="Item name is required")

    items_store["items"].append(new_item)
    return {
        "message": f"Item '{new_item}' added successfully",
        "items": items_store["items"],
    }


@fastapi_app.get("/api/users")
async def get_users():
    """Get all users."""
    return {"users": items_store["users"]}


@fastapi_app.get("/api/stats")
async def get_stats():
    """Get application statistics."""
    return {
        "total_items": len(items_store["items"]),
        "total_users": len(items_store["users"]),
        "status": "active",
    }


# Simple authentication endpoint
@fastapi_app.post("/token")
async def login(username: str, password: str):
    """Simple login endpoint for demo purposes."""
    if username == "admin" and password == "secret":
        return {
            "access_token": "demo_token_12345",
            "token_type": "bearer",
            "message": "Login successful",
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


# Protected endpoint example
@fastapi_app.get("/api/protected")
async def protected_route(token: str = oauth2_scheme):
    """Protected endpoint that requires authentication."""
    if token != "demo_token_12345":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "This is a protected endpoint", "user": "admin"}


# Reflex State
class State(rx.State):
    """The app state."""

    items: List[str] = []
    users: List[Dict[str, Any]] = []
    stats: Dict[str, Any] = {}
    new_item: str = ""
    loading: bool = False
    message: str = ""
    username: str = ""
    password: str = ""
    token: str = ""
    protected_data: str = ""

    async def load_items(self):
        """Load items from the FastAPI endpoint."""
        self.loading = True
        try:
            # Simulate API call (in real app, you'd use httpx or requests)
            await asyncio.sleep(0.1)  # Simulate network delay
            # For demo, we'll use the items directly from the store
            self.items = items_store["items"]
            self.message = "Items loaded successfully!"
        except Exception as e:
            self.message = f"Error loading items: {str(e)}"
        finally:
            self.loading = False

    async def load_users(self):
        """Load users from the FastAPI endpoint."""
        self.loading = True
        try:
            await asyncio.sleep(0.1)
            self.users = items_store["users"]
            self.message = "Users loaded successfully!"
        except Exception as e:
            self.message = f"Error loading users: {str(e)}"
        finally:
            self.loading = False

    async def load_stats(self):
        """Load stats from the FastAPI endpoint."""
        self.loading = True
        try:
            await asyncio.sleep(0.1)
            self.stats = {
                "total_items": len(items_store["items"]),
                "total_users": len(items_store["users"]),
                "status": "active",
            }
            self.message = "Stats loaded successfully!"
        except Exception as e:
            self.message = f"Error loading stats: {str(e)}"
        finally:
            self.loading = False

    async def add_item(self):
        """Add a new item via the FastAPI endpoint."""
        if not self.new_item.strip():
            self.message = "Please enter an item name"
            return

        self.loading = True
        try:
            await asyncio.sleep(0.1)
            items_store["items"].append(self.new_item.strip())
            self.items = items_store["items"]
            self.message = f"Item '{self.new_item}' added successfully!"
            self.new_item = ""
        except Exception as e:
            self.message = f"Error adding item: {str(e)}"
        finally:
            self.loading = False

    async def login(self):
        """Login via the FastAPI endpoint."""
        if not self.username or not self.password:
            self.message = "Please enter username and password"
            return

        self.loading = True
        try:
            await asyncio.sleep(0.1)
            if self.username == "admin" and self.password == "secret":
                self.token = "demo_token_12345"
                self.message = "Login successful!"
            else:
                self.message = "Invalid credentials"
        except Exception as e:
            self.message = f"Login error: {str(e)}"
        finally:
            self.loading = False

    async def access_protected(self):
        """Access protected endpoint."""
        if not self.token:
            self.message = "Please login first"
            return

        self.loading = True
        try:
            await asyncio.sleep(0.1)
            self.protected_data = "This is protected data from the API!"
            self.message = "Protected data accessed successfully!"
        except Exception as e:
            self.message = f"Error accessing protected data: {str(e)}"
        finally:
            self.loading = False

    def set_username(self, value: str):
        self.username = value

    def set_password(self, value: str):
        self.password = value

    def set_new_item(self, value: str):
        self.new_item = value


def index() -> rx.Component:
    """Main page component."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Reflex + FastAPI Integration Demo", size="8"),
            rx.text(
                "This app demonstrates how to integrate Reflex with FastAPI using API transformers."
            ),
            # Status message
            rx.cond(
                State.message,
                rx.callout(
                    State.message,
                    icon="info",
                    color_scheme="blue",
                    size="1",
                ),
            ),
            # Loading indicator
            rx.cond(
                State.loading,
                rx.spinner(size="3"),
            ),
            # Items section
            rx.card(
                rx.vstack(
                    rx.heading("Items Management", size="5"),
                    rx.hstack(
                        rx.input(
                            placeholder="Enter new item",
                            value=State.new_item,
                            on_change=State.set_new_item,
                        ),
                        rx.button(
                            "Add Item",
                            on_click=State.add_item,
                            disabled=State.loading,
                        ),
                        rx.button(
                            "Load Items",
                            on_click=State.load_items,
                            disabled=State.loading,
                        ),
                    ),
                    rx.cond(
                        State.items.length() > 0,
                        rx.vstack(
                            rx.text("Current Items:", weight="bold"),
                            rx.foreach(
                                State.items,
                                lambda item: rx.badge(item, color_scheme="green"),
                            ),
                        ),
                    ),
                    spacing="3",
                ),
                width="100%",
            ),
            # Users section
            rx.card(
                rx.vstack(
                    rx.heading("Users", size="5"),
                    rx.button(
                        "Load Users",
                        on_click=State.load_users,
                        disabled=State.loading,
                    ),
                    rx.cond(
                        State.users.length() > 0,
                        rx.vstack(
                            rx.text("Users:", weight="bold"),
                            rx.foreach(
                                State.users,
                                lambda user: rx.card(
                                    rx.text(f"Name: {user['name']}"),
                                    rx.text(f"Email: {user['email']}"),
                                    size="1",
                                ),
                            ),
                        ),
                    ),
                    spacing="3",
                ),
                width="100%",
            ),
            # Stats section
            rx.card(
                rx.vstack(
                    rx.heading("Statistics", size="5"),
                    rx.button(
                        "Load Stats",
                        on_click=State.load_stats,
                        disabled=State.loading,
                    ),
                    rx.cond(
                        State.stats,
                        rx.vstack(
                            rx.text("Application Stats:", weight="bold"),
                            rx.text(f"Total Items: {State.stats['total_items']}"),
                            rx.text(f"Total Users: {State.stats['total_users']}"),
                            rx.text(f"Status: {State.stats['status']}"),
                        ),
                    ),
                    spacing="3",
                ),
                width="100%",
            ),
            # Authentication section
            rx.card(
                rx.vstack(
                    rx.heading("Authentication Demo", size="5"),
                    rx.text("Use admin/secret to login"),
                    rx.hstack(
                        rx.input(
                            placeholder="Username",
                            value=State.username,
                            on_change=State.set_username,
                        ),
                        rx.input(
                            placeholder="Password",
                            type="password",
                            value=State.password,
                            on_change=State.set_password,
                        ),
                        rx.button(
                            "Login",
                            on_click=State.login,
                            disabled=State.loading,
                        ),
                    ),
                    rx.cond(
                        State.token,
                        rx.vstack(
                            rx.badge("Logged in", color_scheme="green"),
                            rx.button(
                                "Access Protected Data",
                                on_click=State.access_protected,
                                disabled=State.loading,
                            ),
                            rx.cond(
                                State.protected_data,
                                rx.callout(
                                    State.protected_data,
                                    icon="lock",
                                    color_scheme="green",
                                ),
                            ),
                        ),
                    ),
                    spacing="3",
                ),
                width="100%",
            ),
            # API Info
            rx.card(
                rx.vstack(
                    rx.heading("Available API Endpoints", size="5"),
                    rx.text("The following endpoints are available:"),
                    rx.unordered_list(
                        rx.list_item("GET /api/items - Get all items"),
                        rx.list_item("POST /api/items - Add a new item"),
                        rx.list_item("GET /api/users - Get all users"),
                        rx.list_item("GET /api/stats - Get application statistics"),
                        rx.list_item("POST /token - Login endpoint"),
                        rx.list_item("GET /api/protected - Protected endpoint"),
                    ),
                    rx.text(
                        "You can test these endpoints directly at /docs (FastAPI Swagger UI)"
                    ),
                    spacing="3",
                ),
                width="100%",
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
            width="100%",
            max_width="800px",
        ),
        padding="2rem",
    )


# Create the Reflex app with FastAPI integration
app = rx.App(api_transformer=fastapi_app)
app.add_page(index)
