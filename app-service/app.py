from datetime import timedelta
from fastapi import FastAPI
from pydantic import BaseModel

import security as sec

# To add security
from typing import Union
from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


class Input(BaseModel):
    text: str


app = FastAPI(title="Classification pipeline",
              description="A simple text classifier",
              version="1.0")


@app.post("/token", response_model=sec.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = sec.authenticate_user(sec.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=sec.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = sec.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=sec.User)
async def read_users_me(current_user: Annotated[sec.User, Depends(sec.get_current_active_user)]):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: Annotated[sec.User, Depends(sec.get_current_active_user)]):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get('/test-no-free', tags=["test"])
async def get_test(
        incoming_data: Input,
        current_user: Annotated[sec.User, Depends(sec.get_current_active_user)]
):
    texto = incoming_data.text

    return {"test": texto}


@app.get('/test-free', tags=["test"])
async def get_test(
        incoming_data: Input
):
    texto = incoming_data.text

    return {"test": texto}


