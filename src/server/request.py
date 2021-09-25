
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
    'game/make-play': 'makeGamePlay',
    'game/status': 'getGameStatus'
}

CLIENT_OPTIONS = {
    'new_game': {
        'prompt': 'Create a new Game',
        'uri': 'new/game'
    },
    'join_game': {
        'prompt': 'Join Game',
        'uri': 'game/join'
    },
    'make_play': {
        'prompt': 'Make Play',
        'uri': 'game/make-play'
    },
    'game_status': {
        'prompt': 'Game Status',
        'uri': 'game/status'
    },
    'game_reset': {
        'prompt': 'Game Reset',
        'uri': 'game/reset'
    }
}

def cleanQueryStringVars(vars):
    data = {}
    for i,j in vars.items():
        if isinstance(j, list) and len(j) == 1:
            j = j[0]
        data[i]=j
    return data

class ServerRequest:

    uri = ""
    qs_vars = {}
    data = None
    player_id = None
    game_id = None
    game = None

    def __init__(self, httpd):

        self.response = ServerResponse(self)
        self.game_data = GameData()
        
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


        # client_accept = httpd.headers['Accept'] # Accepts
        # if client_accept != None and HTTPContentType.JSON.value in client_accept:
        #     self.response.setContentType(HTTPContentType.JSON.value)

        self.print()

    def print(self):
        os.system('clear')
        print('-- HTTP ServerRequest --')
        print("Type:", self.httpd.request_type.name)
        print("Header:", self.httpd.headers)
        print("Client Address:", self.client_address)
        print("URI (path):", self.uri)
        # print("Accept:", self.accept)
        print("Query String (vars):", self.qs_vars)
        print("Data:", self.data)

    def getQsVar(self, key):
        if key in self.qs_vars:
            return self.qs_vars[key]
        return None

    def processRequest(self):

        self.player_id = self.getQsVar('player_id')
        self.game_id = self.getQsVar('game_id')
        if self.game_id != None:
            self.game = self.game_data.getGame(self.game_id)

        # TODO: handle response content type - right now only application json
        self.response.setContentType('application/json')

        if self.uri in URI_FNC_DICT.keys():
            uri_method = getattr(self, URI_FNC_DICT[self.uri])
            self.response.setOutput(uri_method())
        else:
            self.response.setStatus(HTTPStatus.BAD_REQUEST)
            # TODO set response message

        if self.game != None:
            self.game_data.updateGame(self.game)

        self.game_data.save()

        return self.response

    def newPlayer(self):
        player = self.game_data.newPlayer()
        self.player_id = player['id']

        message = ""
        client_data = {}
        client_options = []

        message = "Welcome {}!".format(player['name'])
        client_data['player_id'] = self.player_id
        client_options.append(CLIENT_OPTIONS['new_game'])
        client_options.append(CLIENT_OPTIONS['join_game'])

        return {
            'message': message,
            'client_data': client_data,
            'client_options': client_options,
        }

    def newGame(self):

        self.game = self.game_data.newGame()
        self.game_id = self.game['id']
        # TODO: validate that player_id exists and is valid
        self.game['players'].append(self.player_id)
        
        # self.game_data.addPlayerToGame(self.game_id, self.player_id)

        client_options = [
            CLIENT_OPTIONS['make_play'],
            CLIENT_OPTIONS['game_status'],
        ]

        message = "New Game Created"
        
        return {
            'client_data': {
                'game_id': self.game_id,
                # 'player_id': player_id
            },
            'client_options': client_options,
            'message': message
        }

    def makeGamePlay(self):

        # check if player can make play
        # if len(self.game['players']) < 2:
        #      return {
        #          'message': 'Cannot make a play yet. Still waiting for other player to join.'
        #      }

        message = ""
        client_options = [
            CLIENT_OPTIONS['make_play'],
            CLIENT_OPTIONS['game_status'],
        ]

        round_num = str(self.game['current_round'])
        if round_num not in self.game['rounds_data']:
            self.game['rounds_data'][round_num] = {
                'plays': {},
                'winner': None
            }
        round = self.game['rounds_data'][round_num]

        if self.player_id in round['plays']: # already made a play
            message = "You already made a play this round!\nYou played: '%s'\nPlease wait for the other player to make a play." % round['plays'][self.player_id]
            return {
                'client_options': client_options,
                'message': message
            }

        play = self.getQsVar('play_type')

        if play == None:
            message = "Choose a play to make:"
            client_options = [
                {
                    'prompt': 'Rock',
                    'uri': 'game/make-play',
                    'qs': {
                        'play_type': 'rock'
                    }
                },
                {
                    'prompt': 'Paper',
                    'uri': 'game/make-play',
                    'qs': {
                        'play_type': 'paper'
                    }
                },
                {
                    'prompt': 'Scissors',
                    'uri': 'game/make-play',
                    'qs': {
                        'play_type': 'scissors'
                    }
                },
            ]
        else:
            round['plays'][self.player_id] = play
            self.game['rounds_data'][round_num] = round
            message = "You played: %s" % play

        return {
            'client_options': client_options,
            'message': message
        }

    def joinGame(self):

        message = ""
        client_data = {}
        client_options = []

        join_game_id = self.getQsVar('join_game_id')
        
        if join_game_id == None:
            # available games
            available_games = self.game_data.getAvailableGames(self.player_id)
            if len(available_games) > 0:
                message = "Choose a game to join"
                for game in available_games:
                    client_options.append({
                        'prompt': 'Join game: %s' % game['id'],
                        'uri': 'game/join',
                        'qs': {
                            'join_game_id': game['id']
                        }
                    })
            else:
                message = "The are no available games to join"
                client_options.append(CLIENT_OPTIONS['new_game'])
                client_options.append(CLIENT_OPTIONS['join_game'])
        else:
            self.game_data.data['games'][join_game_id]['players'].append(self.player_id)
            self.game_id = join_game_id
            self.game = self.game_data.data['games'][self.game_id]
            
            client_data['game_id'] = self.game_id

            client_options = [
                CLIENT_OPTIONS['make_play'],
                CLIENT_OPTIONS['game_status']
            ]

        # if 'game_id' in self.qs_vars.keys():
        #     self.game_data.addPlayerToGame(self.qs_vars['game_id'], self.qs_vars['player_id'])
        #     client_data['game_id'] = self.qs_vars['game_id']
        #     msg = 'Joined Game: '+self.qs_vars['game_id']
        #     options = [
        #         CLIENT_OPTIONS['make_play'],
        #         CLIENT_OPTIONS['game_status'],
        #     ]
            
        # else:
        #     self.game_data.getAvailableGames()
        #     available_games = self.game_data.getAvailableGames() # TODO: error is 0, send error header
        #     for id in available_games:
        #         options.append({
        #             'prompt': id,
        #             'uri': 'game/join',
        #             'qs': {
        #                 'game_id': id
        #             }
        #         })
        

        return {
            'client_data': client_data,
            'client_options': client_options,
            'message': message
        }

    def getGameStatus(self):
        
        game_id = self.qs_vars['game_id']
        game = self.game_data.data['games'][game_id]

        message = "Game Status: %s\n" % (game['name'])

        return {
            'client_options': [
                CLIENT_OPTIONS['make_play'],
                CLIENT_OPTIONS['game_status'],
                # CLIENT_OPTIONS['game_reset']
            ],
            'message': message
        }
