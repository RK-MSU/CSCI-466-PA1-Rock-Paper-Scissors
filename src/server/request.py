
import os
import json
from http import HTTPStatus
from .http import HTTPContentType
from urllib.parse import urlparse, parse_qs
from .response import ServerResponse
from .game_data import GameData

URI_FNC_DICT = {
    'new/player': 'newPlayer',
    'new/game': 'newGame',
    'game/join': 'joinGame',
    'game/throw-play': 'makeGameThrow',
    'game/status': 'getGameStatus',
    'game/throw-results': 'getThrowResults',
    'game/reset': 'resetGame'
}

EMPTY_GAME_ROUND = {
    'plays': {},
    'winner': None,
    'tie': False
}

def cleanQueryStringVars(vars):
    data = {}
    for i,j in vars.items():
        if isinstance(j, list) and len(j) == 1:
            j = j[0]
        data[i]=j
    return data

def getRoundWinnerPlayerId(round_plays):
    player_one_id = list(round_plays.keys())[0]
    player_one_play = round_plays[player_one_id]
    player_two_id = list(round_plays.keys())[1]
    player_two_play = round_plays[player_two_id]

    if player_one_play == player_two_play:
        return None

    if player_one_play == 'rock':
        if player_two_play == 'scissors':
            return player_one_id
        if player_two_play == 'paper':
            return player_two_id
    
    if player_one_play == 'paper':
        if player_two_play == 'rock':
            return player_one_id
        if player_two_play == 'scissors':
            return player_two_id

    if player_one_play == 'scissors':
        if player_two_play == 'paper':
            return player_one_id
        if player_two_play == 'rock':
            return player_two_id

class ServerRequest:

    uri = ""
    qs_vars = {}
    data = None
    output_data = None

    def __init__(self, httpd):
        # self.response = ServerResponse(self)
        self.httpd = httpd # Http handler
        self.client_address = self.httpd.client_address # client address
        self.headers = self.httpd.headers # request headers
        # URI (path)
        parsed_path = urlparse(httpd.path)
        self.uri = str(parsed_path.path).strip('/')
        # Query String (vars)
        self.qs_vars = cleanQueryStringVars(parse_qs(parsed_path.query))

        content_len = httpd.headers['Content-Length'] # Content-Length
        if content_len != None:
            try:
                content_len = int(content_len)
            except ValueError:
                print("ValueError Message") # TODO: make appropriate message
                content_len = None

        if content_len != None:
            self.data = self.httpd.rfile.read(content_len)
            self.data = self.data.decode("utf-8")

        # TODO: content-type could be a number of things
        # post requests are: x-www-form-urlencoded
        content_type = httpd.headers['Content-Type']
        if self.data != None and content_type != None:
            if content_type == 'application/json':
                try:
                    self.data = json.loads(self.data)
                except:
                    print("Error loading Request Data to JSON") # TODO: make appropriate message

        self.print()

    def print(self):
        os.system('clear')
        print("{!s:-^50}\n{!s:->50}\n{!s:<18}{!s}\n{!s:<18}{!s}\n{!s:<18}{!s}\n{!s:<18}{!s}\n".format('Server Request','',"Type:",self.httpd.request_type.name,"Path:", self.httpd.path,'URI',self.uri,'QS Vars',self.qs_vars))

    def getQsVar(self, key):
        if key in self.qs_vars:
            return self.qs_vars[key]
        return None

    def processRequest(self):
        # TODO: handle response content type - right now only application json
        self.response = ServerResponse(self)
        self.response.setContentType('application/json')
        game_data = GameData(self)
        if self.uri in URI_FNC_DICT.keys():
            uri_method = getattr(game_data, URI_FNC_DICT[self.uri])
            self.response.setOutput(uri_method())
            game_data.save()
        else:
            self.response.setStatus(HTTPStatus.BAD_REQUEST)
        return self.response
