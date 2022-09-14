import psycopg

class CreateDB:

    def __init__(self, db_username):
        connection = psycopg.connect("dbname='grp6admin' user='%s'" % (db_username))
        cur = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS Users(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            username varchar(24), 
            user_type varchar(1));"""
        query += """
        CREATE TABLE IF NOT EXISTS Review(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            userID int, 
            engagement_score int, 
            excitement_score int, 
            production_score int, 
            explanation varchar(512), 
            movieID int, 
            timestamp varchar(30),  
            FOREIGN KEY (userID) REFERENCES Users (id));"""
        query += """
        CREATE TABLE IF NOT EXISTS ReviewComments(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            reviewID int, 
            commenterID int, 
            text varchar(128), 
            timestamp varchar(30), 
            FOREIGN KEY (reviewID) REFERENCES Review (id), 
            FOREIGN KEY (commenterID) REFERENCES Users (id));"""
        query += """
        CREATE TABLE IF NOT EXISTS ReviewCommentInvite(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            reviewID int, 
            inviteeID int, 
            message varchar(128), 
            timestamp varchar(30), 
            FOREIGN KEY (reviewID) REFERENCES Review (id), 
            FOREIGN KEY (inviteeID) REFERENCES Users (id));"""
        query += """
        CREATE TABLE IF NOT EXISTS Survey(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            creatorID int, 
            timestamp varchar(30), 
            FOREIGN KEY (creatorID) REFERENCES Users (id));"""
        query += """
        CREATE TABLE IF NOT EXISTS SurveyInvite(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            surveyID int, 
            inviteeID int, 
            message varchar(128), 
            timestamp varchar(30), 
            FOREIGN KEY (surveyID) REFERENCES Survey (id), 
            FOREIGN KEY (inviteeID) REFERENCES Users (id));"""
        query += """
        CREATE TABLE IF NOT EXISTS SurveyQuestion(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            surveyID int, 
            qtext varchar(128), 
            option1 varchar(128), 
            option2 varchar(128), 
            FOREIGN KEY (surveyID) REFERENCES Survey (id));"""
        query += """
        CREATE TABLE IF NOT EXISTS SurveyQuestionResponse(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            questionID int, 
            choice boolean, 
            surveyID int, 
            timestamp varchar(30));"""
        query += """
        CREATE TABLE IF NOT EXISTS Interface(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
            movieID int,
            engagement_score REAL, 
            excitement_score REAL, 
            production_score REAL, 
            num_reviews varchar(128));"""
        query += """
        CREATE TABLE IF NOT EXISTS Verifier(
            ID int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            type varchar(16),
            timestamp varchar(30));"""
        query += """
        CREATE TABLE IF NOT EXISTS Movies(
            id int,
            name varchar(128),
            year int,
            rating decimal(3, 1));"""

        cur.execute(query)
        connection.commit()
