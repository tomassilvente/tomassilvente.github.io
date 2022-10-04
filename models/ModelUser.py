from .entities.User import User

class ModelUser():
    @classmethod
    def login(self, db, user):
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT id, username, password 
                FROM user
                WHERE username = '{}' 
            """.format(user.username)
            cursor.execute(sql)
            data = cursor.fetchone()
            if data != None:
                return User(data[0], data[1], User.check_password(data[2],user.password))   
                
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """
                SELECT id, username
                FROM user
                WHERE id = '{}' 
            """.format(id)
            cursor.execute(sql)
            data = cursor.fetchone()
            if data != None:
               return  User(data[0], data[1], None)
            else:
                return None
        except Exception as ex:
            raise Exception(ex)