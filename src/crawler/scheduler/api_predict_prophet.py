import json, traceback, sys, requests, math, time, threading, gc
sys.path.append('/app/')
from shutil import move
from datetime import datetime, timedelta
from sqlalchemy import desc
from lib.var import stock_api_prophet_url
from lib.db_var import db
from dateutil.relativedelta import relativedelta
from db_tables.stock         import StockInfo
from db_tables.stock_history import StockHistory
from db_tables.predicted_result import PredictedResult

def write_predicted_dict(input_obj, fp2write):
    tmp_filepath = './tmp.json'
    f = open(tmp_filepath, 'w')
    f.write(json.dumps(input_obj, ensure_ascii=False, indent=4))
    f.close()
    move(tmp_filepath, fp2write)

class MultiThread():
    def __init__(self, target_func, thread_limit=5):
        self.target_func = target_func
        self.thread_limit = thread_limit
        self.result = []
        self.thread_list = []

    def thread_controller(self):
        while [x.is_alive() for x in self.thread_list].count(True)>self.thread_limit:
            continue
        index_list = []
        for thread_index, thread in enumerate(self.thread_list):
            if not thread.is_alive():
                index_list.append(thread_index)
        index_list.reverse()
        for index in index_list:
            del(self.thread_list[index])
        gc.collect()

    def exec_target_func(self, *args, **kwargs):
        self.result.append(self.target_func(*args, **kwargs))

    def exec(self, *args, **kwargs):
        self.thread_controller()
        thrad = threading.Thread(target=self.exec_target_func, args=(*args, ), kwargs=kwargs, daemon=True)
        thrad.start()
        self.thread_list.append(thrad)

    def clear_result(self):
        del(self.result)
        gc.collect()
        self.result = []

    def get_result(self):
        for thread in self.thread_list:
            thread.join()
        return self.result
    
def save2pr(mt_class):
    rsp_list = mt_class.get_result()
    for rsp in rsp_list:
        try:
            dictionary = rsp.json()
        except:
            print(traceback.format_exc())
            continue
        db.session.add(PredictedResult(**dictionary))
    db.session.commit()
    mt_class.clear_result()

def main(days=3, training_years=5, training_months=0):

    PredictedResult.query.filter(
        PredictedResult.predicted_date <= datetime.now()
    ).delete()
    db.session.commit()

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = math.ceil(time.time())
    print(f"start_time: {start_time}")

    for chn_name, category in {'上市': 'tse', '上櫃': 'otc'}.items():
        mt = MultiThread(target_func=requests.post)

        si_db_result_list = StockInfo.query.with_entities(
                                    StockInfo.stock_code,
                                    StockInfo.cmpy_name_s
                                    ).filter(
                                        StockInfo.category == category,
                                        StockInfo.exist == True,
                                        # StockInfo.stock_code == '3037'
                                        ).all()
        for si_db_index, si_db_result in enumerate(si_db_result_list):
            print(f"Notification: {chn_name}, {category}, {si_db_result.stock_code}, {si_db_index}/{len(si_db_result_list)}")

            sh_db_result = StockHistory.query.with_entities(
                StockHistory.date
                ).filter(
                    StockHistory.stock_code == si_db_result.stock_code,
                    StockHistory.date > (datetime.now()-relativedelta(years=training_years))
                ).order_by(desc(StockHistory.date)).first()
            if not sh_db_result:
                continue
            elif sh_db_result.date<(datetime.now()-timedelta(days=7)).date():
                continue

            PredictedResult.query.filter(
                PredictedResult.stock_code == si_db_result.stock_code,
                PredictedResult.date < sh_db_result.date,
            ).delete()

            pr_db_result = PredictedResult.query.filter(
                PredictedResult.stock_code == si_db_result.stock_code,
                PredictedResult.date == sh_db_result.date,
            ).first()
            if pr_db_result:
                continue

            req_json = {
                "stock_code": si_db_result.stock_code,
                "days": 3,
                "png_fp": f"/tmp/{si_db_result.stock_code}_{si_db_result.cmpy_name_s}.png",
                "training_years": training_years,
                "training_months": training_months,
            }
            # rsp = requests.post(stock_api_prophet_url, json=req_json)
            # rsp.close()
            # rsp_result = rsp.json()
            mt.exec(**{'url': stock_api_prophet_url, 'json': req_json})
            if si_db_index and si_db_index%mt.thread_limit == 0:
                save2pr(mt)
        save2pr(mt)

        # data_dict = {}
        # for pr_db_result in PredictedResult.query.all():
        #     dictionary = pr_db_result.json()
        #     if dictionary['predicted_date'] not in data_dict:
        #         data_dict[dictionary['predicted_date']] = []
        #     data_dict[dictionary['predicted_date']].append(dictionary)
        # for predicted_date_str in data_dict.keys():
        #     data_dict[predicted_date_str] = sorted(data_dict[predicted_date_str], key=lambda k: k['fluctuation_percent'])

        # if not os.path.exists(out_put_dir_json):
        #     os.makedirs(out_put_dir_json)
        # write_predicted_dict(data_dict, f"{out_put_dir_json}{chn_name}_1.json")
        # for predicted_date_str in data_dict.keys():
        #     data_dict[predicted_date_str].reverse()
        # write_predicted_dict(data_dict, f"{out_put_dir_json}{chn_name}_2.json")

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timelapse = math.ceil(time.time())-start_timestamp
    print(f"start_time: {start_time}, end_time: {end_time}, timelapse: {timelapse}")

if __name__ == '__main__':
    main()