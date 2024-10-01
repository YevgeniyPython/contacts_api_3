import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from datetime import datetime, timedelta

from models import Contact, User
from schemas import ContactUpdate, ContactCreate
from repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    delete_contact,
    update_contact,
    search_contacts,
    get_birthdays_in_next_7_days,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    # async def test_get_contacts(self):
    #     contacts = [Contact(), Contact(), Contact()]
    #     self.session.query().filter().offset().limit().all.return_value = contacts
    #     result = await get_contacts(db=self.session, user=self.user, skip=0, limit=10)
    #     self.assertEqual(result, contacts)

    # async def test_get_contact_found(self):
    #     contact = Contact()
    #     self.session.query().filter().first.return_value = contact
    #     result = await get_contact(db=self.session, contact_id=1, user=self.user)
    #     self.assertEqual(result, contact)

    # async def test_get_contact_not_found(self):
    #     self.session.query().filter().first.return_value = None
    #     result = await get_contact(db=self.session, contact_id=1, user=self.user)
    #     self.assertIsNone(result)

    # async def test_create_contact(self):
    #     body = ContactCreate(first_name="John", last_name="Doe", 
    #                    email="test@api.com", phone_number="0123456789",  
    #                    birthday="2000-01-10", additional_info="test contact")
    #     result = await create_contact(db=self.session, body=body, user=self.user)
    #     self.assertEqual(result.first_name, body.first_name)
    #     self.assertEqual(result.last_name, body.last_name)
    #     self.assertEqual(result.email, body.email)
    #     self.assertEqual(result.phone_number, body.phone_number)
    #     self.assertEqual(result.birthday, body.birthday)
    #     self.assertEqual(result.additional_info, body.additional_info)
    #     self.assertTrue(hasattr(result, "id"))

    # async def test_delete_contact_found(self):
    #     contact = Contact()
    #     self.session.query().filter().first.return_value = contact
    #     result = await delete_contact(db=self.session, contact_id=1, user=self.user)
    #     self.assertEqual(result, contact)

    # async def test_delete_contact_not_found(self):
    #     self.session.query().filter().first.return_value = None
    #     result = await delete_contact(db=self.session, contact_id=1, user=self.user)
    #     self.assertIsNone(result)

    # async def test_update_contact_found(self):
    #     body = ContactUpdate(first_name="John", last_name="Doe", 
    #                    email="test@api.com", phone_number="0123456789",  
    #                    birthday="2000-01-10", additional_info="test contact")
    #     contact = Contact()
    #     self.session.query().filter().first.return_value = contact
    #     self.session.commit.return_value = None
    #     result = await update_contact(db=self.session, contact_id=1, body=body, user=self.user)
    #     self.assertEqual(result, contact)

    # async def test_update_contact_not_found(self):
    #     body = ContactUpdate(first_name="John", last_name="Doe", 
    #                    email="test@api.com", phone_number="0123456789",  
    #                    birthday="2000-01-10", additional_info="test contact")
    #     self.session.query().filter().first.return_value = None
    #     self.session.commit.return_value = None
    #     result = await update_contact(db=self.session, contact_id=1, body=body, user=self.user)
    #     self.assertIsNone(result)

    # async def test_get_birthdays_in_next_7_days_found(self):
    #     today = datetime.now().date()
    #     # next_week = today + timedelta(days=7)
    #     contacts = [Contact(birthday=today),
    #                 Contact(birthday=today+timedelta(days=4)),
    #                 Contact(birthday=today-timedelta(days=362)),
    #                 Contact(birthday=today-timedelta(days=2)), # Birthday already passed
    #                 Contact(birthday=today+timedelta(days=8)), # Birthday outside 7-day range
    #                 ]
    #     self.session.query().filter().all.return_value = contacts
    #     result = await get_birthdays_in_next_7_days(db=self.session, user=self.user)
    #     self.assertEqual(result, [contacts[0], contacts[1], contacts[2]])

    # async def test_get_birthdays_in_next_7_days_not_found(self):
    #     self.session.query().filter().all.return_value = None
    #     result = await get_birthdays_in_next_7_days(db=self.session, user=self.user)
    #     self.assertIsNone(result)


    async def test_search_contact_found(self):
        contacts = [Contact(first_name="John", last_name="Doe", email="johndoe@example.com"),
                    Contact(first_name="Jake", last_name="Smith", email="jakesmith@example.com"),
                    Contact(first_name="Jane", last_name="Doe", email="janedoe@example.com")
                    ]
        self.session.query().filter().filter().all.return_value = contacts
        # Test case 1: Search with query "Doe"
        result  = await search_contacts(db=self.session, query = "Doe", user=self.user)
        # self.assertEqual([contact.last_name for contact in result], ["Doe"])
        self.assertEqual(result, [contacts[0], contacts[2]])        
        # Test case 2: Search with query "Jane"
        result  = await search_contacts(db=self.session, query = "Jane", user=self.user)
        self.assertEqual(result, [contacts[2]])
        # Test case 3: Search with query "jakesmith@example.com"
        result  = await search_contacts(db=self.session, query = "jakesmith@example.com", user=self.user)
        self.assertEqual(result, [contacts[1]])
        # Test case 4: Search with query "anna"
        result  = await search_contacts(db=self.session, query = "anna", user=self.user)
        self.assertEqual(result, [])



if __name__ == '__main__':
    unittest.main()

