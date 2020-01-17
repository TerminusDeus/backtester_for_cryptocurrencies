import psycopg2

conn = {}


def init():
    conn = psycopg2.connect(database='backtest', user='postgres', port=5432,
                            password='postgres', host='localhost')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS public.results ('
                   'id INTEGER NOT NULL PRIMARY KEY, '
                   'market varchar(255) NOT NULL, '
                   'tick_interval varchar(255) NOT NULL, '
                   'strategy varchar(255) NOT NULL, varchar(255) NOT NULL, '
                   'price numeric NOT NULL, '
                   'start_depo numeric NOT NULL, '
                   'final_depo numeric NOT NULL'
                   ');'
                   )
    conn.commit()
    cursor.close()
    conn.close()


def exec_sql(sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
