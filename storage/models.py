from datetime import datetime

from sqlalchemy import Integer, Column, String, DateTime, Float, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    device_id = Column(String, default='raspberry-1')
    timestamp = Column(String)

    temperature = Column(Float)
    media_path = Column(String)

    file_url = Column(String, nullable=True)

    event_type = Column(String)
    synced = Column(Boolean, default=False)
