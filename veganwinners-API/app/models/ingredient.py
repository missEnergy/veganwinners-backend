from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base
from app.models.recipes import Recipe


class Ingredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    recipe_id = Column(Integer, ForeignKey(Recipe.id), primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)
    quantity = Column(String(255), nullable=False)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<{} {!r}>'.format(self.__type__.__name__, self.name)
