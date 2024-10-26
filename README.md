# Contacts API

Contacts API is a contact management application developed using FastAPI. The application allows you to create, view, edit and delete contacts, as well as search for them by partial matches of name, email or phone. Additionally, the API provides the ability to register a user with email confirmation and manage the user profile, including changing the avatar.

## Main functions

- **Create contact** — add a new contact with details.
- **View contact** — get data of one contact by its ID.
- **View contact list** — get all available contacts.
- **Search contacts** — search for a contact by name, email or phone number.
- **Edit contact** — update data of an existing contact.
- **Delete contact** — delete a contact from the database.
- **Sort by date of birth** — view contacts with the closest date of birth.
- **Register user** — create an account with sending a link for email confirmation.
- **User Profile** — profile management, including changing avatar.

## Technologies

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose

## Installation and Run

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) must be installed.

### Starting the Project

1. Clone the repository:

```bash
git clone https://github.com/YevgeniyPython/contacts_api_3
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate # For Linux/Mac
venv\Scripts\activate # For Windows
```
3. Install dependencies:

```
pip install -r requirements.txt
```  
or
```
poetry install
```


2. Set up environment variables in the .env file to connect to the PostgreSQL database and configure the SMTP server to send emails (an example .env.example is attached). 

3. Run containers using Docker Compose:
```
docker-compose up --build
```
This will get the FastAPI server and PostgreSQL container up and running.

4. Open the API documentation at http://localhost:8000/docs or http://localhost:8000/redoc to see the available endpoints.

### Usage
#### Main Endpoints
##### Contacts

- **POST api/contacts/** — create a new contact
- **GET api/contacts/{id}** — get details of a specific contact
- **GET api/contacts/** — list all contacts
- **GET api/contacts/contacts/search** — search contacts by name, email, or phone
- **PUT api/contacts/{id}** — update a contact
- **DELETE api/contacts/{id}** — delete a contact
- **GET api/contacts/contacts/birthdays** — get contacts with upcoming birthdays

##### Auth

- **POST api/auth/signup** — user registration with email confirmation link
- **POST /auth/login** — user login
- **GET api/auth/refresh_token** — refresh the access and refresh tokens using the provided refresh token.
- **GET api/auth/confirmed-email/{token}** — confirm the user's email address using the confirmation token.

##### Users

- **GET api/users/me** — retrieve the details of the currently authenticated user.
- **PATCH api/users/avatar** — Update the avatar of the currently authenticated user by uploading a new image to Cloudinary.


### Example .env File
Create a .env file in the root project folder and configure it as follows:
```dotenv
DATABASE_URL=postgresql://user:password@db/contacts_db
SECRET_KEY=your_secret_key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASS=your_email_password
```

### Documentation

To view detailed documentation, open the file docs/_build/html/index.html in your browser.

### Testing
FastAPI provides built-in testing tools using pytest. To run tests, use the command:
```
pytest
```

### Author
This project was developed by Yevgeniy Shevchenko itpython2023@gmail.com.

### License
This project is licensed under the MIT License. See the LICENSE file for more details.




