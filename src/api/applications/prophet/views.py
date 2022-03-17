import os
from datetime import datetime
from flask.views import MethodView
from flask import jsonify, request, send_file
from sqlalchemy import asc, desc
from lib.db_var import db
from lib.predict.predict_prophet import predict_a_stock
from models.stock import StockInfo
from models.predicted_result import PredictedResult

class PredictResultAPI(MethodView):
    def __init__(self):
        self.api_result = {}
        self.purpose_dict = {
            "LIST_PREDICTED_RESULT": self.list_predicted_result,
            "GET_PREDICTED_RESULT": self.get_predicted_result,
            "CHECK_PICTURE": self.check_picture,
            "DOWNLOAD_PICTURE": self.download_picture,
        }
    
    def check_stock_exist(self):
        self.stock = request.args.get("stock")
        if not self.stock:
            self.api_result["status"] = False
            self.api_result["message"] = "Invalid stock (1)"
            return False
        self.db_result = db.session.query(StockInfo).filter(
            StockInfo.stock_code == self.stock,
        ).first()
        if not self.db_result:
            self.api_result["status"] = False
            self.api_result["message"] = "Stock data not found"
            return False
        return True

    def list_predicted_result(self):
        self.api_result["status"] = True
        self.api_result["result"] = [
            x.stock_code for x in db.session.query(PredictedResult).with_entities(PredictedResult.stock_code).all()
        ]
        return jsonify(self.api_result)

    def get_predicted_result(self):
        if not self.check_stock_exist():
            return jsonify(self.api_result), 400
        pr_db_result = db.session.query(PredictedResult).filter(
            PredictedResult.stock_code == self.stock
        ).first()
        if not pr_db_result:
            self.api_result["status"] = False
            self.api_result["message"] = "Predicted result not found"
            return jsonify(self.api_result), 400
        self.api_result["status"] = True
        self.api_result.update(
            pr_db_result.json()
        )
        return jsonify(self.api_result)

    def check_picture(self):
        if not self.check_stock_exist():
            return jsonify(self.api_result), 400
        file_path = f"/tmp/{self.stock}_{self.db_result.cmpy_name_s}.png"
        if os.path.exists(file_path):
            self.api_result["status"] = True
            return jsonify(self.api_result)
        self.api_result["status"] = False
        self.api_result["message"] = "Picture not found"
        return jsonify(self.api_result), 400

    def download_picture(self):
        if not self.check_stock_exist():
            return jsonify(self.api_result), 400
        file_path = f"/tmp/{self.stock}_{self.db_result.cmpy_name_s}.png"
        if os.path.exists(file_path):
            return send_file(file_path, attachment_filename=f"{self.stock}_{self.db_result.cmpy_name_s}.png")
        self.api_result["status"] = False
        self.api_result["message"] = "Picture not found"
        return jsonify(self.api_result), 400

    def get(self):
        purpose = request.args.get("purpose", "LIST_PREDICTED_RESULT")
        if purpose not in self.purpose_dict:
            self.api_result["status"] = False
            self.api_result["message"] = "Invalid purpose"
            return jsonify(self.api_result), 400
        return self.purpose_dict[purpose]()


class PredictProphet(MethodView):
    def __init__(self):
        self.predict_method = 'PROPHET'
        self.api_result = {}
        # app_config_dict['DIR_SETTINGS']['PROPHET']['PNG']
        # app_config_dict['DIR_SETTINGS']['PROPHET']['JSON']
        self.order_dict = {
            'asc': asc,
            'desc': desc
        }
        db.session.close()
    
    def bad_request(self, msg):
        self.api_result['status'] = False
        self.api_result['message'] = msg
        return jsonify(self.api_result), 400

    def get(self):
        si_db_result_list = StockInfo.query.with_entities(StockInfo.stock_code, StockInfo.category, StockInfo.cmpy_name_s).all()
        stock_cmpy_name_dict = {x.stock_code: x.cmpy_name_s for x in si_db_result_list}
        stock_category_dict = {x.stock_code: x.category for x in si_db_result_list}
        order = request.args.get('order', 'desc')

        pr_db_result_list = PredictedResult.query.all()
        dictionary_list = []
        for db_result in pr_db_result_list:
            dictionary = db_result.json()
            # if not dictionary['confidence_max'] < dictionary['price'] < dictionary['confidence_min']:
            #     continue
            dictionary['predicted_fluctuation_percent'] = round(((dictionary['predicted_price']/dictionary['price'])-1)*100, 3)
            dictionary['cmpy_name_s'] = stock_cmpy_name_dict[dictionary['stock_code']]
            dictionary['category'] = stock_category_dict[dictionary['stock_code']]
            if dictionary['predicted_date'] not in self.api_result:
                self.api_result[dictionary['predicted_date']] = []
            self.api_result[dictionary['predicted_date']].append(dictionary)
        
        for key in self.api_result.keys():
            self.api_result[key] = sorted(self.api_result[key], key=lambda k: k['predicted_fluctuation_percent'])
            if order == 'desc':
                self.api_result[key].reverse()

        # if order == 'desc':
        #     dictionary_list.reverse()
        # for db_result in PredictedResult.query.order_by(self.order_dict[order](PredictedResult.fluctuation_percent)).all():
        #     dictionary = db_result.json()
        #     dictionary['cmpy_name_s'] = stock_cmpy_name_dict[dictionary['stock_code']]
        #     dictionary['category'] = stock_category_dict[dictionary['stock_code']]
        #     if dictionary['predicted_date'] not in self.api_result:
        #         self.api_result[dictionary['predicted_date']] = []
        #     self.api_result[dictionary['predicted_date']].append(dictionary)
        return jsonify(self.api_result)

    def post(self):
        check_dict = {
            'stock_code': str,
            'days': int,
            'training_years': int,
            'training_months': int,
        }
        input_dict = {
            'dataframe':None,
            'training_years': 1,
            'training_months': 6,
        }
        for key, value in check_dict.items():
            if key not in request.json:
                return self.bad_request(f"No {key}.")
            elif not isinstance(request.json.get(key), value):
                return self.bad_request(f"{key} must be {value}.")
            input_dict[key] = request.json[key]
        db_result = db.session.query(StockInfo).filter(
            StockInfo.stock_code == input_dict["stock_code"],
        ).first()
        if not db_result:
            self.api_result["status"] = False
            self.api_result["message"] = "stock_code not found"
            return jsonify(self.api_result), 400
        input_dict["png_fp"] = f"/tmp/{db_result.stock_code}_{db_result.cmpy_name_s}.png"
        self.api_result["status"] = True
        self.api_result["result"] = predict_a_stock(**input_dict)
        # Prevent MySQL 2006, 2013
        db.session.commit()
        db.session.query(PredictedResult).filter(PredictedResult.stock_code == input_dict["stock_code"]).delete()
        db.session.add(PredictedResult(**self.api_result["result"]))
        db.session.commit()
        return jsonify(self.api_result)

predict_result_api = PredictResultAPI.as_view("PredictResultAPI")
prophet_view = PredictProphet.as_view('PredictProphet')