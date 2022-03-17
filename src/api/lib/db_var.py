import pymysql
pymysql.install_as_MySQLdb()
import os
from flask             import Flask
from flask_sqlalchemy  import SQLAlchemy

app  = Flask(__name__)

DB_SETTING = {
    'DB_TYPE': 'mysql',
    'ACCOUNT': os.environ.get('MYSQL_USER'),
    'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
    'HOST': 'database',
    'PORT': '3306',
    'DB_NAME': os.environ.get('MYSQL_DATABASES'),
    'CHARSET': 'utf8mb4',
}

app.config.update(
    SECRET_KEY='QRF7aY2Z51gDQ#EJoltjIXBYs8eC&l0c3Z*pOF7yWk@uf3Gi8SyK)toJwyXhryRN',
    SQLALCHEMY_DATABASE_URI='%(DB_TYPE)s://%(ACCOUNT)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(DB_NAME)s?charset=%(CHARSET)s' % DB_SETTING,
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SQLALCHEMY_RECORD_QUERIES = True,
    SQLALCHEMY_POOL_SIZE = 1024,
    SQLALCHEMY_POOL_TIMEOUT = 90,
    SQLALCHEMY_POOL_RECYCLE = 3,
    SQLALCHEMY_MAX_OVERFLOW = 1024
)
db   = SQLAlchemy(app)