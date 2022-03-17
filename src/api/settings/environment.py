import pymysql
pymysql.install_as_MySQLdb()
import os
from flask             import Flask
from flask_sqlalchemy  import SQLAlchemy

app  = Flask(__name__)

app_config_dict = {
    'SECRET_KEY': 'QRF7aY2Z51gDQ#EJoltjIXBYs8eC&l0c3Z*pOF7yWk@uf3Gi8SyK)toJwyXhryRN',
    'DB_SETTING': {
        'DB_TYPE': 'mysql',
        'ACCOUNT': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': 'database',
        'PORT': 3306,
        'DB_NAME': os.environ.get('MYSQL_DATABASES'),
        'CHARSET': 'utf8mb4',
    },
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_RECORD_QUERIES': True,
    'SQLALCHEMY_POOL_SIZE': 1024,
    'SQLALCHEMY_POOL_TIMEOUT': 90,
    'SQLALCHEMY_POOL_RECYCLE': 3,
    'SQLALCHEMY_MAX_OVERFLOW': 1024,
    'RUN_SETTINGS': {'ip': '0.0.0.0', 'port': '80'},
    'DIR_SETTINGS': {
        'GLOBAL_DIR': '/app/result/'
    },
}
KEY = 'PROPHET'
app_config_dict['DIR_SETTINGS'][KEY] = {
    'DIR': f"{app_config_dict['DIR_SETTINGS']['GLOBAL_DIR']}{KEY}/",
}
app_config_dict['DIR_SETTINGS'][KEY]['PNG'] = f"{app_config_dict['DIR_SETTINGS'][KEY]['DIR']}PNG/"
app_config_dict['DIR_SETTINGS'][KEY]['JSON'] = f"{app_config_dict['DIR_SETTINGS'][KEY]['DIR']}JSON/"

for path in app_config_dict['DIR_SETTINGS'][KEY].values():
    if not os.path.exists(path):
        os.makedirs(path)

app_config_dict['SQLALCHEMY_DATABASE_URI'] = '%(DB_TYPE)s://%(ACCOUNT)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(DB_NAME)s?charset=%(CHARSET)s' % app_config_dict['DB_SETTING']

app.config.update(**app_config_dict)
db   = SQLAlchemy(app)

@app.teardown_request
def teardown_request(exception):
    db.session.rollback()
    db.session.close()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET, PATCH, DELETE, PUT')
    db.session.rollback()
    db.session.close()
    return(response)