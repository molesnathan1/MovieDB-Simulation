import psycopg

class ResetDB:
    
    def __init__(self, db_username):
        connection = psycopg.connect("dbname='grp6admin' user='%s'" % (db_username))
        cur = connection.cursor()
        query = """
            DROP TABLE IF EXISTS Interface; 
            DROP TABLE IF EXISTS SurveyQuestionResponse; 
            DROP TABLE IF EXISTS SurveyQuestion; 
            DROP TABLE IF EXISTS SurveyInvite; 
            DROP TABLE IF EXISTS Survey; 
            DROP TABLE IF EXISTS ReviewCommentInvite; 
            DROP TABLE IF EXISTS ReviewComments; 
            DROP TABLE IF EXISTS Review; 
            DROP TABLE IF EXISTS Users; 
            DROP TABLE IF EXISTS Verifier;"""
        cur.execute(query)
        connection.commit()


