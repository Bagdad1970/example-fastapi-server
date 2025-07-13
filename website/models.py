import time
from sqlalchemy.orm import mapped_column, relationship
from database import Base
from sqlalchemy import String, Integer, ForeignKey
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)


class Users(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(40), unique=True)

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def check_password(self, password: str):
        return password == 'valid'


class OAuth2Client(Base, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('Users')


class OAuth2AuthorizationCode(Base, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('Users')


class OAuth2Token(Base, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('Users')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()
