from libgravatar import Gravatar
from sqlalchemy.orm import Session

from models import User
from schemas import UserModel

async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieve a user from the database by their email.

    :param email: The email address of the user.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user that matches the provided email, or None if not found.
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user in the database and set their avatar from Gravatar if available.

    :param body: The data for creating the user, including email and password.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user with the avatar URL from Gravatar.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user.

    :param user: The user whose token needs to be updated.
    :type user: User
    :param token: The new refresh token, or None to invalidate it.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
    Mark a user's email as confirmed in the database.

    :param email: The email address of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar URL for a user.

    :param email: The email address of the user.
    :type email: str
    :param url: The new avatar URL to set for the user.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The updated user with the new avatar URL.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


