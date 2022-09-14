import psycopg
import HiredCritic


def printStats(db_username, time_diff):
    conn = psycopg.connect("dbname='grp6admin' user='%s'" % (db_username))
    cursor = conn.cursor()
    successCount = HiredCritic.sendDBQuery(cursor, "SELECT COUNT(type) FROM Verifier WHERE type = 'SUCCESS';")
    incorrectCount = HiredCritic.sendDBQuery(cursor, "SELECT COUNT(type) FROM Verifier WHERE type = 'INCORRECT';")
    failedCount = HiredCritic.sendDBQuery(cursor, "SELECT COUNT(type) FROM Verifier WHERE type = 'FAILED';")
    print("DATA INTEGRITY (insert stats):\nsuccess: %d, incorrect: %d, failed: %d" % (successCount[0][0], incorrectCount[0][0], failedCount[0][0]))

    execution_time = time_diff.total_seconds() * 1000
    print("TOTAL RUNTIME:\n%d ms" % (execution_time))

