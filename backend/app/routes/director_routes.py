from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.controllers.director_controller import get_director_researchers
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.user import UserResponseSchema


router = APIRouter(
    prefix="/api/director",
    tags=["Director Panel"],
)


@router.get("/researchers", response_model=list[UserResponseSchema])
def get_researchers(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_director_researchers(db, current_user)
