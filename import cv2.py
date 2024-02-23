from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from graphene import ObjectType, String, Schema
from bson import ObjectId
from starlette.graphql import GraphQLApp

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['mycollection']

# Define GraphQL schema
class Query(ObjectType):
    hello = String(name=String(default_value="stranger"))

    def resolve_hello(root, info, name):
        return f"Hello, {name}!"

# Create FastAPI instance
app = FastAPI()

# Define GraphQL schema
schema = Schema(query=Query)

# Mount GraphQL app
app.add_route("/", GraphQLApp(schema=schema))

# Define endpoint to create user
@app.post("/users/")
async def create_user(name: str, email: str):
    user_data = {"name": name, "email": email}
    result = collection.insert_one(user_data)
    return {"id": str(result.inserted_id), **user_data}

# Define endpoint to get user by ID
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user_data = collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return user_data
    else:
        raise HTTPException(status_code=404, detail="User not found")
