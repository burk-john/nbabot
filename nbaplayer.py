import json
import requests
import csv
import jsonpickle

class player:
    def __init__(self, name, team, pos, age, ppg, rpg, apg, spg, bpg, tsp, claimed, id):
        self.name = name
        self.team = team
        self.pos = pos
        self.age = age
        self.ppg = ppg
        self.rpg = rpg
        self.bpg = bpg
        self.apg = apg
        self.spg = spg
        self.tsp = tsp
        self.claimed = claimed
        self.id = id

    def playerStr(self):
        return ("Name: " + self.getName() + '\n' + "Team: " + self.getTeam().upper() + ', ' + "Pos: " + self.getPos() + ", " + "Age: " + str(self.getAge()) + '\n' + "PPG: " + str(self.getPPG()) +
        ", " + "RPG " + str(self.getRPG()) + ", " + "BPG: " + str(self.getBPG()) + ", " + "SPG: " + str(self.getSPG()))

    def getTSP(self):
        return self.tsp

    def setID(self, PID):
        self.id = PID

    def getID(self):
        return self.id

    def getClaim(self):
        if self.claimed == "":
            return "Nobody"
        return self.claimed

    def getName(self):
        return self.name

    def getTeam(self):
        return self.team

    def getPos(self):
        return self.pos

    def getAge(self):
        return self.age

    def getPPG(self):
        return self.ppg

    def getRPG(self):
        return self.rpg

    def getBPG(self):
        return self.bpg

    def getSPG(self):
        return self.spg

    def getAPG(self):
        return self.apg

    def setName(self, nm):
        self.name = nm

    def setTeam(self, tm):
        self.team = tm

    def setPos(self, posn):
        self.pos = posn

    def setAge(self, ag):
        self.age = ag

    def setPPG(self, pts):
        self.ppg = pts

    def setRPG(self, reb):
        self.rpg = reb

    def setBPG(self, blk):
        self.bpg = blk

    def setSPG(self, stl):
        self.spg = stl

    def setAPG(self, ast):
        self.apg = ast

    def setClaim(self, clm):
        self.claimed = clm
