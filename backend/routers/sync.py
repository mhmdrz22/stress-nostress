from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
from backend.database import get_db
from backend.models.stress_data import MoodEntryModel, AdviceFeedbackModel

router = APIRouter(tags=["Sync"])

class MoodEntrySchema(BaseModel):
    date_millis: int
    user_input: str
    category_tag: str
    has_stress: bool
    is_prediction_correct: Optional[bool] = None

class AdviceFeedbackSchema(BaseModel):
    advice_title: str
    is_liked: bool
    timestamp: int

class SyncRequest(BaseModel):
    device_id: str
    moods: List[MoodEntrySchema]
    feedbacks: List[AdviceFeedbackSchema]

@router.post("/sync")
async def sync_data(request: SyncRequest, db: AsyncSession = Depends(get_db)):
    # 1. Sync Moods
    for mood in request.moods:
        stmt = select(MoodEntryModel).where(
            MoodEntryModel.device_id == request.device_id,
            MoodEntryModel.date_millis == mood.date_millis
        )
        result = await db.execute(stmt)
        existing_mood = result.scalars().first()

        if existing_mood:
            # Update prediction feedback if it changed
            if mood.is_prediction_correct is not None:
                existing_mood.is_prediction_correct = mood.is_prediction_correct
        else:
            db_mood = MoodEntryModel(
                device_id=request.device_id,
                date_millis=mood.date_millis,
                user_input=mood.user_input,
                category_tag=mood.category_tag,
                has_stress=mood.has_stress,
                is_prediction_correct=mood.is_prediction_correct
            )
            db.add(db_mood)
        
    # 2. Sync Feedbacks
    for fb in request.feedbacks:
        stmt = select(AdviceFeedbackModel).where(
            AdviceFeedbackModel.device_id == request.device_id,
            AdviceFeedbackModel.timestamp == fb.timestamp
        )
        result = await db.execute(stmt)
        existing_fb = result.scalars().first()

        if existing_fb:
            # Update like status if it changed
            existing_fb.is_liked = fb.is_liked
        else:
            db_fb = AdviceFeedbackModel(
                device_id=request.device_id,
                advice_title=fb.advice_title,
                is_liked=fb.is_liked,
                timestamp=fb.timestamp
            )
            db.add(db_fb)
        
    await db.commit()
    return {"message": "Data synced successfully", "synced_moods": len(request.moods), "synced_feedbacks": len(request.feedbacks)}
