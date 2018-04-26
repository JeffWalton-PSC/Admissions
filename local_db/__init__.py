import os


# local connection information
def connection():
    from sqlalchemy import create_engine

    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')
    db_host = os.environ.get('DB_HOST')
    db_database = os.environ.get('DB_DATABASE')
    db_driver = os.environ.get('DB_DRIVER')
    engine = create_engine(f'mssql+pyodbc://{db_user}:{db_pass}' +
                           f'@{db_host}/{db_database}?' +
                           f'driver={db_driver}')
    return engine.connect()

def print_connection_variables():
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')
    db_host = os.environ.get('DB_HOST')
    db_database = os.environ.get('DB_DATABASE')
    db_driver = os.environ.get('DB_DRIVER')

    print(db_user)
    print(db_pass)
    print(db_host)
    print(db_database)
    print(db_driver)
