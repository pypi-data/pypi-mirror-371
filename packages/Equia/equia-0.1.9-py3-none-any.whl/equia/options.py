""" `options`

Allowable specifications for flash calculations.
"""

from enum import Enum

class ToStrEnum(str, Enum):
    """Enum whose values are always strings, and which can validate+return .value."""
    @classmethod
    def to_str(cls, val: "ToStrEnum") -> str:
        # will raise if val isn’t a valid member
        return cls(val).value

class VolumeType(ToStrEnum):
    """Allowable volume calculation specifications: `{'Auto', 'Liquid', 'Vapor'}`."""
    Auto = 'Auto'
    Liquid = 'Liquid'
    Vapor = 'Vapor'
