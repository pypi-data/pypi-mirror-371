from sqlalchemy import Column, Integer, String, SmallInteger, TIMESTAMP, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Alarm(Base):
    """
    Alarm table class
    """
    __tablename__ = 'alarm'

    Id = Column(Integer, name="Id", primary_key=True, autoincrement=True)
    Site = Column(String(20), name="Site", nullable=False)
    Area = Column(String(20), name="Area", nullable=False)
    Line = Column(String(20), name="Line", nullable=False)
    Station = Column(String(20), name="Station", nullable=False)
    AlarmType = Column(String(20), name="AlarmType", nullable=False)
    ReminderType = Column(String(100), name="ReminderType", nullable=False)
    AlarmContent = Column(String(100), name="AlarmContent", nullable=False)
    Severity = Column(SmallInteger, name="Severity", nullable=False)
    EventTime = Column(TIMESTAMP, name="EventTime", nullable=False)
    CreatedTime = Column(TIMESTAMP, name="CreatedTime", nullable=False)