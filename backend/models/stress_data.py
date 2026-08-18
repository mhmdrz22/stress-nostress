from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, UniqueConstraint
from backend.database import Base
import datetime

class MoodEntryModel(Base):
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    date_millis = Column(Integer)
    user_input = Column(String)
    category_tag = Column(String)
    has_stress = Column(Boolean)
    is_prediction_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('device_id', 'date_millis', name='uix_device_date'),
    )

class AdviceFeedbackModel(Base):
    __tablename__ = "advice_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    advice_title = Column(String)
    is_liked = Column(Boolean)
    timestamp = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('device_id', 'timestamp', name='uix_device_time'),
    )
