import psycopg
import ResetDB
import CreateDB
import HiredCritic
import UserSpawner
import sys
import threading
import os
import logging
import datetime
import Util

db_username = "grp6admin"
numThreads = int(sys.argv[1])
numUsers = int(sys.argv[2])
numActions = int(sys.argv[3])

start_time = datetime.datetime.now()

def createSpawner(name, n_users, n_actions, threadNum):
    UserSpawner.UserSpawner(name, n_users, n_actions, threadNum)
    return
        
#Create DB program
if __name__ == "__main__":
    ResetDB.ResetDB(db_username)
    CreateDB.CreateDB(db_username)

#remove previous logfile
logName = "verifier.log"
if os.path.exists(logName):
    os.remove(logName)

threads = []

for i in range(numThreads):
    threadi = threading.Thread(target=createSpawner, name=i, args=(db_username, numUsers, numActions, i))
    threads.append(threadi)

for x in threads:
    x.start()

for x in threads:
    x.join()

end_time = datetime.datetime.now()
time_diff = (end_time - start_time)
Util.printStats(db_username, time_diff)

