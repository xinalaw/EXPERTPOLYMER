from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.models.user import User


def is_admin(user: User) -> bool:
    return user.role == "admin"


def is_director(user: User) -> bool:
    return user.role == "director"


def is_researcher(user: User) -> bool:
    return user.role == "researcher"


def can_search_users(user: User) -> bool:
    return is_admin(user) or is_director(user)


def can_access_analysis_result(
    db: Session,
    current_user: User,
    analysis_result: AnalysisResult,
) -> bool:
    if is_admin(current_user):
        return True

    if is_researcher(current_user):
        return analysis_result.user_id == current_user.id

    if is_director(current_user):
        researcher = db.query(User).filter(User.id == analysis_result.user_id).first()

        return bool(researcher and researcher.director_id == current_user.id)

    return False


def can_delete_analysis_result(
    db: Session,
    current_user: User,
    analysis_result: AnalysisResult,
) -> bool:
    return can_access_analysis_result(
        db=db,
        current_user=current_user,
        analysis_result=analysis_result,
    )


def can_access_user_history(
    db: Session,
    current_user: User,
    target_user_id: int,
) -> bool:
    if is_admin(current_user):
        return True

    if is_researcher(current_user):
        return current_user.id == target_user_id

    if is_director(current_user):
        researcher = db.query(User).filter(User.id == target_user_id).first()

        return bool(researcher and researcher.director_id == current_user.id)

    return False
