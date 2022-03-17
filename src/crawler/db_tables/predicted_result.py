from datetime import datetime
from lib.db_var import db
from sqlalchemy import Column, String, Date, DateTime, text, Float

class PredictedResult(db.Model):
    __tablename__    = 'predicted_result'
    stock_code       = Column('stock_code',      String(10), primary_key=True)
    date             = Column('date',            Date, comment='該公司最新資料日期', primary_key=True)
    price            = Column('price',           Float, comment='該公司最新資料日期的股價')
    predicted_date   = Column('predicted_date',  Date, comment='模型預測的日期', primary_key=True)
    predicted_price  = Column('predicted_price', Float, comment='模型預測的股價')
    confidence_max   = Column('confidence_max',  Float, comment='模型預測股價信心最大值')
    confidence_min   = Column('confidence_min',  Float, comment='模型預測股價信心最小值')
    fluctuation      = Column('fluctuation',     Float, comment='模型預測股價漲跌幅')
    fluctuation_percent = Column('fluctuation_percent', Float, comment='模型預測股價漲跌幅百分比')
    created_at       = Column('created_at',      DateTime, server_default=text('CURRENT_TIMESTAMP'))

    def __init__(self, stock_code, date, price, predicted_date, predicted_price, confidence_max, confidence_min, fluctuation, fluctuation_percent):
        self.stock_code = stock_code
        self.date       = date
        self.price      = price
        self.predicted_date = predicted_date
        self.predicted_price = predicted_price
        self.confidence_max = confidence_max
        self.confidence_min = confidence_min
        self.fluctuation = fluctuation
        self.fluctuation_percent = fluctuation_percent
        self.created_at = datetime.now()
    
    def json(self):
        return {
            'stock_code': self.stock_code,
            'date': self.date.strftime('%Y-%m-%d'),
            'price': self.price,
            'predicted_date': self.predicted_date.strftime('%Y-%m-%d'),
            'predicted_price': self.predicted_price,
            'confidence_max': self.confidence_max,
            'confidence_min': self.confidence_min,
            'fluctuation_percent': self.fluctuation_percent,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

db.create_all()
db.session.commit()
