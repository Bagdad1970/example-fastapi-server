import pytest

from sqlalchemy import select
from website.models import Users, OAuth2Client

pytestmark = pytest.mark.asyncio


async def test_create_user(test_client, db):
    response = await test_client.post("/home/", data={ "username": "user123"})

    user = await db.scalar(select(Users).where(Users.username == 'user123'))

    assert response.status_code == 307
    assert user.username == 'user123'


async def test_create_client_with_not_none_auth_method(test_client, db):
    response = await test_client.post("/home/create_client", data={"client_name": "user123",
                                                                   "client_uri": "https://authlib.org/",
                                                                   "grant_type": ["profile"],
                                                                   "redirect_uri": ["https://authlib.org/"],
                                                                   "response_type": "code",
                                                                   "scope": "profile",
                                                                   "token_endpoint_auth_method": "client_secret_basic"})

    oauth2_client = await db.scalar(select(OAuth2Client).where(OAuth2Client.client_metadata.get("client_name") == "user123"))    

    assert response.status_code == 307
    assert oauth2_client.client_metadata == {"client_name": "user123",
                                             "client_uri": "https://authlib.org",
                                             "grant_types": ["authorization_code","password"],
                                             "redirect_uris": ["https://authlib.org"],
                                             "response_types": ["code"],
                                             "scope": "profile",
                                             "token_endpoint_auth_method": "client_secret_basic"
    }

