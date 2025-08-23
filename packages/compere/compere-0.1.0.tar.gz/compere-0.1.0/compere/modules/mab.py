from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import numpy as np
from math import sqrt, log

from .database import get_db
from .models import Entity, Comparison

router = APIRouter()

class UCB:
    def __init__(self, n_arms):
        self.n_arms = n_arms
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)
        self.total_count = 0

    def select_arm(self):
        ucb_values = np.zeros(self.n_arms)
        for arm in range(self.n_arms):
            if self.counts[arm] == 0:
                return arm
            ucb_values[arm] = self.values[arm] + sqrt(2 * log(self.total_count) / self.counts[arm])
        return np.argmax(ucb_values)

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] += 1
        n = self.counts[chosen_arm]
        value = self.values[chosen_arm]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[chosen_arm] = new_value
        self.total_count += 1

def get_ucb_instance(db: Session):
    n_entities = db.query(Entity).count()
    return UCB(n_entities)

def get_entity_arm_mapping(db: Session):
    entities = db.query(Entity).all()
    return {i: entity.id for i, entity in enumerate(entities)}

@router.get("/mab/next_comparison")
def get_next_comparison(db: Session = Depends(get_db)):
    ucb = get_ucb_instance(db)
    arm_entity_mapping = get_entity_arm_mapping(db)

    arm1 = ucb.select_arm()
    arm2 = ucb.select_arm()
    while arm2 == arm1:
        arm2 = ucb.select_arm()

    entity1 = db.query(Entity).get(arm_entity_mapping[arm1])
    entity2 = db.query(Entity).get(arm_entity_mapping[arm2])

    return {"entity1": entity1, "entity2": entity2}

@router.post("/mab/update")
def update_mab(comparison_id: int, db: Session = Depends(get_db)):
    comparison = db.query(Comparison).get(comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")

    ucb = get_ucb_instance(db)
    arm_entity_mapping = get_entity_arm_mapping(db)
    entity_arm_mapping = {v: k for k, v in arm_entity_mapping.items()}

    arm1 = entity_arm_mapping[comparison.entity1_id]
    arm2 = entity_arm_mapping[comparison.entity2_id]

    # Update UCB based on the comparison result
    if comparison.selected_entity_id == comparison.entity1_id:
        ucb.update(arm1, 1)
        ucb.update(arm2, 0)
    elif comparison.selected_entity_id == comparison.entity2_id:
        ucb.update(arm1, 0)
        ucb.update(arm2, 1)
    else:
        ucb.update(arm1, 0.5)
        ucb.update(arm2, 0.5)

    # You might want to store the updated UCB values in the database
    # This is a simplified example; in practice, you'd need a more robust
    # way to persist the UCB state across requests

    return {"message": "MAB updated successfully"}