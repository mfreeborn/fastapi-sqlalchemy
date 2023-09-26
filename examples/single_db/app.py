from typing import Optional

from fastapi import FastAPI
from models import User, db
from pydantic import BaseModel

from fastapi_sqlalchemy import DBSessionMiddleware

app = FastAPI()

# Add SQLAlchemy session middleware to manage database sessions
app.add_middleware(DBSessionMiddleware, db=db)


# Endpoint to retrieve all users
@app.get("/users")
def get_users():
    """
    Retrieve a list of all users.

    Returns:
        List[User]: A list of User objects.
    """
    return User.query.all()


# Pydantic model for creating new users
class UserCreate(BaseModel):
    name: str
    email: str


# Endpoint to add a new user
@app.post("/add_user")
def add_user(user_data: UserCreate):
    """
    Add a new user to the database.

    Args:
        user_data (UserCreate): User data including name and email.

    Returns:
        dict: A message indicating the success of the operation.
    """
    user = User(**user_data.model_dump())
    print(user)
    user.save()
    return {"message": "User created successfully"}


# Pydantic model for updating user information
class UserUpdate(UserCreate):
    id: int
    name: Optional[str]
    email: Optional[str]


# Endpoint to update user information
@app.post("/update_user")
def update_user(user_data: UserUpdate):
    """
    Update user information in the database.

    Args:
        user_data (UserUpdate): User data including ID, name, and email for updating.

    Returns:
        dict: A message indicating the success of the operation.
    """
    user = User.query.filter_by(id=user_data.id).first()
    print(user)
    user.update(**user_data.model_dump())
    user.save()
    return {"message": "User updated successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
