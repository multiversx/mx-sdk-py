from typing import Sequence


class PartsHolder:
    """
    PartsHolder holds data parts (e.g. raw contract call arguments, raw contract return values).
    It allows one to easily construct parts (thus functioning as a builder of parts).
    It also allows one to focus on a specific part to read from (thus functioning as a reader of parts: think of a pick-up head).
    Both functionalities (building and reading) are kept within this single abstraction, for convenience.
    """

    def __init__(self, parts: Sequence[bytes]):
        """
        Creates a new PartsHolder, which has the given parts.
        Focus is on the first part, if any, or "beyond the last part" otherwise.
        """

        self.parts = list(parts)
        self.focused_part_index = 0

    def get_parts(self) -> list[bytes]:
        return self.parts

    def get_num_parts(self) -> int:
        return len(self.parts)

    def get_part(self, index: int) -> bytes:
        if index >= self.get_num_parts():
            raise IndexError(f"part index {index} is out of range")
        return self.parts[index]

    def append_to_last_part(self, data: bytes):
        if not self.has_any_part():
            raise ValueError("cannot write, since there is no part to write to")
        self.parts[-1] += data

    def has_any_part(self) -> bool:
        return len(self.parts) > 0

    def append_empty_part(self):
        self.parts.append(b"")

    def read_whole_focused_part(self):
        """
        Reads the whole focused part, if any. Otherwise, it returns an error.
        """

        if self.is_focused_beyond_last_part():
            raise ValueError(f"cannot wholly read part {self.focused_part_index}: unexpected end of data")
        return self.get_part(self.focused_part_index)

    def focus_on_next_part(self):
        """
        Focuses on the next part, if any. Otherwise, it returns an error.
        """

        if self.is_focused_beyond_last_part():
            raise ValueError(
                f"cannot focus on next part, since the focus is already beyond the last part; focused part index is {self.focused_part_index}"
            )
        self.focused_part_index += 1

    def is_focused_beyond_last_part(self):
        """
        Returns true if the focus is already beyond the last part.
        """

        return self.focused_part_index >= self.get_num_parts()
