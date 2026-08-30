# -*- coding: utf-8 -*-
import sys, os

user_site = os.path.expanduser("~/.local/lib/python3.12/site-packages")
if user_site not in sys.path:
    sys.path.insert(0, user_site)

sys.path.insert(0, os.path.dirname(__file__))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_full_lifecycle():
    # 1. Registro de Usuario
    res_reg = client.post("/auth/register", json={"email": "test@ccia.local", "password": "password123"})
    assert res_reg.status_code == 200
    assert res_reg.json()["email"] == "test@ccia.local"

    # 2. Login y obtención de Token
    res_login = client.post("/auth/login", data={"username": "test@ccia.local", "password": "password123"})
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Crear Item (POST)
    res_create = client.post("/items/", json={"title": "Tarea de Prueba", "description": "Probando suite de tests"}, headers=headers)
    assert res_create.status_code == 201
    item_id = res_create.json()["id"]

    # 4. Listar Items paginados (GET)
    res_list = client.get("/items/?skip=0&limit=5", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # 5. Obtener Item por ID (GET /{id})
    res_single = client.get(f"/items/{item_id}", headers=headers)
    assert res_single.status_code == 200
    assert res_single.json()["title"] == "Tarea de Prueba"

    # 6. Actualizar Item (PUT)
    res_update = client.put(f"/items/{item_id}", json={"completed": True}, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["completed"] is True

    # 7. Eliminar Item (DELETE)
    res_del = client.delete(f"/items/{item_id}", headers=headers)
    assert res_del.status_code == 204

    # 8. Verificar eliminación (GET 404)
    res_get = client.get(f"/items/{item_id}", headers=headers)
    assert res_get.status_code == 404
