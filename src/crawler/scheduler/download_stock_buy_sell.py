import os, sys, time, requests, traceback
sys.path.append('/app/')
from pprint import pprint
from copy import deepcopy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import desc
from lib.var import prefix_dict, headers, cnyes_buysell_api_url
from lib.func_tools import freeze, RequestsRetryer, format_num_string, check_duplicate_process
from lib.db_var import db
from db_tables.stock import StockInfo
from db_tables.stock_buy_sell import StockBuySell

rr = RequestsRetryer()

def main():
    for chn_name, category in prefix_dict.items():
        stock_code_list = [x.stock_code for x in StockInfo.query.with_entities(
                                    StockInfo.stock_code).filter(
                                    StockInfo.category == category,
                                    StockInfo.exist == True,
                                ).all()
                            ]
        for stock_code_index, stock_code in enumerate(stock_code_list):
            print(f"Notification: {chn_name}, {category}, {stock_code}, {stock_code_index}/{len(stock_code_list)}")
            db_result = StockBuySell.query.filter(StockBuySell.stock_code == stock_code).order_by(desc(StockBuySell.date)).first()
            nd2c = db_result.date+timedelta(days=1) if db_result else (datetime.now()-relativedelta(years=10)).date()
            while nd2c.weekday()>=5:
                nd2c+=timedelta(days=1)
            if (datetime.now().hour>=15 and nd2c>datetime.now().date()) \
            or (datetime.now().hour<=14 and nd2c>=(datetime.now().date()-timedelta(days=1))):
                print(f"Notification: {category} stock code {stock_code} history data has been downloaded, skip it.")
                continue
            query_end_timestamp = int(datetime.timestamp(datetime.strptime(nd2c.strftime('%Y-%m-%d'), '%Y-%m-%d')))
            query_start_timestamp = int(datetime.timestamp(datetime.strptime((datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'), '%Y-%m-%d')))

            tmp_url = f"{cnyes_buysell_api_url}TWS:{stock_code}:STOCK"
            params = {
                'from': query_start_timestamp,
                'to': query_end_timestamp
            }

            rsp = rr.requests_retryer('get', **{'url':tmp_url, 'headers':headers, 'params':params})
            rsp.close()

            try:
                rsp_result = rsp.json()
            except:
                raise Exception(f'{rsp.text}')
            if rsp.status_code!=200:
                if rsp_result['error']=='Internal Server Error':
                    stock_code_list.append(stock_code)
                    continue
                raise Exception(f'{rsp.text}')
            rsp_result = rsp.json()

            dictionary_list = []
            for data in rsp_result['data']:
                dictionary = {
                    'stock_code': stock_code,
                    'date': datetime.strptime(data['date'], '%Y/%m/%d').date(),
                    'dealerBuy': data['dealerBuyVolume'],
                    'dealerSell': data['dealerSellVolume'],
                    'dealerBuySell': data['dealerNetBuySellVolume'],
                    'domesticBuy': data['domesticBuyVolume'],
                    'domesticSell': data['domesticSellVolume'],
                    'domesticBuySell': data['domesticNetBuySellVolume'],
                    'foreignBuy': data['foreignBuyVolume'],
                    'foreignSell': data['foreignSellVolume'],
                    'foreignBuySell': data['foreignNetBuySellVolume'],
                    'totalBuySell': data['totalNetBuySellVolume'],
                }
                if dictionary['date']<nd2c:
                    continue
                dictionary_list.append(dictionary)
            if not dictionary_list:
                continue
            for dictionary in dictionary_list:
                db.session.add(StockBuySell(**dictionary))
            db.session.commit()

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    if check_duplicate_process(script_name):
        print(f'{script_name} :尚有相同的程式正在執行')
        exit()
    try:
        main()
    except:
        print(traceback.format_exc())