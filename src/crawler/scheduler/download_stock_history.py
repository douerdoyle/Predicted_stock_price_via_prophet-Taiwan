import os, traceback, sys
sys.path.append('/app/')
from copy import deepcopy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from lib.var import headers, \
                    opendata_folder_dir, \
                    prefix_dict, \
                    cnyes_history_api_url, \
                    sh_params_template, \
                    key_mapping_dict
from lib.func_tools import check_duplicate_process, RequestsRetryer

from sqlalchemy import desc
from lib.db_var import db
from db_tables.stock         import StockInfo
from db_tables.stock_history import StockHistory

for folder_dir in [opendata_folder_dir]:
    if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)

rr = RequestsRetryer()

def download_data():
    for chn_name, category in prefix_dict.items():
        stock_code_list = [x.stock_code for x in StockInfo.query.with_entities(
                                    StockInfo.stock_code).filter(
                                    StockInfo.category == category,
                                    StockInfo.exist == True,
                                ).all()
                            ]
        for stock_code_index, stock_code in enumerate(stock_code_list):
            print(f"Notification: {chn_name}, {category}, {stock_code}, {stock_code_index}/{len(stock_code_list)}")
            db_result = StockHistory.query.filter(StockHistory.stock_code == stock_code).order_by(desc(StockHistory.date)).first()
            nd2c = db_result.date+timedelta(days=1) if db_result else (datetime.now()-relativedelta(years=10)).date()
            while nd2c.weekday()>=5:
                nd2c+=timedelta(days=1)
            if (datetime.now().hour>=14 and nd2c>datetime.now().date()) \
            or (datetime.now().hour<=13 and nd2c>=(datetime.now().date()-timedelta(days=1))):
                print(f"Notification: {category} stock code {stock_code} history data has been downloaded, skip it.")
                continue

            query_end_timestamp = int(datetime.timestamp(datetime.strptime(nd2c.strftime('%Y-%m-%d'), '%Y-%m-%d')))
            query_start_timestamp = int(datetime.timestamp(datetime.strptime((datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'), '%Y-%m-%d')))

            params = deepcopy(sh_params_template)
            params['symbol'] = f'TWS:{stock_code}:STOCK'
            params['from'] = query_start_timestamp
            params['to'] = query_end_timestamp
            rsp = rr.requests_retryer('get', **{'url':cnyes_history_api_url, 'headers':headers, 'params':params})
            rsp.close()
            if rsp.status_code!=200:
                raise Exception(f'{rsp.text}')
            rsp_result = rsp.json()
            if rsp_result['statusCode']==5031:
                print(rsp_result)
                stock_code_list.append(stock_code)
                continue
            elif rsp_result['statusCode']!=200:
                raise Exception(f'{rsp_result}')
            dictionary_list = []
            for index, _ in enumerate(rsp_result['data']['c']):
                dictionary = {new_key: rsp_result['data'][source_key][index]  for source_key, new_key in key_mapping_dict.items()}
                if None in dictionary.values():
                    from pprint import pprint
                    pprint(dictionary)
                dictionary['date'] = datetime.fromtimestamp(dictionary['date']).date()
                dictionary['trade_count'] = int(round(dictionary['trade_count'], 0))
                dictionary['stock_code'] = stock_code
                dictionary['fluctuation'] = round(dictionary['close']-rsp_result['data']['c'][index+1], 2) if index<len(rsp_result['data']['c'])-1 else None
                dictionary['fluctuation_p'] = round((dictionary['close']/rsp_result['data']['c'][index+1]-1)*100, 2) if index<len(rsp_result['data']['c'])-1 else None
                # 1592 在 2021/06/15 後沒資料，拉區間為 2021/06/16 之後的資料會拉出 2021/06/15
                if dictionary['date']<nd2c:
                    continue
                dictionary_list.append(dictionary)
                index+=1
            for dictionary in dictionary_list:
                adding = StockHistory(**dictionary)
                db.session.add(adding)
            db.session.commit()

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    if check_duplicate_process(script_name):
        print(f'{script_name} :尚有相同的程式正在執行')
        exit()
    try:
        download_data()
        print("Download opendata finished.")
    except:
        print(traceback.format_exc())