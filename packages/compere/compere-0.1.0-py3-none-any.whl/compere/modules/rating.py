from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import Entity

router = APIRouter()

K_FACTOR = 32

def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo_ratings(db: Session, entity1: Entity, entity2: Entity, winner_id: int):
    expected_a = expected_score(entity1.rating, entity2.rating)
    expected_b = 1 - expected_a

    if winner_id == entity1.id:
        score_a, score_b = 1, 0
    elif winner_id == entity2.id:
        score_a, score_b = 0, 1
    else:
        score_a, score_b = 0.5, 0.5

    entity1.rating += K_FACTOR * (score_a - expected_a)
    entity2.rating += K_FACTOR * (score_b - expected_b)

    db.commit()

@router.get("/ratings")
def get_ratings(db: Session = Depends(get_db)):
    return db.query(Entity).order_by(Entity.rating.desc()).all()