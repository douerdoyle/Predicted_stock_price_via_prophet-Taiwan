from uuid import uuid1
from sqlalchemy                  import Column, String, Text, DateTime, text
from settings.environment        import app, db

class Member(db.Model):
    __tablename__ = 'member'
    account       = Column('account',    String(50), primary_key=True, nullable=False)
    password      = Column('password',   Text)
    created_at    = Column('created_at', DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at    = Column('updated_at', DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    token         = Column('token',      Text)

    def __init__(self, account, password):
        self.account  = account
        self.password = password