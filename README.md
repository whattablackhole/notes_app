# notes_app
Used technologies:
fastapi
uvicorn
sqlalchemy
alembic
asyncpg
passlib
python-jose
python-dotenv
pydantic_settings
pydantic
PyJWT
psycopg2-binary
slowapi
aiohttp
aiogram
aiogram_middlewares


To run the application:
1. Clone repo
2. Install Docker
3. run "docker compose up --build"

4. Link to bot - https://t.me/notes_keeper_bot
5. API ip - http://localhost:8005

mini-swagger:

/users/register/
body = {username:str, password:str}

/users/token/
body = {username:str, password:str}

Authorized requests:
Prerequsite: add Bearer Token into Authorization header.

GET:
/notes/  - get all related notes to user
/notes/{id}  - get specific note by id

PUT:
/notes/{id} - update specifiy note by id
body = {Note}

DELETE:
/notes/{id}  - delete specific note by id

POST:
/notes/  - create a new note
body = {Note}

/notes/search/ - find all notes with specified tags
body = [{Tag}...] where Tag = {name:"value"}

screenshots of bot interface:
![Screenshot from 2024-09-15 22-03-57](https://github.com/user-attachments/assets/50bff5af-c61a-4df5-b5d7-25851713b376)
![Screenshot from 2024-09-15 22-06-36](https://github.com/user-attachments/assets/87e05d0d-81b5-42fc-b56b-d20c07b46f62)



