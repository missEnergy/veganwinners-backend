from sqlalchemy import Column, Integer, String, Text
from app.database import Base
from sqlalchemy.orm import relationship, backref


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String(255), nullable=False)
    instructions = Column(String(1000), nullable=False)
    img = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    time = Column(String(255), nullable=False)
    people = Column(Integer, nullable=False)
    owner = Column(String(255), nullable=False)
    ingredients = relationship('Ingredient', backref='ingredient')

    def __init__(self, title, instructions, img, type, time, people, owner):
        self.title = title
        self.instructions = instructions
        self.img = img
        self.type = type
        self.time = time
        self.people = people
        self.owner = owner

    def __repr__(self):
        return '<{} {!r}>'.format(self.__type__.__name__, self.name)

