_state_id = 0


def next_state_id():
    global _state_id
    _state_id += 1
    return _state_id
