
import os
import time
import string
import random
import json
from http import HTTPStatus

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def unique_id(id_list=[]):
    id = id_generator()
    while id in id_list:
            id = id_generator()
    return id


CLIENT_OPTIONS = {
    'new_game': {
        'prompt': 'Create a new Game',
        'uri': 'new/game'
    },
    'join_game': {
        'prompt': 'Join Game',
        'uri': 'game/join'
    },
    'throw_play': {
        'prompt': 'Throw Play',
        'uri': 'game/throw-play'
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

CLIENT_COMMON_PLAY_OPTIONS = [
    {
        'prompt': 'Rock',
        'uri': 'game/throw-play',
        'qs': {
            'throw': 'rock'
        }
    },
    {
        'prompt': 'Paper',
        'uri': 'game/throw-play',
        'qs': {
            'throw': 'paper'
        }
    },
    {
        'prompt': 'Scissors',
        'uri': 'game/throw-play',
        'qs': {
            'throw': 'scissors'
        }
    },
]


class GameData:

    data_filename = os.getcwd() + '/game-data.json'
    player_id = None
    player = None
    game_id = None
    game = None
    round = None
    round_id = None
    throw = None
    throw_id = None
    data = {
        'games': {},
        'players': {},
        'rounds': {},
        'throws': {}
    }

    def __init__(self, request):
        self.request = request
        self._loadDataFromFile()
        self.player_id = self.request.getQsVar('player_id')
        self.game_id = self.request.getQsVar('game_id')
        if self.player_id != None:
            self.player = self.data['players'][self.player_id]
        if self.game_id != None:
            self.game = self.data['games'][self.game_id]
        if self.game != None and self.game['round_current'] != None:
            self.round_id = self.game['round_current']
            self.round = self.data['rounds'][self.round_id]

    def _loadDataFromFile(self):
        if os.path.isfile(self.data_filename):
            with open(self.data_filename, 'rt') as json_file:
                try:
                    self.data = json.load(json_file)
                except:
                    print("Unable to load JSON file:", self.data_filename)

    def save(self):
        if self.game != None:
            self.data['games'][self.game['id']] = self.game
        if self.player != None:
            self.data['players'][self.player['id']] = self.player
        if self.round != None:
            self.data['rounds'][self.round['id']] = self.round
        if self.throw != None:
            self.data['throws'][self.throw['id']] = self.throw
        data = json.dumps(self.data, indent=4)
        f = open(self.data_filename, 'wt')
        f.write(data)
        f.close()

    def clearData(self):
        self.data = {
            'games': {},
            'players': {},
            'rounds': {},
            'throws': {}
        }
        self.save()

    def getAvailableGames(self):
        player_id = self.request.getQsVar('player_id')
        data = []
        for i, game in self.data['games'].items():
            if game['status'] != 'new' or len(game['players']) > 1:
                continue
            if player_id != None:
                if player_id in game['players']:
                    continue
            data.append(game)
        return data

    def _newPlayer(self):
        self.player_id = unique_id(list(self.data['players'].keys()))
        self.player = {
            'id': self.player_id,
            'name' : "Player {}".format(len(self.data['players'])+1),
            'created_date': time.time(),
            'last_throw': None
        }

    def _newGame(self):
        self.game_id = unique_id(list(self.data['games'].keys()))
        self.game = {
            'id': self.game_id,
            'name' : "Game {}".format(len(self.data['games'].keys())+1),
            'created_date': time.time(),
            'winner': None,
            'players': [],
            'status': 'new',
            'round_limit': 3,
            'round_current': None,
            'rounds': [],
            'reset_request': []
        }
        self.data['games'][self.game_id] = self.game

    def _newGameRound(self):
        # TODO: validation: make sure game is init
        self.round_id = unique_id(list(self.data['rounds'].keys()))
        self.round = {
            'id': self.round_id,
            'game_id': self.game_id,
            'order': len(self.game['rounds'])+1,
            'winner': None,
            'tie': False,
            'throws': []
        }
        self.game['round_current'] = self.round_id
        self.game['rounds'].append(self.round_id)
        self.data['rounds'][self.round_id] = self.round

    def _newThrow(self, value):
        self.throw_id = unique_id(list(self.data['throws'].keys()))
        self.throw = {
            'id': self.throw_id,
            'player_id': self.player_id,
            'game_id': self.game_id,
            'round_id': self.round_id,
            'value': value
        }
        self.round['throws'].append(self.throw_id)
        self.data['throws'][self.throw_id] = self.throw
        self.player['last_throw'] = self.throw_id
        self._checkRoundWinner()

    def _checkRoundWinner(self):

        if len(self.round['throws']) < 2:
            return
        throw_one = self.data['throws'][self.round['throws'][0]]
        throw_two = self.data['throws'][self.round['throws'][1]]

        if throw_one['value'] == throw_two['value']:
            self.round['tie'] = True
        elif throw_one['value'] == 'rock':
            if throw_two['value'] == 'scissors':
                self.round['winner'] = throw_one['player_id']
            elif throw_two['value'] == 'paper':
                self.round['winner'] = throw_two['player_id']
        elif throw_one['value'] == 'paper':
            if throw_two['value'] == 'rock':
                self.round['winner'] = throw_one['player_id']
            elif throw_two['value'] == 'scissors':
                self.round['winner'] = throw_two['player_id']
        elif throw_one['value'] == 'scissors':
            if throw_two['value'] == 'paper':
                self.round['winner'] = throw_one['player_id']
            elif throw_two['value'] == 'rock':
                self.round['winner'] = throw_two['player_id']

        self.data['rounds'][self.round['id']] = self.round

        game_player_wins = {}
        for round_id, round in self.data['rounds'].items():
            if round['game_id'] != self.game_id:
                continue
            if round['tie']:
                continue

            round_winner = round['winner']
            if round_winner not in game_player_wins:
                game_player_wins[round_winner] = 0
            game_player_wins[round_winner] += 1

        rounds_to_win = int(self.game['round_limit']/2)
        for player_id, round_wins in game_player_wins.items():
            if round_wins > rounds_to_win:
                self.game['winner'] = player_id
                self.game['status'] = 'ended'
                break
        
        if self.game['winner'] == None:
            self._newGameRound()

    def _addLastThrowOption(self, options):
        if self.player['last_throw'] != None:
            options.append({
                'prompt': 'Get last throw results',
                'uri': 'game/throw-results',
                'qs': {
                    'last_throw': self.player['last_throw']
                }
            })
        return options

    def newPlayer(self):
        self._newPlayer()
        message = "Welcome {}!".format(self.player['name'])
        options = [
            CLIENT_OPTIONS['new_game'],
            CLIENT_OPTIONS['join_game']
        ]
        return {
            'message': message,
            'client_data': {
                'player_id': self.player_id
            },
            'client_options': options
        }

    def newGame(self):
        self._newGame()
        self._newGameRound()
        self.game['players'].append(self.player_id) # add player to game

        # TODO: add options?
        options = [
            CLIENT_OPTIONS['throw_play'],
            CLIENT_OPTIONS['game_status']
        ]

        return {
            'message': "New Game Created! (Game ID: {!s})".format(self.game_id),
            'client_data': {
                'game_id': self.game_id
            },
            'client_options': options
        }

    def joinGame(self):

        message = ""
        client_data = {}
        options = []

        join_game_id = self.request.getQsVar('join_game_id')
        
        if join_game_id == None:
            # available games
            available_games = self.getAvailableGames()
            if len(available_games) == 0:
                message = "The are no available games to join"
                options.append(CLIENT_OPTIONS['new_game'])
                options.append(CLIENT_OPTIONS['join_game'])
                return {
                    'message': message,
                    'client_options': options
                }
            else:
                message = "Choose a game to join"
                for game in available_games:
                    options.append({
                        'prompt': 'Join game: %s' % game['id'],
                        'uri': 'game/join',
                        'qs': {
                            'join_game_id': game['id']
                        }
                    })
                return {
                    'message': message,
                    'client_options': options
                }
        self.game_id = join_game_id
        self.game = self.data['games'][join_game_id]
        self.game['players'].append(self.player_id)
        if len(self.game['players']) > 1:
            self.game['status'] = 'active'
        
        message = "Joined game: %s" % (self.game_id)
        client_data['game_id'] = self.game_id
        options = [ # TODO: more options?
            CLIENT_OPTIONS['throw_play'],
            CLIENT_OPTIONS['game_status']
        ]
        return {
            'message': message,
            'client_data': client_data,
            'client_options': options,
        }

    def _getGameOverResponse(self):
        message = "GAME OVER - A victor has emerged."
        if self.game['winner'] == self.player_id:
            message += "\nYOU WON!"
        else:
            message += "\nYOU LOST!"
        message += "\n{!s} won the game.".format(self.data['players'][self.game['winner']]['name'])
        options = []
        options.append(CLIENT_OPTIONS['game_status'])
        options.append(CLIENT_OPTIONS['game_reset'])
        return {
            'message': message,
            'client_options': options,
        }

    def makeGameThrow(self):

        # check if the game status is 'active', if not show end game
        if self.game['status'] == 'ended':
            self.request.response.setStatus(HTTPStatus.BAD_REQUEST)
            return self._getGameOverResponse()

        # check for valid number of players before making throw
        if len(self.game['players']) < 2:
            self.request.response.setStatus(HTTPStatus.BAD_REQUEST)
            message = "ERROR: Please wait form the other player to join the game."
            options = [
                CLIENT_OPTIONS['throw_play'],
                CLIENT_OPTIONS['game_status']
            ]
            return {
                'message': message,
                'client_options': options,
            }

        # check if player has already made throw this round
        for throw_id, throw in self.data['throws'].items():
            if throw['round_id'] != self.round_id:
                continue
            if self.player_id == throw['player_id']:
                self.request.response.setStatus(HTTPStatus.BAD_REQUEST)
                message = "ERROR: You have already thrown a play this round."
                options = [
                    CLIENT_OPTIONS['throw_play']
                ]
                options = self._addLastThrowOption(options)
                options.append(CLIENT_OPTIONS['game_status'])
                return {
                    'message': message,
                    'client_options': options,
                }

        # check if client is trying to throw a new play
        player_throw = self.request.getQsVar('throw')
        if player_throw == None: # user wants to throw a play, needs client_options to do so
            return {
                'message': "Choose a play to throw:",
                'client_options': CLIENT_COMMON_PLAY_OPTIONS,
            }

        self._newThrow(player_throw)

        # check if game is over
        if self.game['status'] == 'ended':
            return self._getGameOverResponse()

        options = [
            CLIENT_OPTIONS['throw_play']
        ]
        options = self._addLastThrowOption(options)
        options.append(CLIENT_OPTIONS['game_status'])
        return {
            'message': "You threw: {}".format(player_throw),
            'client_options': options
        }

    def getGameStatus(self):
        message = "{!s}\nStatus: {!s}".format(self.game['name'], self.game['status'])
        if self.game['status'] == 'ended':
            message += "\nWinner: {!s}".format(self.data['players'][self.game['winner']]['name'])
        options = []

        # message += "{!s:.^50}".format(self.game['name'])
        message += "\n{!s:^10}{!s:<10}".format("Round", "Winner")
        message += "\nResults:"
        for round_id in self.game['rounds']:
            r = self.data['rounds'][round_id]
            if r['tie'] == True:
                message += "\n{!s:^10}{!s:<10}".format(r['order'], "Tie")
            else:
                if r['winner'] != None:
                    winner_player = self.data['players'][r['winner']]
                    winner_name = winner_player['name']
                    if winner_player['id'] == self.player_id:
                        winner_name += " (You)"
                    else:
                        winner_name += " (Opponent)"
                    message += "\n{!s:^10}{!s:<10}".format(r['order'], winner_name)
                else:
                    message += "\n{!s:^10}{!s:<10}".format(r['order'], "In Progress")
            if self.game['round_current'] == r['id']:
                if self.game['status'] == 'ended':
                    message += " (final)"
                else:
                    message += " (current)"
        


        if self.game['status'] == 'active':
            options.append(CLIENT_OPTIONS['throw_play'])
            options = self._addLastThrowOption(options)
        
        options.append(CLIENT_OPTIONS['game_status'])
        if self.game['status'] == 'ended':
            options.append(CLIENT_OPTIONS['game_reset'])
            if len(self.game['reset_request']) > 0:
                for pid in self.game['reset_request']:
                    message += "\n{} has requested to reset the game.".format(self.data['players'][pid]['name'])


        return {
            'message': message,
            'client_options': options
        }

    def getThrowResults(self):
        message = ""
        throw_id = self.request.getQsVar('last_throw')

        if throw_id not in self.data['throws'] or self.player['last_throw'] == None:
            return {
                "message": "The game was reset. This throw no longer exists.",
                'client_options': [
                    CLIENT_OPTIONS['throw_play'],
                    CLIENT_OPTIONS['game_status']
                ]
            }

        throw = self.data['throws'][throw_id]
        round = self.data['rounds'][throw['round_id']]
        game = self.data['games'][throw['game_id']]

        opp_throw = None
        opp_throw_id = None
        for round_throw_id in round['throws']:
            if round_throw_id != throw_id:
                opp_throw_id = round_throw_id
                break
        if opp_throw_id != None:
            opp_throw = self.data['throws'][opp_throw_id]

        round_winner = None
        if round['winner'] == None and round['tie'] == False:
            round_winner = 'Undetermined'
        elif round['tie'] == True:
            round_winner = 'TIE'
        elif round['winner'] != None:
            round_winner = self.data['players'][round['winner']]['name']
            if round['winner'] == self.player_id:
                round_winner += " (You)"
            else:
                round_winner += " (Opponent)"

        # message += "{!s:^50}\n".format("{} (ID: {})".format(game['name'], game['id']))
        # message += "{!s:.^50}\n".format("Throw Results")
        message += "{!s:<10}{!s}".format('Round:', round['order'])
        message += "\n{!s:<10}{!s}".format('Winner:', round_winner)
        message += "\n{!s:<10}{!s}".format('Value:', throw['value'])
        if opp_throw != None:
            message += "\n{!s:<10}{!s}".format('Opponent:', opp_throw['value'])
        else:
            message += "\n{!s:<10}{!s}".format('Opponent:', "Has NOT gone yet")
        
        options = []
        if self.game['status'] != 'ended':
            options.append(CLIENT_OPTIONS['throw_play'])
            # options = self._addLastThrowOption(options)
        options.append(CLIENT_OPTIONS['game_status'])
        if self.game['status'] == 'ended':
            options.append(CLIENT_OPTIONS['game_reset'])
        return {
            'message': message,
            'client_options': options
        }

    def _resetGame(self):
        thows_id_arr = list(self.data['throws'].keys())
        
        for throw_id in thows_id_arr:
            if self.data['throws'][throw_id]['game_id'] == self.game_id:
                self.data['throws'].pop(throw_id)

        for round_id in self.game['rounds']:
            self.data['rounds'].pop(round_id)

        new_game_data = {
            'name' : "Game {}".format(len(self.data['games'].keys())+1),
            'created_date': time.time(),
            'winner': None,
            'status': 'active',
            'round_limit': 3,
            'round_current': None,
            'rounds': [],
            'reset_request': []
        }

        for pid in self.game['players']:
            self.data['players']['last_throw'] = None
        self.player['last_throw'] = None

        self.game = {**self.game, **new_game_data}
        self._newGameRound()

    def resetGame(self):
        
        if self.player_id not in self.game['reset_request']:
            self.game['reset_request'].append(self.player_id)

        if len(self.game['reset_request']) > 1:
            self._resetGame()
            options = [
                CLIENT_OPTIONS['game_status'],
            ]
            return {
                'message': "Game has been reset!",
                'client_options': options
            }
        else:
            return {
                'message': "You have requested to reset the game.\nWaiting for other player to accept.",
                'client_options': [
                    CLIENT_OPTIONS['game_status']
                ]
            }

