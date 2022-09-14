import HiredCritic
import UserCritic
import GeneralUser
import psycopg
import random
import string
import Verifier
import datetime

class UserSpawner:

    #Types of users: h = hired critic, u = user critic, g = general user
    def __init__(self, dbname, numUsers, numActions, threadNum):
        self.user_types = [self.createHiredCritic, self.createUserCritic, self.createGeneralUser]
        self.nactions = numActions
        #Connect to db grp6 admin using provided username
        conn = psycopg.connect("dbname='grp6admin' user='%s'" % (dbname))
        self.cursor = conn.cursor()

        s = ""
        self.username = s.join(random.sample(string.ascii_lowercase*12, 12)) #generate a random username of 12 lowercase letters

        userNum = 0
        for x in range(numUsers):
            start_time = datetime.datetime.now()
            userNum = userNum + 1
            type = self.spawnUser()
            s = ""
            self.username = s.join(random.sample(string.ascii_lowercase*12, 12))
            #Spawn users with sequential user ids, random usernames, and random user types
            end_time = datetime.datetime.now()
            time_diff = (end_time - start_time)
            execution_time = time_diff.total_seconds() * 1000
            userType = ""
            if type == 0:
                userType = "Hired Critic"
            elif type == 1:
                userType = "User Critic"
            else:
                userType = "General User"
            print('thread %d user %d type %s: %d ms' % (threadNum, userNum, userType, execution_time)) 

        conn.commit()
       
    def spawnUser(self):
        usertype = random.randint(0, 2) #Randomly determine the type of user to be created
        self.user_types[usertype]()
        return usertype
        
    def createHiredCritic(self):
        attr = [self.username, "h"]
        Verifier.verifyInsert(self.cursor, "Users", attr)
        HiredCritic.HiredCritic(HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM Users WHERE username = '%s';" % (self.username))[0][0], self.cursor, self.nactions)
    
    def createUserCritic(self):
        attr = [self.username, "u"]
        Verifier.verifyInsert(self.cursor, "Users", attr)
        UserCritic.UserCritic(HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM Users WHERE username = '%s';" % (self.username))[0][0], self.cursor, self.nactions)
    
    def createGeneralUser(self):
        attr = [self.username, "g"]
        Verifier.verifyInsert(self.cursor, "Users", attr)
        GeneralUser.GeneralUser(HiredCritic.sendDBQuery(self.cursor, "SELECT ID FROM Users WHERE username = '%s';" % (self.username))[0][0], self.cursor, self.nactions)
