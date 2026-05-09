def bytes_to_bits(data: bytes) -> list[int]:
    """
    Converts a sequence of bytes into a list of bits (0s and 1s).
    Bits are ordered starting from the Most Significant Bit (MSB).
    Example: 0xE9 -> [1, 1, 1, 0, 1, 0, 0, 1]
    """
    bits = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits

def bits_to_bytes(bits: list[int]) -> bytes:
    """
    Converts a list of bits (0s and 1s) back into a sequence of bytes.
    Requires the length of the list to be a multiple of 8.
    """
    if len(bits) % 8 != 0:
        raise ValueError("Bit length must be a multiple of 8.")

    bytes_out = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        bytes_out.append(byte)

    return bytes(bytes_out)
