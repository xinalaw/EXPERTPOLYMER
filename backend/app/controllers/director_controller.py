from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User


def get_director_researchers(db: Session, current_user: User):
    if current_user.role != "director":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return (
        db.query(User)
        .filter(User.director_id == current_user.id)
        .order_by(User.id.asc())
        .all()
    )
