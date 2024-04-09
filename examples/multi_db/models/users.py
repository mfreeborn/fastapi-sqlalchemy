# Import necessary modules and classes
from sqlalchemy import Column, Integer, String, create_engine  # Import SQLAlchemy components
from sqlalchemy.orm import (  # Import SQLAlchemy components
    DeclarativeMeta,
    declarative_base,
    sessionmaker,
)

from fastapi_sqlalchemy import SQLAlchemy  # Import the SQLAlchemy extension

from . import BaseModel  # Import the custom BaseModel

# Create a SQLAlchemy instance with a connection to the SQLite database "user.db"
user_db = SQLAlchemy("sqlite:///user.db")


# Define the User class representing the "users" database table
# Using the SQLAlchemy Base property instead of defining your own
# And inheriting from the BaseModel class for type hinting and helpful builtin methods and properties
class User(BaseModel, user_db.Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): The primary key of the user.
        name (str): The name of the user.
        email (str): The email address of the user.
    """

    # Name of the database table associated with this class
    __tablename__ = "users"

    # Columns corresponding to the attributes of the User class
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
