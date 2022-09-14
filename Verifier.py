import random
import time
import datetime
import psycopg
import HiredCritic
import logging


def verifyInsert(cursor, tableName, attributesList):
    attributesText = attributesToText(attributesList)

    insertText = "INSERT INTO " + tableName + " VALUES (" + attributesText + ") RETURNING id;"
    lastIDQuery = HiredCritic.sendDBQuery(cursor, insertText)
    
    lastID = str(lastIDQuery[0][0])

    selectText = "SELECT * FROM " + tableName + " WHERE ID = " + lastID + ";"
    selectQuery = HiredCritic.sendDBQuery(cursor, selectText)
    selectList = list(selectQuery[0]) 

    logWrite(cursor, attributesList, selectList, insertText, tableName)

def logWrite(cursor, insertList, selectList, insertText, tableName):
    logging.basicConfig(filename='verifier.log', encoding='utf-8', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    type = ""
    compNum = compareLists(insertList, selectList) 
    if compNum == 0:
        logging.info(" SUCCESS: " + insertText)
        type = "SUCCESS"
    elif compNum == 1:
        logging.warning(" INCORRECT(wrong data found): " + insertText)
        type = "INCORRECT"
    else:
        logging.error(" FAILED(no data found): " + insertText)
        type = "FAILED"

    attr = [type, str(datetime.datetime.now())]
    verifierText = attributesToText(attr)
    verifierQuery = "INSERT INTO Verifier VALUES (" + verifierText + ");"
    lastIDQuery = HiredCritic.sendDBQuery(cursor, verifierQuery)

def compareLists(insertList, selectList):
    if not selectList:
        return -1
    
    selectList.pop(0)
    if (selectList == insertList):
        return 0
    
    return 1

def attributesToText(attributesList):
    attributesText = "DEFAULT, "

    listLen = len(attributesList)
    for i in range(listLen):
        if not isinstance(attributesList[i], str):
            attributesText = attributesText + str(attributesList[i])
        else:
            attributesText = attributesText + "'" + str(attributesList[i]) + "'"
        if i != listLen - 1:
            attributesText = attributesText + ", "
    
    return attributesText


