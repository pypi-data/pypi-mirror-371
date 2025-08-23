from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import get_db
from .models import Comparison, ComparisonCreate, ComparisonOut, Entity
from .rating import update_elo_ratings
from .similarity import get_similar_entities

router = APIRouter()

@router.post("/comparisons/", response_model=ComparisonOut)
async def create_comparison(
    comparison: ComparisonCreate,
    db: Session = Depends(get_db)
):
    # Check if entities exist
    entity1 = db.query(Entity).filter(Entity.id == comparison.entity1_id).first()
    entity2 = db.query(Entity).filter(Entity.id == comparison.entity2_id).first()
    if not entity1 or not entity2:
        raise HTTPException(status_code=404, detail="One or both entities not found")

    # Create comparison
    db_comparison = Comparison(**comparison.dict())
    db.add(db_comparison)
    db.commit()
    db.refresh(db_comparison)

    # Update Elo ratings
    update_elo_ratings(db, entity1, entity2, comparison.selected_entity_id)

    return db_comparison

@router.get("/comparisons/next")
async def get_next_comparison(user_id: int, db: Session = Depends(get_db)):
    entities = get_similar_entities(db)
    if len(entities) < 2:
        raise HTTPException(status_code=404, detail="Not enough entities for comparison")
    return {"entity1": entities[0], "entity2": entities[1]}
