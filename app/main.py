from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pathlib

from .auth import token_store, user_store
from .schemas import (
    PersonCreate,
    PersonResponse,
    RelationshipCreate,
    RelationshipResponse,
    SigninRequest,
    SignupRequest,
    TokenResponse,
    TreeCreate,
    TreeResponse,
)

app = FastAPI(title="MainGen")

static_dir = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=FileResponse)
def read_index():
    return FileResponse(static_dir / "index.html")

# In-memory stores
class TreeStore:
    def __init__(self):
        self._trees = {}
        self._persons = {}
        self._relationships = {}
        self._tree_counter = 1
        self._person_counter = 1
        self._relationship_counter = 1

    def create_tree(self, owner_email: str, data: TreeCreate) -> TreeResponse:
        tree_id = self._tree_counter
        self._tree_counter += 1
        self._trees[tree_id] = {"id": tree_id, "name": data.name, "owner": owner_email}
        self._persons[tree_id] = {}
        self._relationships[tree_id] = {}
        return TreeResponse(id=tree_id, **data.model_dump())

    def get_tree(self, tree_id: int) -> TreeResponse | None:
        t = self._trees.get(tree_id)
        if not t:
            return None
        return TreeResponse(**t)

    def add_person(self, tree_id: int, person: PersonCreate) -> PersonResponse:
        if tree_id not in self._trees:
            raise ValueError("tree not found")
        pid = self._person_counter
        self._person_counter += 1
        data = person.model_dump()
        data.update({"id": pid, "tree_id": tree_id})
        self._persons[tree_id][pid] = data
        return PersonResponse(**data)

    def list_persons(self, tree_id: int):
        return [PersonResponse(**p) for p in self._persons.get(tree_id, {}).values()]

    def add_relationship(self, tree_id: int, rel: RelationshipCreate) -> RelationshipResponse:
        if tree_id not in self._trees:
            raise ValueError("tree not found")
        rid = self._relationship_counter
        self._relationship_counter += 1
        data = rel.model_dump()
        data.update({"id": rid, "tree_id": tree_id})
        self._relationships[tree_id][rid] = data
        return RelationshipResponse(**data)


store = TreeStore()


def get_current_email(token: str | None = Header(default=None)) -> str:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")
    email = token_store.get_email(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return email


@app.post("/auth/signup", response_model=TokenResponse)
def signup(payload: SignupRequest):
    try:
        user_store.create_user(payload.email, payload.password)
    except ValueError:
        raise HTTPException(status_code=400, detail="user exists")
    token = token_store.issue(payload.email)
    return TokenResponse(access_token=token)


@app.post("/auth/signin", response_model=TokenResponse)
def signin(payload: SigninRequest):
    if not user_store.verify_user(payload.email, payload.password):
        raise HTTPException(status_code=400, detail="invalid credentials")
    token = token_store.issue(payload.email)
    return TokenResponse(access_token=token)


@app.post("/trees", response_model=TreeResponse)
def create_tree(data: TreeCreate, email: str = Depends(get_current_email)):
    return store.create_tree(email, data)


@app.get("/trees/{tree_id}", response_model=TreeResponse)
def get_tree(tree_id: int, email: str = Depends(get_current_email)):
    tree = store.get_tree(tree_id)
    if not tree:
        raise HTTPException(status_code=404, detail="tree not found")
    return tree


@app.post("/trees/{tree_id}/persons", response_model=PersonResponse)
def add_person(tree_id: int, person: PersonCreate, email: str = Depends(get_current_email)):
    try:
        return store.add_person(tree_id, person)
    except ValueError:
        raise HTTPException(status_code=404, detail="tree not found")


@app.get("/trees/{tree_id}/persons", response_model=list[PersonResponse])
def list_persons(tree_id: int, email: str = Depends(get_current_email)):
    return store.list_persons(tree_id)


@app.post("/trees/{tree_id}/relationships", response_model=RelationshipResponse)
def add_relationship(tree_id: int, rel: RelationshipCreate, email: str = Depends(get_current_email)):
    try:
        return store.add_relationship(tree_id, rel)
    except ValueError:
        raise HTTPException(status_code=404, detail="tree not found")
