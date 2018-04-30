from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import config

engine = create_engine(config.DATABASE_URI,
                       encoding='utf-8',
                       max_overflow=10,
                       pool_recycle=240,
                       pool_size=20,
                       )

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
    # Base.metadata.bind = engine


def clear_sessions():
    db_session.remove()
