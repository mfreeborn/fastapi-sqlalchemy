from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from fastapi_sqlalchemy import db


# Define the User class representing the "users" database table
# Using the SQLAlchemy Base property instead of defining your own
class User(db.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}',email='{self.email}')"
