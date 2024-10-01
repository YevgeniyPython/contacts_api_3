from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from db import get_db
from schemas import UserModel, UserResponse, TokenModel, RequestEmail
from repository import users as repository_users
from services.auth import auth_service
from services.email import send_email


router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user, hash the password, and send a confirmation email.

    :param body: UserModel schema containing user registration data.
    :type body: UserModel
    :param background_tasks: Used to schedule sending the confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: The HTTP request object, used to get the base URL.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: A response with the newly created user and a success message.
    :rtype: dict
    :raises HTTPException: If the user already exists (status 409).
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user with email and password, then issue a JWT access and refresh token.

    :param body: Form data containing the user's login credentials (username, password).
    :type body: OAuth2PasswordRequestForm
    :param db: Database session.
    :type db: Session
    :return: A response containing the access and refresh tokens.
    :rtype: dict
    :raises HTTPException: If the user is not found, email is not confirmed, or the password is invalid (status 401).
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refresh the access and refresh tokens using the provided refresh token.

    :param credentials: The refresh token from the Authorization header.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Database session.
    :type db: Session
    :return: A new access token and refresh token.
    :rtype: dict
    :raises HTTPException: If the refresh token is invalid (status 401).
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm the user's email address using the confirmation token.

    :param token: The email confirmation token.
    :type token: str
    :param db: Database session.
    :type db: Session
    :return: A success message or a notice that the email is already confirmed.
    :rtype: dict
    :raises HTTPException: If the user is not found or the token is invalid (status 400).
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Request email confirmation for a user who hasn't confirmed their email yet.

    :param body: RequestEmail schema containing the user's email address.
    :type body: RequestEmail
    :param background_tasks: Used to schedule sending the confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: The HTTP request object, used to get the base URL.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: A message indicating whether the confirmation email was sent or if the email is already confirmed.
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}



