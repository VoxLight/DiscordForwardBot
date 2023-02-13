from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True)
    channels = relationship('Channel', back_populates='guild')

class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    guild = relationship('Guild', back_populates='channels')
    forwards = relationship('Channel', secondary='channel_forward', back_populates='receivers')
    receivers = relationship('Channel', secondary='channel_forward', back_populates='forwards')

channel_forward = Table('channel_forward', Base.metadata,
    Column('forwarding_id', Integer, ForeignKey('channels.id')),
    Column('receiving_id', Integer, ForeignKey('channels.id'))
)

    



engine = create_engine('sqlite:///forward.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Add a guild to the database
guild = Guild(name='Test Guild', server_id='1234567890', owner_id='0987654321')
session.add(guild)

# Add channels to the guild
channel_1 = Channel(name='Channel 1', channel_id='abcdefghij', guild_id=guild.id, forward_to=None)
channel_2 = Channel(name='Channel 2', channel_id='klmnopqrst', guild_id=guild.id, forward_to='abcdefghij')
session.add(channel_1)
session.add(channel_2)

session.commit()

# Query the database for all guilds and their channels
guilds = session.query(Guild).all()
for guild in guilds:
    print(guild.id, guild.name, guild.server_id, guild.owner_id)
    channels = session.query(Channel).filter_by(guild_id=guild.id).all()
    for channel in channels:
        print(channel.id, channel.name, channel.channel_id, channel.forward_to)

# Close the session
session.close()