# Import necessary modules and classes
from typing import Optional

from fastapi import FastAPI
from models.posts import Post, post_db  # Import the Post model and post_db database instance
from models.users import User, user_db  # Import the User model and user_db database instance
from pydantic import BaseModel

from fastapi_sqlalchemy import (
    DBSessionMiddleware,  # Import the DBSessionMiddleware for database sessions
)

# Create a FastAPI application instance
app = FastAPI()

# Add the DBSessionMiddleware as a middleware to the FastAPI app, connecting it to the specified databases
app.add_middleware(DBSessionMiddleware, db=[post_db, user_db])


# Define an endpoint for retrieving all users
@app.get("/users")
def get_users():
    """
    Endpoint to retrieve a list of all users.
    Returns:
        List[User]: A list of User objects representing all users in the database.
    """
    return User.get_all()


# Define a Pydantic model for creating a new user
class UserCreate(BaseModel):
    name: str
    email: str


# Define an endpoint for adding a new user
@app.post("/add_user")
def add_user(user_data: UserCreate):
    """
    Endpoint to add a new user to the database.
    Args:
        user_data (UserCreate): User data provided in the request body.
    Returns:
        dict: A message indicating the success of the operation.
    """
    user = User(**user_data.dict())
    user.save()
    return {"message": "User created successfully"}


# Define a Pydantic model for updating user information
class UserUpdate(UserCreate):
    id: int
    name: Optional[str]
    email: Optional[str]


# Define an endpoint for updating user information
@app.post("/update_user")
def update_user(user_data: UserUpdate):
    """
    Endpoint to update user information in the database.
    Args:
        user_data (UserUpdate): User data provided in the request body.
    Returns:
        dict: A message indicating the success of the operation.
    """
    user = User.get(id=user_data.id)
    user.update(**user_data.dict())
    user.save()
    return {"message": "User updated successfully"}


# Define a Pydantic model for retrieving posts by user ID
class UserPosts(BaseModel):
    user_id: int


# Define an endpoint for retrieving posts by user ID
@app.get("/posts")
def get_posts(user: UserPosts):
    """
    Endpoint to retrieve posts by a specific user ID.
    Args:
        user (UserPosts): User ID provided in the query parameters.
    Returns:
        List[Post]: A list of Post objects belonging to the specified user.
    """
    posts = Post.get_all(user_id=user.user_id)
    return posts


# Define a Pydantic model for creating a new post
class PostCreate(UserPosts):
    title: str
    content: str


# Define an endpoint for adding a new post
@app.post("/add_post")
def add_post(post_data: PostCreate):
    """
    Endpoint to add a new post to the database.
    Args:
        post_data (PostCreate): Post data provided in the request body.
    Returns:
        dict: A message indicating the success of the operation.
    """
    post = Post(**post_data.dict())
    post.save()
    return {"message": "Post created successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
