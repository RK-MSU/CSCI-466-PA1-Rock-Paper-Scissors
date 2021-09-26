# client

import os
from src.client import ClientRequest

class Client:

    playing_game = True
    user_input = None
    message = None
    client_data = {}
    client_options = {}

    client_request = None
    response_status = None
    response = None


    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.client_request = ClientRequest(self)

    def playGame(self):
        self.client_request.get(path='new/player')
        while self.playing_game:
            self.prompt()
            self.user_input = input("('q' to quit) > ")
            if self.user_input == 'q':
                self.playing_game = False
            else:
                self.handleUserInput()

    def setClientOptions(self, options):
        self.client_options = {}
        options_count = 1
        for option in options:
            self.client_options[str(options_count)] = option
            options_count += 1

    def prompt(self):
        os.system('clear')
        # print("Client Data: ", self.client_data)
        # print("Client Options: ", self.client_options)

        print('{!s:->50}\n{!s:<10}{!s}'.format('', 'Status:', self.response_status))
        print('{!s:->50}\n{!s}'.format('', self.message))
        print("{!s:->50}".format(''))
        for key, opt in self.client_options.items(): # TODO: error if 0 prompts
            print("{!s:<2}{!s:^3}{!s}".format(key, '-', opt['prompt']))
        
    def handleUserInput(self): # TODO: much error validation needs to be done here
        user_input = str(self.user_input)
        user_input_arr = user_input.split(' ')
        user_selection = user_input_arr[0]

        if user_selection not in self.client_options:
            # print("\nUser Input Selection Error\nUser Input:", user_selection,'\nClient Options:', self.client_options)
            return
            
        option_result = self.client_options[user_selection]

        req_qs = {}
        if 'qs' in option_result:
            req_qs = {**req_qs, **option_result['qs']}
            # for opt_qs_key, opt_qs_val in option_result['qs'].items():
            #     qs[opt_qs_key]=opt_qs_val
        req_qs = {**req_qs, **self.client_data}
        self.client_request.get(path=option_result['uri'], qs=req_qs)

if __name__ == '__main__':
    c = Client()
    c.playGame()