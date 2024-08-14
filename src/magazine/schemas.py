from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    username: str
    new_password: str 


class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    price: float
    renewal_date: datetime

class SubscriptionCreate(SubscriptionBase):
    id: int
    active: bool = True

    class Config:
        orm_mode = True

class SubscriptionUpdate(SubscriptionBase):
    active: bool = True

    class Config:
        orm_mode = True


class MagazineBase(BaseModel):
    title: str
    description: str
    price: float
    discount: float = 0.0

class MagazineCreate(MagazineBase):
    id: int

    class Config:
        orm_mode = True

class PlanBase(BaseModel):
    name: str
    description: str
    price: float
    duration: int  # in months

class PlanCreate(PlanBase):
    id: int

    class Config:
        orm_mode = True

class PlanUpdate(PlanBase):
    pass

    class Config:
        orm_mode = True

