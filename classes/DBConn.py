import pymssql

class DBConn :
    __sql__ = ''
    __conn___ = None
    
    def __init__(self, srv, id, pw, port, db):
        self.srv = srv
        self.id = id
        self.pw = pw
        self.port = port
        self.db = db

    def __del__(self):
        self.close()

    def connect(self):
        if (self.__conn___ == None):
            self.__conn___ = pymssql.connect(server = self.srv, port = self.port, user = self.id, password = self.pw, database = self.db)
            
            if (self.__conn___._conn.connected == False):
                print("Database connection is fail.")
                self.close()
                return None

        return self.__conn___

    def close(self):
        if (self.__conn___ != None):
            self.__conn___.close()
            self.__conn___ = None

    def set_sql(self, sql):
        self.__sql__ = sql
    
    def get_sql(self):
        return self.__sql__

    def add_sql(self, sql):
        self.__sql__ += sql

    def execute(self):
        con = self.connect()
        
        if (con == None):
            print("Connection is None. connect please.")
        else:
            cursor = self.cursor()
            cursor.execute(self.get_sql())

    def cursor(self):
        con = self.connect()

        if (con == None):
            return None

        return con.cursor()

    def commit(self):
        con = self.connect()

        if (con != None):
            con.commit()

