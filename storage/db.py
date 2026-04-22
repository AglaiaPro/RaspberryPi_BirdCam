from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from storage.models import Base

DATABASE_URL = 'sqlite:///device.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    return Session()