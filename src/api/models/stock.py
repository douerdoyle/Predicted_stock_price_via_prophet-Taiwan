from uuid import uuid1
from lib.db_var import db
from sqlalchemy import Column, String, DateTime, text, Boolean

class StockInfo(db.Model):
    __tablename__ = 'stock_info'
    stock_code    = Column('stock_code',  String(10), primary_key=True)
    cmpy_name_s   = Column('cmpy_name_s', String(20), primary_key=True)
    category      = Column('category',    String(5), nullable=False)
    created_at    = Column('created_at',  DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at    = Column('updated_at',  DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    exist         = Column('exist',       Boolean, unique=False, default=True, comment='是否還處於上市上櫃狀態')

    def __init__(self, stock_code, cmpy_name_s, category, exist=True):
        self.id          = f"{uuid1()}"
        self.stock_code  = stock_code
        self.cmpy_name_s = cmpy_name_s
        self.category    = category
        self.exist       = exist

db.create_all()
db.session.commit()
