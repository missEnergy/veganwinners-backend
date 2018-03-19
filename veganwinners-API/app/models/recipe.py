from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String(255), nullable=False)
    directions = Column(Text, nullable=False)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<{} {!r}>'.format(self.__type__.__name__, self.name)
