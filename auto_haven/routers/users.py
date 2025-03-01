from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from auto_haven.authentication import AuthenticationHandler
from auto_haven.models.user import CurrentUser, Login, User, Register


router = APIRouter()
auth_handler = AuthenticationHandler()


@router.post(
    "/register",
    response_description="User registered",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
async def register(new_user: Register = Body(...)) -> User:
    new_user.password = auth_handler.get_password_hash(new_user.password)

    existing_user = await User.find_one(
        {"$or": [{"username": new_user.username}, {"email": new_user.email}]}
    )
    if existing_user:
        if existing_user.username == new_user.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{new_user.username}' is already registered.",
            )
        if existing_user.email == new_user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{new_user.email}' is already registered.",
            )
    # Create and save the new user
    user = User(**new_user.model_dump())
    await user.insert()

    return user


@router.post("/login", response_description="User logged in", status_code=200)
async def login(login_user: Login = Body(...)) -> JSONResponse:
    # Find the user by username
    user = await User.find_one(User.username == login_user.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Verify the password
    if not auth_handler.verify_password(login_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Generate an access token
    token = auth_handler.encode_auth_token(str(user.id), user.username)

    # Return the token and username in the response
    return JSONResponse(
        content={"token": token, "username": user.username},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/me",
    response_model=CurrentUser,
    response_description="Get the currently authenticated user's data",
    status_code=200,
)
async def get_current_user(
    user_data=Depends(auth_handler.authentication_wrapper),
):
    current_user = await User.get(user_data["user_id"])
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return current_user
