
import os
import time
import string
import random
import json

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def unique_id(id_list):
    id = id_generator()
    while id in id_list:
            id = id_generator()
    return id

def loadJsonFile(filename):
    if os.path.isfile(filename):
        with open(filename, 'rt') as json_file:
            try:
                data = json.load(json_file)
                return data
            except:
                print("Unable to load JSON file:", filename)
                return None

GAME_DATA_FILENAME = os.getcwd() + '/game-data.json'

EMPTY_GAME_DATA = {
    'games': {},
    'players': {}
}

class GameData:

    data = EMPTY_GAME_DATA

    def __init__(self):
        self.loadData()

    def loadData(self):
        file_data = loadJsonFile(GAME_DATA_FILENAME)
        if file_data != None:
            self.data = file_data

    def save(self):
        data = json.dumps(self.data, indent=4)
        f = open(GAME_DATA_FILENAME, 'wt')
        f.write(data)
        f.close()

    def clearData(self):
        self.data = EMPTY_GAME_DATA
        self.save()
    
    def getGame(self, game_id):
        if game_id in self.data['games']:
            return self.data['games'][game_id]
        return None

    def updateGame(self, game):
        self.data['games'][game['id']] = game

    def newPlayer(self):
        id = unique_id(self.data['players'].keys())
        player = {
            'id': id,
            'name' : "Player {}".format(len(self.data['players'].keys()) + 1),
            'created_date': time.time() #time.asctime( time.localtime(time.time()) ),
        }
        self.data['players'][id] = player
        # self.save()
        return player

    def newGame(self):
        id = unique_id(self.data['games'].keys())
        game = {
            'id': id,
            'name' : "Game {}".format(len(self.data['games'].keys()) + 1),
            'players': [],
            'status': 'new',
            'num_rounds': 3,
            'current_round': 1,
            'rounds_data': {},
            'created_date': time.time(), # time.asctime( time.localtime(time.
            'winner': None
        }
        self.data['games'][id] = game
        # self.save()
        return game

    # def addPlayerToGame(self, game_id, player_id):
    #     self.data['games'][game_id]['players'].append(player_id) # TODO: validations
    #     self.save()

    def getAvailableGames(self, player_id):
        data = []
        for i, game in self.data['games'].items():
            if game['status'] != 'new' or len(game['players']) > 1 or player_id in game['players']:
                continue
            data.append(game)
        return data
