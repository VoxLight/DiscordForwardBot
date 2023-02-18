import sqlalchemy.exc
import sqlite3
from sqlalchemy import (
    create_engine, 
    Column, 
    Integer, 
    String, 
    ForeignKey, 
    Table, 
    JSON,
    exc,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from . import utils

Base = declarative_base()
db_init = False
db = None

guild_channel_table = Table('guild_channel', Base.metadata,
    Column('guild_id', Integer, ForeignKey('guilds.id')),
    Column('channel_id', Integer, ForeignKey('channels.id'))
)

class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    channels = relationship('Channel', secondary=guild_channel_table, backref='guilds')


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    forwards = Column(JSON)
    last_forward_message_id = Column(Integer)




def get_db():
    if db_init:
        return db

    config = utils.get_config()

    utils.make_path(config.db_location)

    engine = create_engine("sqlite://"+config.db_location.strip("."))

    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    return db
