"""
cd /app/ && \
python scheduler/download_opendata.py > /tmp/download_opendata.json

python scheduler/download_stock_history.py > /tmp/download_stock_history.json &
python scheduler/download_stock_buy_sell.py > /tmp/download_stock_buy_sell.json &
python scheduler/predict_prophet.py
"""
import os, json, traceback, sys
sys.path.append('/app/')
from uuid import uuid1
from shutil import move
from datetime import datetime
from lib.var import opendata_url, \
                    opendata_params_dict, \
                    opendata_folder_dir, \
                    prefix_dict
from lib.func_tools import check_duplicate_process, RequestsRetryer
from lib.db_var import db
from db_tables.stock         import StockInfo
from db_tables.stock_buy_sell import StockBuySell

for folder_dir in [opendata_folder_dir]:
    if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)

rr = RequestsRetryer()

class OpendataHandler():
    def __init__(self):
        self.checkfilename = 'check.json'
        self.checkfilepath = f"{opendata_folder_dir}{self.checkfilename}"

    def get_opendata_update_time(self):
        if not os.path.exists(self.checkfilepath):
            return None
        f = open(self.checkfilepath, 'r')
        content = json.loads(f.read())
        f.close()
        return datetime.strptime(content['opendata_update_time'], '%Y-%m-%d').date()

    def write_opendata_update_time(self, datetime_str=None):
        if not datetime_str:
            datetime_str = datetime.now().date().strftime('%Y-%m-%d')
        try:
            datetime.strptime(datetime_str, '%Y-%m-%d')
        except Exception as e:
            raise Exception(f"Input is not a datetime string: {datetime_str}, {e}")
        content = json.dumps(
            {
                'opendata_update_time':datetime_str
            },
            ensure_ascii=False,
            indent=4,
        )
        tmp_fp = f'/tmp/{uuid1()}.json'
        f = open(tmp_fp, 'w')
        f.write(content)
        f.close()
        move(tmp_fp, self.checkfilepath)
        
    def check_if_need2download(self):
        last_download_date = self.get_opendata_update_time()
        if last_download_date \
        and last_download_date==datetime.now().date():
            return False
        else:
            return True

    def exe(self):
        for opendata_name, params in opendata_params_dict.items():
            print(f"Notification: Start to download file: \"{opendata_name}\"")
            rsp = rr.requests_retryer('get', **{'url': opendata_url, 'params':params})
            rsp.close()
            rsp_result = rsp.json()
            content = json.dumps(rsp_result, ensure_ascii=False, indent=4)
            tmp_fp = f'/tmp/{uuid1()}.json'
            opendata_fp = f"{opendata_folder_dir}{opendata_name}.json"
            f = open(tmp_fp, 'w')
            f.write(content)
            f.close()
            move(tmp_fp, opendata_fp)
            category = prefix_dict[opendata_name]
            db_stock_code_set = {x.stock_code for x in StockInfo.query.with_entities(
                                                            StockInfo.stock_code,
                                                        ).filter(
                                                            StockInfo.category == category
                                                        ).all()
                                }
            for stock_info in rsp_result:
                if stock_info['公司代號'] in db_stock_code_set:
                    continue
                dictionary = {
                    'stock_code': stock_info['公司代號'],
                    'category': category,
                    'cmpy_name_s': stock_info['公司簡稱'],
                }
                adding = StockInfo(**dictionary)
                db.session.add(adding)
            db.session.commit()
            stock_code_list = {x['公司代號'] for x in rsp_result}

            for boolean_value, condition_set in {
                    True: (stock_code_list-db_stock_code_set), 
                    False: (db_stock_code_set-stock_code_list),
                    }.items():
                for stock_code in condition_set:
                    StockInfo.query.filter(
                        StockInfo.stock_code == stock_code,
                        StockInfo.category == category,
                        StockInfo.exist != boolean_value,
                        ).update({'exist': boolean_value})
                    StockBuySell.query.filter(
                        StockBuySell.stock_code == stock_code,
                        StockBuySell.in_sh != boolean_value,
                    ).update({'in_sh': boolean_value})
            db.session.commit()

        self.write_opendata_update_time()

    def download_opendata_and_import2db(self):
        if self.check_if_need2download():
            self.exe()

def main():
    oh = OpendataHandler()
    oh.download_opendata_and_import2db()

if __name__ == '__main__':
    script_name = os.path.basename(__file__)
    if check_duplicate_process(script_name):
        print(f'{script_name} :尚有相同的程式正在執行')
        exit()
    try:
        main()
        print("Download opendata finished.")
    except:
        print(traceback.format_exc())