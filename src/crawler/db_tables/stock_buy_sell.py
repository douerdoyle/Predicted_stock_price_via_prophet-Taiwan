from lib.db_var import db
from sqlalchemy import Column, String, Date, Integer

class StockBuySell(db.Model):
    __tablename__    = 'stock_buy_sell'
    stock_code       = Column('stock_code', String(10), primary_key=True)
    date             = Column('date',       Date, primary_key=True)
    dealerBuy        = Column('dealerBuy',  Integer, comment='自營商買入')
    dealerSell       = Column('dealerSell', Integer, comment='自營商賣出')
    dealerBuySell    = Column('dealerBuySell',   Integer, comment='自營商合計')
    domesticBuy      = Column('domesticBuy',     Integer, comment='投信買入')
    domesticSell     = Column('domesticSell',    Integer, comment='投信賣出')
    domesticBuySell  = Column('domesticBuySell', Integer, comment='投信合計')
    foreignBuy       = Column('foreignBuy',      Integer, comment='外資買入')
    foreignSell      = Column('foreignSell',     Integer, comment='外資賣出')
    foreignBuySell   = Column('foreignBuySell',  Integer, comment='外資合計')
    totalBuySell     = Column('totalBuySell',    Integer, comment='三大法人買賣合計')

    def __init__(self, stock_code, date, 
                 dealerBuy, dealerSell, dealerBuySell,
                 domesticBuy, domesticSell, domesticBuySell,
                 foreignBuy, foreignSell, foreignBuySell,
                 totalBuySell):
        self.stock_code = stock_code
        self.date = date
        self.dealerBuy = dealerBuy
        self.dealerSell = dealerSell
        self.dealerBuySell = dealerBuySell
        self.domesticBuy = domesticBuy
        self.domesticSell = domesticSell
        self.domesticBuySell = domesticBuySell
        self.foreignBuy = foreignBuy
        self.foreignSell = foreignSell
        self.foreignBuySell = foreignBuySell
        self.totalBuySell = totalBuySell

db.create_all()
db.session.commit()