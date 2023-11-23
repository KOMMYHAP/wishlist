from enum import IntEnum

from bot.utilities.id_generator import next_state_id


class WishEditStates(IntEnum):
    TITLE = next_state_id(),
    HINT = next_state_id(),
    REFERENCES = next_state_id(),
    COST = next_state_id(),
    ABORT = next_state_id(),
    COMPLETION = next_state_id()
