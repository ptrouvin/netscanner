import sys
import sqlite3
import Config
import logging

CONFIG=Config.Config('univoice_filters.config')

class DB:
    def __init__(self, dbname='univoice.db.sqlite3'):
        self.dbname=dbname
        self.conn = sqlite3.connect(self.dbname)

        self.create()

    def create(self):
        c=self.cursor()
        raise Exception('Not implemented')        
        self.commit()
        
    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def insert(self,data):
        c=self.cursor()
        raise Exception('Not implemented')        
            
    def fetch(self):
        c=self.cursor()
        raise Exception('Not implemented')        
        return c.fetchall()

    def close(self):
        self.conn.close()

class Stats(DB):
    def create(self):
        c=self.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS stats
            (
                date text DEFAULT CURRENT_DATE,
                destination text,
                n integer,
                PRIMARY KEY (date,destination)
            );
        """)
        self.commit()
        
    def insert(self,destination,n,date=None):
        c=self.cursor()
        if not date:
            c.execute("INSERT OR IGNORE INTO stats (destination,n) VALUES(?,?)", (destination,n))
            c.execute("UPDATE stats SET n=n+? WHERE destination=?", (n,destination))
        else:
            c.execute("INSERT OR IGNORE INTO stats (date,destination,n) VALUES(?,?,?)", (date, destination,n))
            c.execute("UPDATE stats SET n=n=+? WHERE date=? AND destination=?", (n,date,destination))
            
    def insertHash(self,hsh,date=None):
        for d in hsh.keys():
            self.insert(d,hsh[d],date=date)

    def fetch(self,date=None):
        c=self.cursor()
        if not date:
            c.execute("SELECT destination,n FROM stats WHERE date=date('now')")
        else:
            c.execute("SELECT destination,n FROM stats WHERE date='%s'" % (date))
        return c.fetchall()


if __name__ == '__main__':
    import argparse
    import json

    LOGGING_LEVELS = {'critical': logging.CRITICAL,
                 'error': logging.ERROR,
                 'warning': logging.WARNING,
                 'info': logging.INFO,
                 'debug': logging.DEBUG}
                  


    parser = argparse.ArgumentParser(description='univoice db sqlite3')
    parser.add_argument('--logging-level', default='info',
            help='Logging level '+','.join(LOGGING_LEVELS.keys()))
    parser.add_argument('-d', '--debug', action='count',
            help='Enable and increase debug level')
    

    args = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(args.logging_level, logging.NOTSET)
    logging.basicConfig(level=logging_level,
                      format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

    d=Stats()
    print json.dumps(d.fetch(),indent=1)

