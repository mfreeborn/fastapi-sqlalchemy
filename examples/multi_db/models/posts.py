from sqlalchemy import Column, Integer, MetaData, String, create_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker

from fastapi_sqlalchemy import SQLAlchemy

from . import BaseModel

# Create a SQLAlchemy instance with a connection to the SQLite database "post.db"
post_db = SQLAlchemy("sqlite:///post.db")


# Define the User class representing the "posts" database table
# using the SQLAlchemy Base property instead of defining your own
# And inheriting from the BaseModel class for type hinting and helpful builtin methods and properties
class Post(BaseModel, post_db.Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    user_id = Column(Integer)
