from sqlalchemy import create_engine, Column, Integer, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from . import utils

Base = declarative_base()
db_init = False
db = None

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    forwarded_to = Column(Integer)
    last_forward_message_id = Column(Integer)
    paused = Column(Boolean, default=False)

def get_db():
    if db_init:
        return db

    config = utils.get_config()

    utils.make_path(config.db_location)

    engine = create_engine("sqlite://"+config.db_location.strip("."))

    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    return db
