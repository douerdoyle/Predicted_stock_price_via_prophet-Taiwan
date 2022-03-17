import os, json, traceback, threading, sys, time, math, gc
sys.path.append('/app/')
from shutil import move
from copy import deepcopy
from lib.stocker_prophet import Stocker
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import desc, func
from lib.db_var import db
from lib.load_data import load_stock2dataframe
from lib.var import result_folder_dir
from models.stock         import StockInfo
from models.stock_history import StockHistory
from models.predicted_result import PredictedResult

out_put_dir = f"{result_folder_dir}PROPHET/"
out_put_dir_png = f"{out_put_dir}PNG/"
out_put_dir_json = f"{out_put_dir}JSON/"

def write_predicted_dict(input_obj, fp2write):
    tmp_filepath = './tmp.json'
    f = open(tmp_filepath, 'w')
    f.write(json.dumps(input_obj, ensure_ascii=False, indent=4))
    f.close()
    move(tmp_filepath, fp2write)

def predict_a_stock(stock_code, png_fp, dataframe=None, training_years=1, training_months=6, days=2):
    print(f"Start to transfer {stock_code} data into dataframe.")
    if dataframe is None:
        dataframe = load_stock2dataframe(stock_code, training_years)
    # if dataframe['Date'].empty:
    #     return
    price = dataframe.squeeze()
    price.head()

    stocker_class = Stocker(stock_code, price, png_fp, training_years, training_months)
    _, future, predicted_date = stocker_class.create_prophet_model(days=days)

    predicted_price = float("{:.2f}".format(future.loc[future.index[-1], "yhat"]))
    confidence_min = round(list(future["yhat_lower"])[-1], 2)
    confidence_max = round(list(future["yhat_upper"])[-1], 2)
    ps_tmp_dict = {
        'stock_code': stock_code,
        'date': list(dataframe[dataframe['Date'] == max(dataframe['Date'])]['Date'])[0].strftime('%Y-%m-%d'),
        'price': list(dataframe[dataframe['Date'] == max(dataframe['Date'])]['Close'])[0],
        'predicted_date': predicted_date.strftime('%Y-%m-%d'),
        'predicted_price': predicted_price,
        'confidence_max': confidence_max,
        'confidence_min': confidence_min,
    }
    ps_tmp_dict['fluctuation'] = round(predicted_price-ps_tmp_dict['price'], 2)
    ps_tmp_dict['fluctuation_percent'] = round(predicted_price/ps_tmp_dict['price']-1, 5)
    del(stocker_class, future, dataframe)
    gc.collect()
    return ps_tmp_dict

def predict_all_stock(training_years=10, days=2):
    PredictedResult.query.filter(
        PredictedResult.predicted_date <= datetime.now()
    ).delete()
    db.session.commit()

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    start_timestamp = math.ceil(time.time())
    print(f"start_time: {start_time}")

    # mt = MultiThread(predict_a_stock)

    for chn_name, category in {'上市': 'tse', '上櫃': 'otc'}.items():
        si_db_result_list = StockInfo.query.with_entities(
                                    StockInfo.stock_code,
                                    StockInfo.cmpy_name_s
                                    ).filter(
                                        StockInfo.category == category,
                                        StockInfo.exist == True,
                                        # StockInfo.stock_code == '3037',
                                        # StockInfo.stock_code == '2888',
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

            if not os.path.exists(out_put_dir_png):
                os.makedirs(out_put_dir_png)
            png_fp = f"{out_put_dir_png}{si_db_result.stock_code}_{si_db_result.cmpy_name_s}.png"
            dictionary = predict_a_stock(si_db_result.stock_code, png_fp, dataframe=load_stock2dataframe(si_db_result.stock_code, training_years), training_years=training_years, training_months=6, days=days)
            db.session.add(PredictedResult(**dictionary))
            db.session.commit()

            # mt.exec(si_db_result.stock_code, png_fp, load_stock2dataframe(si_db_result.stock_code, training_years), training_years, days)
        # dictionary_list = sorted(mt.get_result(), key=lambda k: k['fluctuation_percent'])

        data_dict = {}
        for pr_db_result in PredictedResult.query.all():
            dictionary = pr_db_result.json()
            if dictionary['predicted_date'] not in data_dict:
                data_dict[dictionary['predicted_date']] = []
            data_dict[dictionary['predicted_date']].append(dictionary)
        for predicted_date_str in data_dict.keys():
            data_dict[predicted_date_str] = sorted(data_dict[predicted_date_str], key=lambda k: k['fluctuation_percent'])

        if not os.path.exists(out_put_dir_json):
            os.makedirs(out_put_dir_json)
        write_predicted_dict(data_dict, f"{out_put_dir_json}{chn_name}_1.json")
        for predicted_date_str in data_dict.keys():
            data_dict[predicted_date_str].reverse()
        write_predicted_dict(data_dict, f"{out_put_dir_json}{chn_name}_2.json")

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timelapse = math.ceil(time.time())-start_timestamp
    print(f"start_time: {start_time}, end_time: {end_time}, timelapse: {timelapse}")

class MultiThread():
    def __init__(self, target_func, thread_limit=10):
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

    def exec_target_func(self, *args):
        self.result.append(self.target_func(*args))

    def exec(self, *args):
        self.thread_controller()
        thrad = threading.Thread(target=self.exec_target_func, args=(*args, ), daemon=True)
        thrad.start()
        self.thread_list.append(thrad)

    def get_result(self):
        for thread in self.thread_list:
            thread.join()
        return self.result

if __name__ == '__main__':
    try:
        predict_all_stock()
    except:
        print(traceback.format_exc())
