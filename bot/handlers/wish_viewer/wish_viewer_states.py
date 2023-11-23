from enum import IntEnum

from bot.utilities.id_generator import next_state_id


class WishViewerStates(IntEnum):
    ASK_FOR_USERNAME = next_state_id()
    RESERVATION = next_state_id(),
    BACK = next_state_id()
