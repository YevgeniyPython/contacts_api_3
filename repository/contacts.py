from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import models, schemas
from datetime import datetime, timedelta

async def create_contact(db: Session, body: schemas.ContactCreate, user: models.User):
    """
    Create a new contact for a specific user in the database.

    The function takes the contact information from the provided schema, associates it with the user, 
    and saves the new contact to the database.

    :param db: The database session.
    :type db: Session
    :param contact: The schema containing the contact information to be created.
    :type contact: schemas.ContactCreate
    :param user: The user for whom the contact is being created.
    :type user: models.User
    :return: The newly created contact object after being saved to the database.
    :rtype: models.Contact

    Process:
        - The contact data is unpacked from the schema and used to create a new Contact instance.
        - The new contact is associated with the given user via the `user_id`.
        - The contact is added to the database, committed, and refreshed to reflect the latest state.
    """
    contact = models.Contact(**body.model_dump(), user_id = user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def get_contact(db: Session, contact_id: int, user: models.User):
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param db: The database session.
    :type db: Session
    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: models.Contact | None
    """
    return db.query(models.Contact).filter(and_(models.Contact.user_id == user.id, models.Contact.id == contact_id)).first()

async def get_contacts(db: Session, user: models.User, skip: int = 0, limit: int = 10):
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve contacts for.
    :type user: User
    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contactss to return.
    :type limit: int
    :return: A list of contacts.
    :rtype: List[models.Contact]
    """
    return db.query(models.Contact).filter(models.Contact.user_id == user.id).offset(skip).limit(limit).all()

async def update_contact(db: Session, contact_id: int, body: schemas.ContactUpdate, user: models.User):
    """
    Update an existing contact for a specific user in the database.

    The function searches for a contact by its ID and the associated user, updates the contact's details with 
    the provided data, and commits the changes to the database.

    :param db: The database session.
    :type db: Session
    :param contact_id: The ID of the contact to be updated.
    :type contact_id: int
    :param contact: The schema containing the updated contact information.
    :type contact: schemas.ContactUpdate
    :param user: The user who owns the contact.
    :type user: models.User
    :return: The updated contact object after being saved to the database.
    :rtype: models.Contact

    Process:
        1. Query the database for the contact by its `contact_id` and `user_id`.
        2. For each key-value pair in the `contact` schema, update the corresponding attribute of the `db_contact`.
        3. Commit the changes to the database.
        4. Return the updated `db_contact` object.
    """
    db_contact = db.query(models.Contact).filter(and_(models.Contact.user_id == user.id, models.Contact.id == contact_id)).first()
    if db_contact is None:
        return None
    else:
        for key, value in body.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        return db_contact

async def delete_contact(db: Session, contact_id: int, user: models.User):
    """
    Delete an existing contact for a specific user from the database.

    The function searches for a contact by its ID and the associated user, deletes the contact from the database, 
    and commits the change.

    :param db: The database session.
    :type db: Session
    :param contact_id: The ID of the contact to be deleted.
    :type contact_id: int
    :param user: The user who owns the contact.
    :type user: models.User
    :return: The contact object before it was deleted.
    :rtype: models.Contact

    Process:
        1. Query the database for the contact by its `contact_id` and `user_id` to ensure it belongs to the user.
        2. If the contact is found, delete it from the database.
        3. Commit the changes to the database.
        4. Return the `db_contact` object that was deleted.
    """
    db_contact = db.query(models.Contact).filter(and_(models.Contact.user_id == user.id, models.Contact.id == contact_id)).first()
    db.delete(db_contact)
    db.commit()
    return db_contact

async def search_contacts(db: Session, query: str, user: models.User):
    """
    Search for contacts that match a query string for a specific user in the database.

    The function searches the user's contacts by first name, last name, or email, using a case-insensitive 
    match (ILIKE) for the given query string.

    :param db: The database session.
    :type db: Session
    :param query: The search string to match against the contact's first name, last name, or email.
    :type query: str
    :param user: The user whose contacts are being searched.
    :type user: models.User
    :return: A list of contacts that match the search query.
    :rtype: list[models.Contact]

    Process:
        1. Query the database for contacts associated with the user.
        2. Apply case-insensitive filters on the `first_name`, `last_name`, and `email` fields to match the `query`.
        3. Return all matching contacts.
    """
    return db.query(models.Contact).filter(models.Contact.user_id == user.id).filter(
        models.Contact.first_name.ilike(f"%{query}%") |
        models.Contact.last_name.ilike(f"%{query}%") |
        models.Contact.email.ilike(f"%{query}%")
    ).all()

async def get_birthdays_in_next_7_days(db: Session, user: models.User):
    """
    Retrieve contacts whose birthdays fall within the next 7 days for a specific user.

    The function filters the user's contacts to find those whose birthdays are between the current date
    and 7 days from now.

    :param db: The database session.
    :type db: Session
    :param user: The user whose contacts are being searched.
    :type user: models.User
    :return: A list of contacts with birthdays in the next 7 days.
    :rtype: List[models.Contact]

    Process:
        1. Retrieve the current date and the date 7 days from now.
        2. Fetch all contacts for the user from the database.
        3. Check if the contacts' birthdays fall within the range from today to 7 days ahead.
        4. Return a list of contacts with upcoming birthdays.
    """
    today = datetime.now().date()
    next_week = today + timedelta(days=7)    
    contacts = db.query(models.Contact).filter(models.Contact.user_id == user.id).all()
    if contacts is None:
        return None
    else:
        upcoming_birthdays = [contact for contact in contacts if today <= contact.birthday.replace(year=today.year) <= next_week]
        if upcoming_birthdays is None:
            return None
        else:
            upcoming_birthdays = [contact for contact in contacts if today <= contact.birthday.replace(year=today.year) <= next_week]
            return upcoming_birthdays
