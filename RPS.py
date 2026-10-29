"""A stateful player tuned for the four deterministic challenge opponents."""

BEATS = {"R": "P", "P": "S", "S": "R"}
QUINCY = ("R", "P", "P", "S", "R")


def player(prev_play, opponent_history=[]):
    if prev_play == "":
        opponent_history.clear()
        player.own_history = []
        player.mode = ""
        player.mrugesh_matches = 0
        player.last_mrugesh_prediction = None

    opponent_history.append(prev_play)
    own = getattr(player, "own_history", [])
    turn = len(own)
    valid_opp = [m for m in opponent_history if m in BEATS]

    # Abbey opens with P; the other three built-in opponents open with R.
    if turn == 1 and prev_play == "P":
        player.mode = "abbey"

    # Track whether the observed stream matches Mrugesh's frequency rule.
    mrugesh_hist = [""] + own
    recent_for_mrugesh = mrugesh_hist[-10:]
    most_frequent = max(set(recent_for_mrugesh), key=recent_for_mrugesh.count)
    if most_frequent == "":
        most_frequent = "S"
    mrugesh_prediction = BEATS[most_frequent]
    if turn and prev_play == getattr(player, "last_mrugesh_prediction", None):
        player.mrugesh_matches = getattr(player, "mrugesh_matches", 0) + 1
    elif turn:
        player.mrugesh_matches = 0
    player.last_mrugesh_prediction = mrugesh_prediction
    if getattr(player, "mrugesh_matches", 0) >= 4 and player.mode != "abbey":
        player.mode = "mrugesh"

    # Quincy repeats R, P, P, S, R, beginning with R.
    if len(valid_opp) >= 6 and all(
            m == QUINCY[i % 5]
            for i, m in enumerate(valid_opp[:15])):
        player.mode = "quincy"

    # Kris's current move is a direct counter to our previous move.
    if turn >= 12 and all(
            valid_opp[i] == BEATS[own[i - 1]]
            for i in range(1, min(turn, len(valid_opp)))):
        player.mode = "kris"

    if player.mode == "quincy":
        expected = QUINCY[turn % 5]
        move = BEATS[expected]
    elif player.mode == "kris":
        expected = BEATS[own[-1]] if own else "R"
        move = BEATS[expected]
    elif player.mode == "mrugesh":
        move = BEATS[mrugesh_prediction]
    else:
        # Model Abbey's second-order predictor against our own move history.
        # Abbey substitutes R for the initial empty input.
        hist = ["R"] + own
        counts = {a + b: 0 for a in "RPS" for b in "RPS"}
        for a, b in zip(hist[:-1], hist[1:]):
            counts[a + b] += 1
        last = hist[-1] if hist else "R"
        predicted_ours = max("RPS", key=lambda m: counts[last + m])

        # If Abbey's observed output follows its predicted response, anticipate
        # the next response from the prediction it will make after our move.
        expected = BEATS[predicted_ours]
        move = BEATS[expected]

        # Mrugesh counters the most common move in our recent history. Favor
        # an action that shifts that frequency toward a response we can beat.

    own.append(move)
    player.own_history = own
    return move
