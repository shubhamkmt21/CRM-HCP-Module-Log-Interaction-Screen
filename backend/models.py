from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time
from datetime import datetime
from database import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), index=True)
    interaction_type = Column(String(50))
    interaction_date = Column(String(50), nullable=True) # string for simplicity
    interaction_time = Column(String(50), nullable=True)
    attendees = Column(String(255), nullable=True)
    notes = Column(Text) # Topics Discussed
    materials_shared = Column(Text, nullable=True)
    samples_distributed = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    outcomes = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
