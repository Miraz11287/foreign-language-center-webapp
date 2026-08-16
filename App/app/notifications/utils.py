from app.extensions import db
from app.models.notification import Notification


def notify(user_id: int, message: str, link: str = None) -> None:
    db.session.add(Notification(user_id=user_id, message=message, link=link))
    db.session.commit()
