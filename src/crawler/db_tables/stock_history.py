from lib.db_var import db
from sqlalchemy import Column, String, Date, Integer, Float, ForeignKey
from db_tables.stock import StockInfo
class StockHistory(db.Model):
    __tablename__    = 'stock_history'
    stock_code       = Column('stock_code',    String(10), ForeignKey(StockInfo.stock_code), primary_key=True)
    open             = Column('open',          Float, comment='開盤')
    high             = Column('high',          Float, comment='最高')
    low              = Column('low',           Float, comment='最低')
    close            = Column('close',         Float, comment='收盤')
    fluctuation      = Column('fluctuation',   Float, comment='漲跌')
    fluctuation_p    = Column('fluctuation_p', Float, comment='漲跌（%）')
    trade_count      = Column('trade_count',   Integer, comment='成交張數')
    date             = Column('date',          Date, primary_key=True)

    def __init__(self, stock_code, trade_count, open, close, high, low, fluctuation, fluctuation_p, date):
        self.stock_code = stock_code
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.fluctuation = fluctuation
        self.fluctuation_p = fluctuation_p
        self.trade_count = trade_count
        self.date = date

db.create_all()
db.session.commit()