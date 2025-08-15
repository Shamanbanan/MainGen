from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class SigninRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str


class TreeCreate(BaseModel):
    name: str


class TreeResponse(TreeCreate):
    id: int


class Gender(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class PersonCreate(BaseModel):
    first_name: str
    last_name: str
    gender: Gender = Gender.unknown
    birth_date: Optional[date] = None


class PersonResponse(PersonCreate):
    id: int
    tree_id: int


class RelationshipType(str, Enum):
    parent = "parent"
    spouse = "spouse"


class RelationshipCreate(BaseModel):
    person_a_id: int
    person_b_id: int
    type: RelationshipType


class RelationshipResponse(RelationshipCreate):
    id: int
    tree_id: int
