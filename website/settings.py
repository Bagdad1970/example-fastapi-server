from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    OAUTH2_SCOPES_SUPPORTED: list[str] = []
    OAUTH2_ERROR_URIS: list[str] = []
    OAUTH2_ACCESS_TOKEN_GENERATOR: bool = True
    OAUTH2_REFRESH_TOKEN_GENERATOR: bool = False
    OAUTH2_TOKEN_EXPIRES_IN: dict = {}
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = ""