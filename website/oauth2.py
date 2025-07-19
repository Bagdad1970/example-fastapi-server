from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_scoped_session
from asyncio import current_task

from authlib.authlib.integrations.fastapi_oauth2 import (
    AuthorizationServer,
    ResourceProtector,
)
from authlib.authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator
)
from authlib.authlib.oauth2.rfc6749 import grants
from authlib.authlib.oauth2.rfc7636 import CodeChallenge
from models import Users
from models import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
from database import AsyncSessionLocal

session = async_scoped_session(AsyncSessionLocal, scopefunc=current_task)


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post',
        'none',
    ]

    async def save_authorization_code(self, code, request) -> OAuth2AuthorizationCode:
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        session.add(auth_code)
        await session.commit()
        return auth_code

    async def query_authorization_code(self, code, client):
        auth_code = await session.scalar(select(OAuth2AuthorizationCode).where(OAuth2AuthorizationCode.code == code,
                                                                                OAuth2AuthorizationCode.client_id == client.client_id))
        if auth_code and not auth_code.is_expired():
            return auth_code

    async def delete_authorization_code(self, authorization_code: OAuth2AuthorizationCode):
        await session.delete(authorization_code)
        await session.commit()

    async def authenticate_user(self, authorization_code):
        return session.get(Users, authorization_code.user_id)


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    async def authenticate_user(self, username, password):
        user = await session.scalar(select(Users).where(Users.username == username))
        if user is not None and user.check_password(password):
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    async def authenticate_refresh_token(self, refresh_token):
        token = await session.scalar(select(OAuth2Token).where(OAuth2Token.refresh_token == refresh_token))
        if token and token.is_refresh_token_active():
            return token

    async def authenticate_user(self, credential):
        return Users.query.get(credential.user_id)

    async def revoke_old_credential(self, credential):
        credential.revoked = True
        session.add(credential)
        await session.commit()



query_client = create_query_client_func(session, OAuth2Client)
save_token = create_save_token_func(session, OAuth2Token)
authorization = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)
require_oauth = ResourceProtector()


def config_oauth(app, settings):
    authorization.init_app(settings)

    # support all grants
    authorization.register_grant(grants.ImplicitGrant)
    authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(AuthorizationCodeGrant, [CodeChallenge(required=True)])
    authorization.register_grant(PasswordGrant)
    authorization.register_grant(RefreshTokenGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())