import sys
sys.path.append('/app/')
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import desc
from models.stock_history import StockHistory

def load_stock2dataframe(stock_code, training_years):
    ls2d_tmp_dict = {
        'Date':[],
        'Open':[],
        'Close':[]
    }
    for sh_db_result in StockHistory.query.filter(
        StockHistory.stock_code == stock_code,
        StockHistory.date >= (datetime.now()-relativedelta(years=training_years))
        ).order_by(desc(StockHistory.date)).all():
        ls2d_tmp_dict['Date'].append(sh_db_result.date)
        ls2d_tmp_dict['Open'].append(sh_db_result.open)
        ls2d_tmp_dict['Close'].append(sh_db_result.close)
    dataframe = pd.DataFrame.from_dict(ls2d_tmp_dict)
    dataframe.set_index('Date')
    return dataframe