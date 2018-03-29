from sqlalchemy import Column, Integer, String, Text
from app.database import Base
from sqlalchemy.orm import relationship, backref


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String(255), nullable=False)
    instructions = Column(String(1000), nullable=False)
    ingredients = relationship('Ingredient', backref='ingredient')

    def __init__(self, title, instructions):
        self.title = title
        self.instructions = instructions

    def __repr__(self):
        return '<{} {!r}>'.format(self.__type__.__name__, self.name)
