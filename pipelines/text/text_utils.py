import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.converters import bytes_to_bits, bits_to_bytes

# ZWC Constants
ZERO = '\u200B'
ONE  = '\u200C'

def bits_to_zwc(bits: list[int]) -> str:
    """Converts a list of 0s and 1s into Zero-Width Characters."""
    return "".join(ONE if b == 1 else ZERO for b in bits)

def zwc_to_bits(text: str) -> list[int]:
    """Extracts bits exclusively from Zero-Width Characters in a string."""
    bits = []
    for char in text:
        if char == ZERO:
            bits.append(0)
        elif char == ONE:
            bits.append(1)
    return bits
