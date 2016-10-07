Tic-Tac-Toe Game

Set Up Instructions:
1. Update the application ID on app.yaml to an ID you register on Google App Engine
2. Run the app on devserver using dev_appserver.py DIR in terminal
3. Create a new player using the create_player endpoint
4. Use create_game endpoint to create a game. Remeber to save the urlsafe_key for later use


Game Discription:

Tic-Tac-Toe is a simple game. There are 9 blocks on the board and players take turn to draw 'X' or 'O' on the block. The player who occupies 3 consecutive blocks(vertical, horizontal, or diagonal)

If the board is filled and neither of the players wins, it would count as a tie.
A win is 3 points; a tie is 1 point; a loss is 0 point.

Files:

    api.py: contains endpoints and the logic
    app.yaml: app configuration
    cron.yaml: cronjob configuration
    main.py: Handlers
    models: entity and Mssages definitions
    utils.py: helper functions

Endponts:

    cancel_game
    Path: 'game/{urlsafe_game_key}'
    Method: DELETE
    Parameters: urlsafe_game_key
    Returns: StringMessage
    Description: Deletes game provided with key. Game must not have finished yet.

    create_player
    Path: 'user'
    Method: POST
    Parameters: player_name
    Returns: Message confirming creation of the User.
    Description: Creates a new Player. user_name provided must be unique. Will raise a ConflictException if a Player with that player_name already exists.
    
    new_game
    Path: 'game'
    Method: POST
    Parameters: playerOne, playerTwo
    Returns: GameForm with initial game state.
    Description: Creates a new Game. playerOne and playerTwo are the names of the 'X' and 'O' player respectively.

    get_game
    Path: 'game/{urlsafe_game_key}'
    Method: GET
    Parameters: urlsafe_game_key
    Returns: GameForm with current game state.
    Description: Returns the current state of a game.

    make_move
    Path: 'game/{urlsafe_game_key}'
    Method: PUT
    Parameters: urlsafe_game_key, name, move
    Returns: GameForm with new game state.
    Description: Accepts a move and returns the updated state of the game. A move is a number from 0 - max index on board depending od board size, corresponding to one of the possible positions on the board. If this causes a game to end, a corresponding Score entity will be created.

    get_scores
    Path: 'scores'
    Method: GET
    Parameters: None
    Returns: ScoreForms.
    Description: Returns all Scores in the database (unordered).

    get_player_scores
    Path: 'scores/player/{name}'
    Method: GET
    Parameters: name
    Returns: ScoreForms.
    Description: Returns all Scores recorded by the provided player (unordered). Will raise a NotFoundException if the User does not exist.

    get_finished_games
    Path: 'games/finished_games'
    Method: GET
    Parameters: None
    Returns: StringMessage
    Description: Gets the number of games played from a previously cached memcache key.

    get_game_history
    Path: 'game/{urlsafe_game_key}/history'
    Method: GET
    Parameters: urlsafe_game_key
    Returns: StringMessage
    Description: Return a Game's move history.

    get_user_games
    Path: 'player/games'
    Method: GET
    Parameters: name, email
    Returns: GameForms
    Description: Return all Player's active games.

    get_player_rankings
    Path: 'player/ranking'
    Method: GET
    Parameters: None
    Returns: PlayerForms sorted by user points.
    Description: Return all Players ranked by their points.
