import pytest
from unittest.mock import patch, MagicMock
from utils.swagger import create_app, custom_openapi

def test_create_app_returns_fastapi_instance():
    app = create_app()
    from fastapi import FastAPI
    assert isinstance(app, FastAPI)
    assert callable(app.openapi)
    schema = app.openapi()
    assert "components" in schema
    assert "securitySchemes" in schema["components"]
    assert "jwt" in schema["components"]["securitySchemes"]
    jwt_scheme = schema["components"]["securitySchemes"]["jwt"]
    assert jwt_scheme["type"] == "apiKey"
    assert jwt_scheme["in"] == "header"
    assert jwt_scheme["name"] == "Authorization"

def test_custom_openapi_returns_existing_schema_if_present():
    app = MagicMock()
    app.openapi_schema = {"existing": True}
    result = custom_openapi(app)
    assert result == {"existing": True}
    app.openapi_schema = None

@patch("utils.swagger.get_openapi")
def test_custom_openapi_creates_schema_when_none(mock_get_openapi):
    app = MagicMock()
    app.openapi_schema = None
    mock_get_openapi.return_value = {"routes": []}
    
    result = custom_openapi(app)
    
    mock_get_openapi.assert_called_once_with(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    assert "components" in result
    assert "securitySchemes" in result["components"]
    assert "jwt" in result["components"]["securitySchemes"]
    assert app.openapi_schema == result

def test_custom_openapi_components_exist_but_security_schemes_missing():
    app = MagicMock()
    app.openapi_schema = None
    mock_schema = {"components": {}}
    with patch("utils.swagger.get_openapi", return_value=mock_schema):
        result = custom_openapi(app)
        assert "components" in result
        assert "securitySchemes" in result["components"]
        assert "jwt" in result["components"]["securitySchemes"]

def test_custom_openapi_components_and_security_exist():
    app = MagicMock()
    app.openapi_schema = None
    mock_schema = {
        "components": {
            "securitySchemes": {"existing": {"type": "http"}}
        }
    }
    with patch("utils.swagger.get_openapi", return_value=mock_schema):
        result = custom_openapi(app)
        assert "existing" in result["components"]["securitySchemes"]
        assert "jwt" in result["components"]["securitySchemes"]
