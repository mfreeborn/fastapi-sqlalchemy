from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from fastapi_sqlalchemy import ModelBase, SQLAlchemy

db = SQLAlchemy(url="sqlite:///example.db")


# Define the User class representing the "users" database table
# Using the SQLAlchemy Base property instead of defining your own
# And inheriting from the BaseModel class for type hinting and helpful builtin methods and properties
class User(ModelBase, db.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}',email='{self.email}')"
