from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from app.database import Base
from app.models.recipe import Recipe


class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    recipe_id = Column(Integer, ForeignKey(Recipe.id))
    credit = Column(String(255), nullable=False)
    text = Column(String(1000), nullable=False)
    approved = Column(Boolean, default=True)

    def __init__(self, credit, text, approved):
        self.credit = credit
        self.text = text
        self.approved = approved

    def __repr__(self):
        return '<{} {!r}>'.format(self.__type__.__name__, self.name)
