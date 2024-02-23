# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import asyncio

# Define FastAPI instance
app = FastAPI()

# Database connection pool
pool = None

# Define model for your resource (e.g., a simple User model)
class User(BaseModel):
    id: int
    name: str
    email: str

# Connect to the PostgreSQL database
async def connect_to_db():
    global pool
    pool = await asyncpg.create_pool(
        user='your_username',
        password='your_password',
        database='your_database',
        host='your_host'
    )

# Create user
@app.post("/users/")
async def create_user(user: User):
    async with pool.acquire() as connection:
        query = "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id"
        user_id = await connection.fetchval(query, user.name, user.email)
        return {"id": user_id, **user.dict()}

# Get user by ID
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with pool.acquire() as connection:
        query = "SELECT * FROM users WHERE id = $1"
        user_row = await connection.fetchrow(query, user_id)
        if user_row:
            return user_row
        else:
            raise HTTPException(status_code=404, detail="User not found")

# Update user by ID
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    async with pool.acquire() as connection:
        query = "UPDATE users SET name = $1, email = $2 WHERE id = $3"
        await connection.execute(query, user.name, user.email, user_id)
        return {"id": user_id, **user.dict()}

# Delete user by ID
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    async with pool.acquire() as connection:
        query = "DELETE FROM users WHERE id = $1"
        await connection.execute(query, user_id)
        return {"message": "User deleted successfully"}


# Start the application and connect to the database
@app.on_event("startup")
async def startup_event():
    await connect_to_db()
