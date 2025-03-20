from sqlalchemy import Column, Integer, String, Text
from database import Base


class RecipeModel(Base):
    __tablename__ = "recipes"
    #__table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    views = Column(Integer, default=0)
    cooking_time = Column(Integer)
    ingredients = Column(Text)
    description = Column(Text)
