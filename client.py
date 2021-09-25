# client

import os
from src.client import ClientRequest

class Client:

    playing_game = True
    user_input = None
    client_data = {}
    client_options = {}
    message = None

    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.client_req = ClientRequest(self)
        self.client_req.get(path='new/player')

    def playGame(self):

        while self.playing_game:
            self.prompt()
            self.user_input = input("('q' to quit) > ")
            if self.user_input == 'q':
                self.playing_game = False
            else:
                self.handleUserInput()

    def prompt(self):
        os.system('clear')

        print("Client Data: ", self.client_data)
        print("Client Options: ", self.client_options)

        if self.message != None:
            print('\n%s' % (self.message))
        for i, opt in enumerate(self.client_options): # TODO: error if 0 prompts
            print("{} - {}".format(i+1, opt['prompt']))
        
    def handleUserInput(self): # TODO: much error validation needs to be done here

        user_i = str(self.user_input)
        user_i_action = None

        if len(user_i) == 0:
            print('No input received')
            return

        if len(user_i) == 1:
            user_i = int(user_i)-1
        elif ' ' in user_i:
            space_index = user_i.index(' ')
            user_i_action = user_i[space_index+1:]
            user_i = int(user_i[0:space_index])
        else:
            print('Error')
            return

        # TODO: Error detection
        option_result = self.client_options[user_i]
        req_qs = self.client_data

        if user_i_action != None:
            req_qs['action_value'] = user_i_action

        if 'qs' in option_result.keys():
            req_qs = {**option_result['qs'], **req_qs}

        self.client_req.get(path=option_result['uri'], qs=req_qs)



if __name__ == '__main__':
    c = Client()
    c.playGame()