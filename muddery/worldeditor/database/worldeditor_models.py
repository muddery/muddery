
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import UniqueConstraint

Base = declarative_base()

KEY_LENGTH = 80
NAME_LENGTH = 80
VALUE_LENGTH = 80


# ------------------------------------------------------------
#
# world editor's accounts
#
# ------------------------------------------------------------
class accounts(Base):
    """
    User accounts.
    """
    __tablename__ = "accounts"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # account's username
    username = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # account's password
    password = Column(String(128), nullable=False)

    # password's salt
    salt = Column(String(128), nullable=False)

    # account's type
    type = Column(String(KEY_LENGTH), index=True, nullable=False)

    # account's create time
    create_time = Column(DateTime, nullable=True)

    # account's last login time
    last_login = Column(DateTime, nullable=True)

    # the last access token
    token = Column(String(256))
