from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    user_img:str
class Post(BaseModel):
    id:int
    title:str
    post_img:str
    user_id:int
    content:str
    style:str
    category:str
    keywords:List[str]
class subscriber(BaseModel):
    id:int
    email:str

class Poster(BaseModel):
    title:str
    post_img:str
    user_id:int
    content:str
    style:str
    category:str

class LoginForm(BaseModel):
    email: str
    password: str