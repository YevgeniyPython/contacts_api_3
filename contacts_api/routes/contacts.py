from fastapi import Depends, HTTPException
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from typing import List

from repository import contacts as repository_contacts
import models, schemas
from db import get_db
from services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=["contacts"])


# Создать новый контакт
@router.post("/", response_model=schemas.ContactResponse)
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), 
                         current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Create a new contact for the authenticated user.

    :param contact: The contact information to be created.
    :type contact: schemas.ContactCreate
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: models.User
    :return: The created contact information.
    :rtype: schemas.ContactResponse
    """
    return await repository_contacts.create_contact(db, contact, current_user)

# Получить список всех контактов
@router.get("/", response_model=List[schemas.ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Retrieve a list of contacts for the authenticated user, with optional pagination.

    :param skip: The number of contacts to skip for pagination.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: models.User
    :return: A list of contacts.
    :rtype: List[schemas.ContactResponse]
    """
    contacts = await repository_contacts.get_contacts(db, current_user, skip, limit)
    return contacts

# Получить один контакт по идентификатору
@router.get("/{contact_id}", response_model=schemas.ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db), 
                         current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Retrieve a contact by its ID for the authenticated user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: models.User
    :return: The contact information.
    :rtype: schemas.ContactResponse
    :raises HTTPException: If the contact is not found (404).
    """
    db_contact = await repository_contacts.get_contact(db, contact_id, current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Обновить контакт
@router.put("/{contact_id}", response_model=schemas.ContactResponse)
async def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), 
                         current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Update the details of an existing contact for the authenticated user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param contact: The updated contact data.
    :type contact: schemas.ContactUpdate
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: models.User
    :return: The updated contact information.
    :rtype: schemas.ContactResponse
    :raises HTTPException: If the contact is not found (404).
    """
    contact = await repository_contacts.update_contact(db, contact_id, contact, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

# Удалить контакт
@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db), 
                         current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Delete a contact by its ID for the authenticated user.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: models.User
    :return: A message indicating the contact has been deleted.
    :rtype: dict
    :raises HTTPException: If the contact is not found (404).
    """
    contact = await repository_contacts.delete_contact(db, contact_id, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

# Поиск по имени, фамилии или email
@router.get("/contacts/search/", response_model=List[schemas.ContactResponse])
async def search_contacts(query: str, db: Session = Depends(get_db), 
                         current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Search contacts by first name, last name, or email for the authenticated user.

    :param query: The search term for filtering contacts.
    :type query: str
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: models.User
    :return: A list of contacts matching the search query.
    :rtype: List[schemas.ContactResponse]
    :raises HTTPException: If no matching contacts are found (404).
    """
    contact = await repository_contacts.search_contacts(db, query, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

# Контакты с днями рождения в ближайшие 7 дней
@router.get("/contacts/birthdays/", response_model=List[schemas.ContactResponse])
async def upcoming_birthdays(db: Session = Depends(get_db), 
                         current_user: models.User = Depends(auth_service.get_current_user)):
    """
    Retrieve a list of contacts who have birthdays in the next 7 days for the authenticated user.

    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: models.User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[schemas.ContactResponse]
    :raises HTTPException: If no contacts with upcoming birthdays are found (404).
    """
    contact = await repository_contacts.get_birthdays_in_next_7_days(db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

