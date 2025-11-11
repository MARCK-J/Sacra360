
"""Tests para endpoints de Parroquias (/api/v1/parishes/)
"""

import pytest


def test_list_parishes_empty(client):
    """Listado inicialmente vacío"""
    response = client.get("/api/v1/parishes/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_parish(client):
    """Crear parroquia y obtenerla por id"""
    parish_data = {
        "name": "Parroquia de Prueba",
        "address": "Calle de Prueba 123",
        "priest_name": "Padre Prueba"
    }

    # Crear
    response = client.post("/api/v1/parishes/", json=parish_data)
    assert response.status_code in (200, 201)
    created = response.json()
    assert created["name"] == parish_data["name"]
    assert "id" in created

    parish_id = created["id"]

    # Obtener por id
    response = client.get(f"/api/v1/parishes/{parish_id}")
    assert response.status_code == 200
    got = response.json()
    assert got["id"] == parish_id
    assert got["name"] == parish_data["name"]


def test_update_and_delete_parish(client):
    """Actualizar y eliminar una parroquia"""
    parish_data = {
        "name": "Parroquia Update",
        "address": "Dirección",
        "priest_name": "Padre Uno"
    }
    response = client.post("/api/v1/parishes/", json=parish_data)
    assert response.status_code in (200, 201)
    created = response.json()
    parish_id = created["id"]

    # Update
    update = {"name": "Parroquia Actualizada", "address": "Nueva dirección", "priest_name": "Padre Dos"}
    response = client.put(f"/api/v1/parishes/{parish_id}", json=update)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Parroquia Actualizada"

    # Delete
    response = client.delete(f"/api/v1/parishes/{parish_id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert data.get("id") == parish_id
