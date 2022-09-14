import random
import time
import datetime
import psycopg
import string
from random import randrange
import Verifier



def getRandomMovie(cursor):
    # movieIDQuery = sendDBQuery(cursor, "SELECT id FROM Movies ORDER BY RANDOM() LIMIT 1")
    # movieID = movieIDQuery[0][0]
    # movieNameQuery = sendDBQuery(cursor, "SELECT name FROM Movies WHERE id = %s;" % (movieID))
    # movieName = movieNameQuery[0][0]

    sizeQ = sendDBQuery(cursor, "SELECT COUNT(*) FROM Movies;")
    size = sizeQ[0][0]
    movieNameQuery = []
    while not movieNameQuery:
        movieID = random.randint(1, size)
        movieNameQuery = sendDBQuery(cursor, "SELECT name FROM Movies WHERE id = %s;" % (movieID))
    movieName = movieNameQuery[0][0]

    return movieID, movieName


def sendDBQuery(cursor, text):
    try:
        return cursor.execute(text).fetchall()
    except psycopg.ProgrammingError:
        return []

def makeSurvey(user_id, questionslist, cursor):
    stamp = datetime.datetime.now()

    attr = [user_id, str(stamp)]
    Verifier.verifyInsert(cursor, "Survey", attr)
    surveyID = sendDBQuery(cursor, "SELECT ID FROM Survey WHERE creatorID = %s AND timestamp = '%s';" % (user_id, stamp))
        
    n_questions = random.randint(1, 3)
    for i in range(n_questions):
        mv1id, movie1_title = getRandomMovie(cursor)
        mv2id, movie2_title = getRandomMovie(cursor)

        attr = [surveyID[0][0], questionslist[random.randint(0, len(questionslist) - 1)], movie1_title, movie2_title]
        Verifier.verifyInsert(cursor, "SurveyQuestion", attr)        
    
class HiredCritic:
    reviews = [] #List of review ids
    surveys = [] #List of created surveys' ids

    #non-list self variables: userID (int), username (str)

    #Lists populated in _init_ function:
    #actionOptions, questions, survey_request_messages, comment_request_messages, comment_messages

    def __init__(self, user_id, db_cursor, num_actions):
        self.actionOptions = [self.review, self.createSurvey, self.requestSurvey, self.requestComment, self.makeComment]
        
        self.cursor = db_cursor
        self.userID = user_id
        
        try:
            self.username = sendDBQuery(self.cursor, "SELECT username FROM Users WHERE ID = %s;" % (user_id))[0]
        except IndexError:
            # TODO - call error reporter?
            print("Error: Username for user id %s not found! Aborting HiredCritic" % (user_id))
            return
        
        mvID, title = getRandomMovie(self.cursor)
        engagement = random.randint(0, 10)
        excitement = random.randint(0, 10)
        prod = random.randint(0, 10)
        explanation = self.getExplanation(title, (engagement + excitement + prod))
        attr = [self.userID, engagement, excitement, prod, str(explanation), mvID, str(datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "Review", attr)


        myreviews = sendDBQuery(self.cursor, "SELECT ID FROM Review WHERE userID = %s;" % (user_id))
        if(len(myreviews) > 0):
            self.reviews = myreviews

        mysurveys = sendDBQuery(self.cursor, "SELECT ID FROM Survey WHERE creatorID = %s;" % (user_id))
        if(len(mysurveys) > 0):
            self.surveys = mysurveys

        self.survey_request_messages = ["%s would like you to fill out their survey!" % (self.username),
                                        "Hey could you take my survey please? -%s" % (self.username),
                                        "Make your opinion heard by completing %s s survey!" % (self.username)]

        self.comment_request_messages = ["%s wants to hear from you!" % (self.username),
                                         "Yo what do you think of my review? Yours Truly, %s" % (self.username),
                                         "Remember what you told me about my review? Well you should share!"]

        self.comment_messages = ["Well said, I agree completely -%s" % (self.username),
                                 "Interesting take, but I found the film more enjoyable than you indicate -%s" % (self.username),
                                 "Its nice to hear others insight on this movie - I fell asleep halfway through! -%s" % (self.username),
                                 "I must disagree with your review. The plot was just so confusing that your rating is too kind. -%s" % (self.username)]
        
        self.questions = ["Better production value?", "More influential film?", "Best date night movie?",
                          "Which would you rather watch twice?", "Which couldve used a different director?",
                          "More iconic film?", "What movie would make for the best book?"]

        #Setup complete, start adding new data to db
        self.takeAction()

        for x in range(num_actions):
            self.takeAction()


    def takeAction(self):
        action_choice = random.randint(0, 4)

        #Don't request someone take a survey or comment on a review if you haven't created any surveys or reviews
        while((action_choice == 2 and len(self.surveys) == 0) or (action_choice == 3 and len(self.reviews) == 0)):
            action_choice = random.randint(0, 4)

        self.actionOptions[action_choice]()

    def review(self):
        mvID, title = getRandomMovie(self.cursor)

        engagement = random.randint(0, 10)
        excitement = random.randint(0, 10)
        prod = random.randint(0, 10)
        explanation = self.getExplanation(title, (engagement + excitement + prod))

        attr = [self.userID, engagement, excitement, prod, str(explanation), mvID, str(datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "Review", attr)
        self.reviews.append(sendDBQuery(self.cursor, "SELECT ID FROM Review WHERE userID = %s AND movieID = %s;" %(self.userID, mvID))[0])

        interface_data = sendDBQuery(self.cursor, "SELECT num_reviews, engagement_score, excitement_score, production_score FROM Interface WHERE movieID = %s;" % (mvID))

        if(len(interface_data) == 0):
            attr = [mvID, engagement, excitement, prod, str(1)]
            Verifier.verifyInsert(self.cursor, "Interface", attr)
        else:
            tot_eng = int(interface_data[0][1]) * int(interface_data[0][0]) + engagement
            tot_exc = int(interface_data[0][2]) * int(interface_data[0][0]) + excitement
            tot_prod = int(interface_data[0][3]) * int(interface_data[0][0]) + prod

            num_reviews = int(interface_data[0][0]) + 1
            real_eng = tot_eng / num_reviews
            real_exc = tot_exc / num_reviews
            real_prod = tot_prod / num_reviews

            attr = [mvID, real_eng, real_exc, real_prod, str(num_reviews)]
            Verifier.verifyInsert(self.cursor, "Interface", attr)            

    def getExplanation(self, title, rating):
        summary = ""

        if(rating < 4):
            summary = "Impressively atrocious"
        elif(rating < 10):
            summary = "A waste of time"
        elif(rating < 15):
            summary = "Underwhelming"
        elif(rating < 20):
            summary = "Good but not spectacular"
        elif(rating < 25):
            summary = "A really great production - well worth seeing"
        else:
            summary = "One of the best films of the year.  Everyone should see %s - dont miss it!" % (title)
            
        return summary

    def requestSurvey(self):
        # invitee = sendDBQuery(self.cursor, "SELECT id FROM Users ORDER BY RANDOM() LIMIT 1;")
        invitee = sendDBQuery(self.cursor, "SELECT id FROM Users LIMIT 1;")

        attr = [self.surveys[random.randint(0, len(self.surveys) - 1)], invitee[0][0], str(self.survey_request_messages[random.randint(0, len(self.survey_request_messages) - 1)]), str(datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "SurveyInvite", attr)
        # sendDBQuery(self.cursor, "INSERT INTO SurveyInvite VALUES (DEFAULT, %s, %s, '%s', '%s');" % (self.surveys[random.randint(0, len(self.surveys) - 1)], invitee, self.survey_request_messages[random.randint(0, len(self.survey_request_messages) - 1)], datetime.datetime.now()))                            

    def requestComment(self):
        # invitee = sendDBQuery(self.cursor, "SELECT id FROM Users ORDER BY RANDOM() LIMIT 1;")
        invitee = sendDBQuery(self.cursor, "SELECT id FROM Users LIMIT 1;")
        
        attr = [self.reviews[random.randint(0, len(self.reviews) - 1)][0], invitee[0][0], str(self.comment_request_messages[random.randint(0, len(self.comment_request_messages) - 1)]), str(datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "ReviewCommentInvite", attr)

    def makeComment(self):
        # reviewID = sendDBQuery(self.cursor, "SELECT id FROM review ORDER BY RANDOM() LIMIT 1;")
        reviewID = sendDBQuery(self.cursor, "SELECT id FROM review LIMIT 1;")

        attr = [reviewID[0][0], self.userID, str(self.comment_messages[random.randint(0, len(self.comment_messages) - 1)]), str(datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "ReviewComments", attr)

    def createSurvey(self):
        makeSurvey(self.userID, self.questions, self.cursor)        
