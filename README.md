# User API

This repository contains a sample Python API for managing users.

## API Endpoints

*   `GET /users/{user_id}`: Retrieves user details by ID.
*   `GET /users`: Lists all users.
*   `class UserProfile`: Represents a user profile.

## Example Usage

```python
from src.api.users import get_user, list_users, UserProfile

# Get user details
user = get_user(1)
print(user)

# List all users
users = list_users()
print(users)

# Create a user profile
profile = UserProfile(1)
print(profile.get_profile_data())
