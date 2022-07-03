from pickle import NONE
import psycopg2

class postgres():
    def connect(self,host,database,user,password):
        try:
            self.conn=psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password)
            
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            raise
            
        else:
            self.cursor=self.conn.cursor()
    def execute(self,sql,bindvars=None,commit=False):
        try:
            self.cursor.execute(sql,bindvars)
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            raise
            
        else:
            if commit:
                self.conn.commit()
            
                
class User():
    def add_user(self,db,params):
        sql='''insert into users (username,usertype_id,email,password,name,phone,created_at,modified_at,is_deleted)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        bindvars=[params[0],params[1],params[2],params[3],params[4],params[5],params[6],params[7],params[8]]
        db.execute(sql,bindvars,True)
    def get_users(self,db):
        sql='select * from users where is_deleted=False'
        db.execute(sql)
        result=db.cursor.fetchall()
        return result
    def get_user_by_username(self,db,username):
        user=None
        sql='''select * from users where username = %s AND is_deleted = %s'''
        bindvars=[username,False]
        db.execute(sql,bindvars)
        result=db.cursor.fetchall()
        if result:
            user=result[0]
        return user
        
        
class Model1():
    def get_classification_id(self,db,hamada):
        sql='''select * from classification where classification = %s'''
        bindvars=[hamada]
        db.execute(sql,bindvars)
        result=db.cursor.fetchone()[0]
        return result
    def add_session(self,db,params):
        sql='''insert into session(user_id,classification_id,beef_file_name,created_at)
        values (%s,%s,%s,%s)'''
        bindvars=[params[0],params[1],params[2],params[3]]
        db.execute(sql,bindvars,True)
        