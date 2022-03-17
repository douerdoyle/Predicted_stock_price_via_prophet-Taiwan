from settings.environment       import app
from applications.prophet.views import prophet_view, predict_result_api

def hello():
    return 'OK'

app.add_url_rule('/', view_func=hello, methods=['GET'])

app.add_url_rule('/predict/prophet', view_func=prophet_view, methods=['GET', 'POST'])
app.add_url_rule('/predict_result/', view_func=predict_result_api, methods=['GET'])