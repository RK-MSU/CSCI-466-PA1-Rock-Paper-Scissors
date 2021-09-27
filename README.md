# CSCI-466: PA 1 - Rock Paper Scissors Client-Server Application
*Programming Assignment 1: Rock Paper Scissors Client-Server Application* - CSCI-466 Networks - Fall 2021 - Montana State University

## Client

The client will make HTTP request in the following template format: _**http://`<HOST>`:`<PORT>`/`<URI>`?`<QUERY_STRING>`**_

| `<Key>` | Value |
| :--: | :--: |
| `<HOST>` | _localhost_ |
| `<PORT>` | _8000_ |
| `<URI>` | _make/play_ |
| `<QUERY_STRING>` | _player_id=45JKL89_ |

The resulting URL would look like: `http://localhost:8000/make/play?player_id=45JKL89`.

> **Note**: The `URI` will determine what actions the server will make.

### ClientRequest and Prompt

The client is "server-event" driven. When the client receives a response from the server, this response has certain information to tell the client what to do next.

**Server Response Data Format**

    {
        'client_data': {
            'player_id': player['id']
        },
        'client_options': {
            {
                'prompt': 'Game: SJ790JHKP:',
                'uri': 'game/join',
                'qs': {
                    'game_id': SJ790JHKP
                }
            }
        
        },
        'message': "Choose a game to join."
    }

- `message` (String): Basically a message that is displayed to the client before the user input prompt is provided.
- [`client_options`](#client_options) (Dictionary): Consider this an application object. It contains the necessary information for the client to make a choice from an options list, which in-turn translates a server request.
- `client_data` (Dictionary): Think of this like cache in a web browser. This information is included in the query string of each server request to help identify the client to the server.
  - There are two possible fields:
    - `player_id`: Identifies the unique player
    - `game_id`: Identifies the unique game

#### `client_options`

A specific option in the list of `client_options` may look like:

    {
       'prompt': 'Join Game'
       'uri': 'game/join'
       'qs': {
          'game_id': 'ASD890AJKL'
       }
    }

- `prompt`: The text that is displayed as a label for the individual option
- `uri`: The designated URI path segments to generate a server request for the specific option
  - Remember the `<URI>` path segments are significant, the tell the server what exactly the client is requesting.
- `qs`: Addition query string variables to be merged if the specific option is selected.
  - For example, if the client is prompted to join a game, from a list of available games, the selected options needs to contain information to identify which games was selected, this is how this is done.
