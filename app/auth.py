from typing import Dict
from uuid import uuid4

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserStore:
    def __init__(self):
        self._users: Dict[str, str] = {}

    def create_user(self, email: str, password: str):
        if email in self._users:
            raise ValueError("user exists")
        self._users[email] = pwd_context.hash(password)

    def verify_user(self, email: str, password: str) -> bool:
        hashed = self._users.get(email)
        if not hashed:
            return False
        return pwd_context.verify(password, hashed)


class TokenStore:
    def __init__(self):
        self._tokens: Dict[str, str] = {}

    def issue(self, email: str) -> str:
        token = uuid4().hex
        self._tokens[token] = email
        return token

    def get_email(self, token: str) -> str | None:
        return self._tokens.get(token)


user_store = UserStore()
token_store = TokenStore()
