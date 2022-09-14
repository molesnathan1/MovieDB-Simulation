import HiredCritic
import psycopg
import random
import time
import Verifier
import datetime


class UserCritic:

    def __init__(self, user_id, db_cursor, num_actions):
        self.action_options = [self.takeSurvey, self.reviewMovie, self.createSurvey, self.respondToRequest]

        self.cursor = db_cursor
        self.userID = user_id

        self.requesting_surveys = []
        self.requesting_comments = []
        self.requested_comments = []
        self.requested_surveys = []
        
        self.comment_messages = ["This is way too wordy. Just make your point and move on.", "Wow, your enthusiasm is infectious. I didnt plan to watch this but I think I will now.",
                                 "Ha nice review bro. You think youre some sort of professional critic?", "I couldnt agree more - well said!",
                                 "Well we clearly have different tastes...", "Nice review. And to think this film was under budget too!"]
        self.questions = ["Which movie is better?", "Which was more exciting?",
                          "More engaging film?", "Would you rather see a sequel for..."]

        try:
            self.username = HiredCritic.sendDBQuery(self.cursor, "SELECT username FROM Users WHERE ID = %s;" % (user_id))[0][0]
        except IndexError:
            #print("Error: Username for user id %s not found! Aborting UserCritic" % (user_id))
            return

        self.takeAction()
        for x in range(num_actions):
            self.takeAction()

    def takeAction(self):
        random_choice = random.randint(0, 3)
        self.requesting_surveys = HiredCritic.sendDBQuery(self.cursor, "SELECT id FROM SurveyInvite WHERE inviteeID = %s;" % (self.userID))
        self.requesting_comments = HiredCritic.sendDBQuery(self.cursor, "SELECT id FROM ReviewCommentInvite WHERE inviteeID = %s;" % (self.userID))

        if(random_choice == 3 and len(self.requesting_surveys) == len(self.requested_surveys) and len(self.requesting_comments) == len(self.requested_comments)):
            random_choice = random.randint(0, 2)

        self.action_options[random_choice]()
        
    def reviewMovie(self):
        mvID, title = HiredCritic.getRandomMovie(self.cursor)
        reviewed = HiredCritic.sendDBQuery(self.cursor, "SELECT movieID FROM Review WHERE userID = %s;" % (self.userID))
        while(mvID in reviewed):
            mvID, title = HiredCritic.getRandomMovie(self.cursor)

        ratings = [random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)]
        for i in range(3):
            #Users are mean & they don't do 4s or 6s
            if(ratings[i] in (4, 6) ):
                ratings[i] = ratings[i] - 1
        
        explanation = self.getExplanation(title, (ratings[0] + ratings[1] + ratings[2]))

        attributes = [self.userID, ratings[0], ratings[1], ratings[2], explanation, mvID,
                      str(datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "Review", attributes)
        # self.reviews.append(sendDBQuery(self.cursor, "SELECT ID FROM Review WHERE userID = %s AND movieID = %s;" %(self.userID, mvID)))

        interface_data = HiredCritic.sendDBQuery(self.cursor, "SELECT num_reviews, engagement_score, excitement_score, production_score FROM Interface WHERE ID = %s;" % (mvID))

        if(len(interface_data) == 0):
            attr = [mvID, ratings[0], ratings[1], ratings[2], str(1)]
            Verifier.verifyInsert(self.cursor, "Interface", attr)
        else:
            tot_eng = int(interface_data[0][1]) * int(interface_data[0][0]) + ratings[0]
            tot_exc = int(interface_data[0][2]) * int(interface_data[0][0]) + ratings[1]
            tot_prod = int(interface_data[0][3]) * int(interface_data[0][0]) + ratings[2]

            num_reviews = int(interface_data[0][0]) + 1
            real_eng = tot_eng / num_reviews
            real_exc = tot_exc / num_reviews
            real_prod = tot_prod / num_reviews

            attr = [mvID, real_eng, real_exc, real_prod, str(num_reviews)]
            Verifier.verifyInsert(self.cursor, "Interface", attr)      

    def getExplanation(self, title, rating):
        summary = ""

        if(rating < 4):
            summary = "My toddler does better"
        elif(rating < 10):
            summary = "Yikes"
        elif(rating < 15):
            summary = "Bad"
        elif(rating < 20):
            summary = "Mostly entertaining"
        elif(rating < 25):
            summary = "Yes"
        else:
            summary = "OMG this was so good!!!!"
            
        #Double apostrophe escapes premature end of string
        return ("%s reviews %s: %s" % (self.username, title, summary))

    def createSurvey(self):
        HiredCritic.makeSurvey(self.userID, self.questions, self.cursor)

    def takeSurvey(self):
        if HiredCritic.sendDBQuery(self.cursor, "SELECT COUNT(*) FROM Survey;")[0][0] == 0:
            return
        survey_id = HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM Survey OFFSET floor(random() * (SELECT COUNT(*) FROM Survey)) LIMIT 1;")[0][0]
        questionIDs = HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM SurveyQuestion WHERE surveyID = %s;" % (survey_id))[0]
        for qid in questionIDs:
            attr = [qid, (True == random.randint(0, 1)), survey_id, str(datetime.datetime.now())]
            Verifier.verifyInsert(self.cursor, "SurveyQuestionResponse", attr)

    def respondToRequest(self):
        if((len(self.requesting_surveys) - len(self.requested_surveys) % 2) != 0):
            self.surveyResponse()
        else:
            self.commentResponse()

    def surveyResponse(self):
        for s in self.requesting_surveys:
            if s not in self.requested_surveys:
                questionIDs = HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM SurveyQuestion WHERE surveyID = %s;" % (s))[0]
                self.requested_surveys.append(s)
                for qid in questionIDs:
                    attr = [self.userID, qid, (True == random.randint(0, 1)), s, str(datetime.datetime.now())]
                    Verifier.verifyInsert(self.cursor, "SurveyQuestionResponse", attr)
                return

    def commentResponse(self):
        review = self.requesting_comments[0]
        count = 0
        while review in self.requested_comments and count < 100:
            count += 1
            review = self.requesting_comments[random.randint(0, len(self.requesting_comments) - 1)]
            
        if count >= 99:
            review = HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM Review OFFSET floor(random() * (SELECT COUNT(*) FROM Review)) LIMIT 1;")
        else:
            self.requested_reviews.append(review)
            
        attr = [review, self.userID, self.comment_messages[random.randint(0, len(self.comment_messages) - 1)],
                str(datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "ReviewComments", attr)
        
