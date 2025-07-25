# ai/state_tracker.py

class StateTracker:
    def __init__(self):
        self.last_position = None  # "LONG" or "SHORT"
        self.candle_hold = 0       # Neçə candle-dır mövqe açıqdır
        self.cooldown_required = 3 # Minimum candle sayı mövqe bağlanmadan öncə

    def update_position(self, position: str):
        if position == self.last_position:
            self.candle_hold += 1
        else:
            self.last_position = position
            self.candle_hold = 1

    def get_position(self) -> str:
        return self.last_position or "NONE"

    def can_close_position(self) -> bool:
        return self.candle_hold >= self.cooldown_required

    def reset(self):
        self.last_position = None
        self.candle_hold = 0
