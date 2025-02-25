from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from auto_haven.authentication import AuthenticationHandler
from auto_haven.models.user import CurrentUser, Login, User


router = APIRouter()
auth_handler = AuthenticationHandler()


@router.post("/register", response_description="User registered", status_code=201)
async def register(request: Request, new_user: Login = Body(...)) -> User:
    users = request.app.db["users"]
    # hash the password before inserting it into MongoDB
    new_user.password = auth_handler.get_password_hash(new_user.password)
    new_user = new_user.model_dump()
    # check if existing user or email conflicts
    if (
        existing_username := await users.find_one({"username": new_user["username"]})
        is not None
    ):
        raise HTTPException(
            status_code=409,
            detail=f"User with username {new_user['username']} already registered.",
        )
    new_user = await users.insert_one(new_user)
    created_user = await users.find_one({"_id": new_user.inserted_id})
    return created_user


@router.post("/login", response_description="User logged in", status_code=200)
async def login(request: Request, login_user: Login = Body(...)) -> User:
    users = request.app.db["users"]
    user = await users.find_one({"username": login_user.username})
    if (user is None) or (
        not auth_handler.verify_password(login_user.password, user["password"])
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )
    token = auth_handler.encode_auth_token(str(user["_id"]), user["username"])
    response = JSONResponse(content={"token": token, "username": user["username"]})
    return response


@router.get(
    "/me",
    response_model=CurrentUser,
    response_description="Logged in data",
    status_code=200,
)
async def me(
    request: Request,
    user_data=Depends(auth_handler.authentication_wrapper),
):
    print("User data from token:", user_data)
    users = request.app.db["users"]
    current_user = await users.find_one({"_id": ObjectId(user_data["user_id"])})
    return current_user
