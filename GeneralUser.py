import HiredCritic
import psycopg
import random
import Verifier

class GeneralUser:

    def __init__(self, user_id, db_cursor, num_actions):
        self.action_options = [self.takeSurvey, self.respondToReview]
        self.cursor = db_cursor
        self.userID = user_id
        self.requested_surveys = []
        
        try:
            self.username = HiredCritic.sendDBQuery(self.cursor, "SELECT username FROM Users WHERE ID = %s;" % (user_id))[0]
        except IndexError:
            print("Error: Username for user id %s not found! Aborting GeneralUser" % (user_id))
            return

        self.comment_messages = ["How could you slander such a masterpiece?", "Sure the action was cool but the plot sucked.",
                                 "Well said, I felt the exact same way when watching. - %s" % (self.username),
                                 "This is your whole review? IMDB should hire me instead!"]
            
        self.takeAction()
        for x in range(num_actions):
            self.takeAction()
            #Perform n random actions that the user has permission to do
            
    def takeAction(self):
        random_choice = random.randint(0, 1)
        #If there are no requested surveys for the user to take, then their only option is to leave a comment on a review. Otherwise, the user will randomly either respond to a survey or comment on a review.
        requests = HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM SurveyInvite WHERE inviteeID = %s;" % (self.userID))
        self.requested_surveys = requests[0] if len(requests) > 0 else []
        if(len(self.requested_surveys) == 0):
            random_choice = 1
        self.action_options[random_choice]()
        
    def takeSurvey(self):
        self.surveyID = self.requested_surveys[random.randint(0, len(self.requested_surveys) - 1)]
        self.questionID = HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM SurveyQuestion WHERE surveyID = %s LIMIT 1;" % (self.surveyID))
        attr = [self.questionID, random.randint(0,1), self.surveyID, str(HiredCritic.datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "SurveyQuestionResponse", attr)
        
    
    def respondToReview(self):
        if HiredCritic.sendDBQuery(self.cursor, "SELECT COUNT(*) FROM Review;")[0][0] == 0:
            return
        self.reviewID = HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM Review ORDER BY RANDOM() LIMIT 1;")[0][0]
        attr = [self.reviewID, self.userID, self.comment_messages[random.randint(0, len(self.comment_messages) - 1)], str(HiredCritic.datetime.datetime.now())]
        Verifier.verifyInsert(self.cursor, "ReviewComments", attr)
