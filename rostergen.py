import nbaplayer
import requests
import csv
import string
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.static import players
import pidobj
import urllib.request, json, jsonpickle
roster = []
pidlist = []

def setup():
    with open('C:/Users/John/Downloads/pids.json') as file:
        file_data = file.read()
        file_data = file_data.replace("{}", "},{}")
        file_data = "[" + file_data + "]"
        data = json.loads(file_data)
        idList = data[0]['league']['standard']
        for x in range (len(idList)):
            pidlist.append(pidobj.pidobj((idList[x].get('firstName') + " " + idList[x].get('lastName')), idList[x].get('personId')))

    with open('C:/Users/John/Downloads/nba2020.csv') as file:
        csv_reader = csv.reader(file)

        next(csv_reader)
        next(csv_reader)

        for line in csv_reader:
            roster.append(nbaplayer.player(line[1].rstrip(), line[2].rstrip(), line[3].rstrip(), int(float(line[4])), line[18].rstrip(), line[19].rstrip(), line[21].rstrip(), line[23].rstrip(), line[24].rstrip(), line[17], "", 0))
        # print(roster[5].playerStr());
        print("Done creating fresh roster.")

    for x in range (len(pidlist)):
        for y in range (len(roster)):
            if pidlist[x].getName() == roster[y].getName():
                roster[y].setID(pidlist[x].getID())
    print("Done appending IDs.")


    
