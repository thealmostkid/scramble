# POST /login: redirects to /lobby/userid
# GET /lobby/userid returns lobby.js code for that userid.

# lobby.js:
# Prints "Hello.  Waiting for the puzzles to start...".  Polls /lobby/userid
# /lobby/userid returns empty or gameid

# ADMIN option of who is puzzle solver
# random, rotate, earned
# requirements: 1) all partipants are registered 2) all groups ready (ADMIN)
