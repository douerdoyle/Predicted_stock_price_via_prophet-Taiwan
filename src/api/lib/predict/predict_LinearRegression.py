import os, traceback, sys
sys.path.append('/app/')
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sqlalchemy import asc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from lib.var import prefix_dict
from models.stock          import StockInfo
from models.stock_buy_sell import StockBuySell
from models.stock_history import StockHistory
from lib.stocker_prophet import Stocker

def main(training_years=1, days=2):
    for category in prefix_dict.values():
        stock_code_list = [x.stock_code for x in StockInfo.query.with_entities(
                                    StockInfo.stock_code).filter(
                                    StockInfo.category == category,
                                    StockInfo.exist == True,
                                ).all()]
        for stock_code_index, stock_code in enumerate(stock_code_list):
            stock_code = '3037'
            print(f"Notification: {stock_code}, {stock_code_index}/{len(stock_code_list)}")
            start_date = (datetime.now()-relativedelta(years=training_years)).date()
            sh_date_fluctuation_p_dict = {x.date: {'close': x.close, 'fluctuation_p': x.fluctuation_p} for x in StockHistory.query.with_entities(
                        StockHistory.close,
                        StockHistory.fluctuation_p,
                        StockHistory.date
                    ).filter(
                        StockHistory.stock_code == stock_code,
                        StockHistory.fluctuation_p != None,
                        StockHistory.date >= start_date,
                    ).all()}

            x_list = []
            y_list = []
            for sbs_db_result in StockBuySell.query.filter(
                StockBuySell.stock_code == stock_code,
                StockBuySell.date >= start_date,
                ).order_by(
                    asc(StockBuySell.date
                    )
                ).all():
                if sbs_db_result.date not in sh_date_fluctuation_p_dict:
                    continue
                x_list.append(
                    [
                        # datetime.timestamp(datetime.strptime(sbs_db_result.date.strftime("%Y-%m-%d"), '%Y-%m-%d')),
                        sbs_db_result.dealerBuySell,
                        sbs_db_result.domesticBuySell,
                        sbs_db_result.foreignBuySell,
                        sbs_db_result.totalBuySell
                    ]
                )
                y_list.append(sh_date_fluctuation_p_dict[sbs_db_result.date]['fluctuation_p'])

            print(x_list[-1])
            print(len(x_list))
            print(y_list[-1])
            print(len(y_list))

            reg = LinearRegression().fit(x_list, y_list)
            print(f"score: {reg.score(x_list, y_list)}")
            print(f"coef_: {reg.coef_}")
            print(f"singular_: {reg.singular_}")
            print(f"rank_: {reg.rank_}")
            print(f"intercept_: {reg.intercept_}")
            input_list = x_list[-1]+reg.coef_
            print('-'*20)
            print(x_list[-1])
            print(input_list)
            print(reg.predict(input_list))
            return

            df_dcit = {
                'Date':[],
                'Close':[]
            }
            for sbs_db_result in StockBuySell.query.with_entities(
                StockBuySell.date, 
                StockBuySell.totalBuySell
                ).filter(
                StockBuySell.stock_code == stock_code,
                StockBuySell.date >= (datetime.now()-relativedelta(years=training_years))
                ).order_by(asc(StockBuySell.date)).all():
                df_dcit['Date'].append(sbs_db_result.date)
                df_dcit['Close'].append(sbs_db_result.totalBuySell)
            dataframe = pd.DataFrame.from_dict(df_dcit)
            dataframe.set_index('Date')
            print(dataframe.squeeze())
            if dataframe['Date'].empty:
                return {"status": False, "message": "No data."}

            stocker_class = Stocker(stock_code, dataframe.squeeze(), png_fp=None, training_years=training_years)
            _, future, predicted_date = stocker_class.create_prophet_model(days=days)
            predicted_price = float("{:.2f}".format(future.loc[future.index[-1], "yhat"]))
            confidence_min = round(list(future["yhat_lower"])[-1], 2)
            confidence_max = round(list(future["yhat_upper"])[-1], 2)

    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    reg = LinearRegression().fit(X, y)
    print(reg.score(X, y))
    print(reg.coef_)
    print(reg.intercept_)
    print(reg.predict(np.array([[3, 5]])))
    return

if __name__ == '__main__':
    try:
        print(main())
    except:
        print(traceback.format_exc())