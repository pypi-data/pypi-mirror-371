from sqlalchemy import Column, Integer, String, SmallInteger, TIMESTAMP, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MonitorState(Base):
    """
    Monitor_State table class
    """
    __tablename__ = 'monitor_state'

    Id = Column(Integer, name="Id", primary_key=True, autoincrement=True)
    Site = Column(String(20), name="Site", nullable=False)
    Area = Column(String(20), name="Area", nullable=False)
    Line = Column(String(20), name="Line", nullable=False)
    Station = Column(String(20), name="Station", nullable=False)
    State = Column(Integer, name="State", nullable=False)
    StartTime = Column(TIMESTAMP, name="StartTime", nullable=False)
    EndTime = Column(TIMESTAMP, name="EndTime", nullable=False)