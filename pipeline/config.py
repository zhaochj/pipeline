USER_NAME = 'piplineuser'
PASSWORD = 'pipeline'
DB_IP = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'pipeline'
PARAMS = 'charset=utf8mb4'
URL = 'mysql+pymysql://{}:{}@{}:{}/{}?{}'.format(USER_NAME, PASSWORD, DB_IP, DB_PORT, DB_NAME, PARAMS)

DATABASE_DEBUG = True

# 数据库权限： grant all ON pipeline.* TO 'piplineuser'@'%' IDENTIFIED BY 'pipeline';




