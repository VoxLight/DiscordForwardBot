"""
   Copyright 2023 VoxLight

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

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
