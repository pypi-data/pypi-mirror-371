from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .database import get_db
from .models import Entity

router = APIRouter()

def generate_embedding(entity: Entity):
    # This is a placeholder function. In a real implementation, you would use
    # an LLM or another ML model to generate embeddings based on the entity's
    # text and image data.
    return np.random.rand(100)  # Return a random 100-dimensional vector

def get_similar_entities(db: Session, n=2):
    entities = db.query(Entity).all()
    if len(entities) < n:
        return entities

    embeddings = np.array([generate_embedding(entity) for entity in entities])
    similarities = cosine_similarity(embeddings)

    # Select two entities with highest similarity
    most_similar_pair = np.unravel_index(np.argmax(similarities), similarities.shape)
    return [entities[most_similar_pair[0]], entities[most_similar_pair[1]]]

@router.get("/similar_entities")
def get_similar_entities_route(db: Session = Depends(get_db)):
    return get_similar_entities(db)