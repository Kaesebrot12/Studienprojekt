import numpy as np
from reedsolo import RSCodec


#####################################################################################################################################################################################################################################################################
# Konfigurationswerte
#####################################################################################################################################################################################################################################################################

BLOCK_SIZE = 8  # Blockgröße für das Interleaving
ECC_SYMBOLS = 10  # Länge der Fehlerkorrekturbits
HAMMING_BIT_LENGTH = 4  # Länge der Bits, die in der Hamming-Codierung verwendet werden
HAMMING_ENCODED_BIT_LENGTH = 7  # Länge der codierten Bits in der Hamming-Codierung


#####################################################################################################################################################################################################################################################################

#####################################################################################################################################################################################################################################################################




#####################################################################################################################################################################################################################################################################
# Fehlerschutz
#####################################################################################################################################################################################################################################################################

def hamming_encode(bits):
     # Ensure data is a multiple of 4 bits
    assert len(bits) % HAMMING_BIT_LENGTH == 0

    encoded_data = []

    for i in range(0, len(bits), HAMMING_BIT_LENGTH):
        # Extract 4 bits
        bit_group = bits[i:i+4]

        # Calculate parity bits
        p1 = bit_group[0] ^ bit_group[1] ^ bit_group[3]
        p2 = bit_group[0] ^ bit_group[2] ^ bit_group[3]
        p3 = bit_group[1] ^ bit_group[2] ^ bit_group[3]

        # Append parity bits and data bits to encoded data
        encoded_data.extend([p1, p2, bit_group[0], p3, bit_group[1], bit_group[2], bit_group[3]])
    return encoded_data

def hamming_decode(encoded_bits):
    # Ensure data is a multiple of 7 bits
    assert len(encoded_bits) % HAMMING_ENCODED_BIT_LENGTH == 0

    decoded_data = []

    for i in range(0, len(encoded_bits), HAMMING_ENCODED_BIT_LENGTH):
        # Extract 7 bits
        bit_group = encoded_bits[i:i+7]

        # Calculate parity bits
        p1 = bit_group[0] ^ bit_group[2] ^ bit_group[4] ^ bit_group[6]
        p2 = bit_group[0] ^ bit_group[3] ^ bit_group[4] ^ bit_group[6]
        p3 = bit_group[1] ^ bit_group[2] ^ bit_group[3] ^ bit_group[4]

        # If parity bits do not match, there was an error in transmission
        if p1 != bit_group[0] or p2 != bit_group[1] or p3 != bit_group[3]:
            raise ValueError("Hamming decode error")

        # Append data bits to decoded data
        decoded_data.extend(bit_group[2:6])

    return ''.join(str(bit) for bit in decoded_data)

def interleave(data,):
    # Ensure data is a multiple of block size
    assert len(data) % BLOCK_SIZE == 0

    # Create an empty list to hold the interleaved data
    interleaved_data = []

    # Split the data into blocks
    blocks = [data[i:i+BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]

    # Interleave the data
    for i in range(BLOCK_SIZE):
        for block in blocks:
            interleaved_data.append(block[i])

    return ''.join(interleaved_data)

def deinterleave(data):
    # Ensure data is a multiple of block size
    assert len(data) % BLOCK_SIZE == 0

    # Create an empty list to hold the deinterleaved data
    deinterleaved_data = [''] * BLOCK_SIZE

    # Split the data into blocks
    blocks = [data[i:i+BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]

    # Deinterleave the data
    for i, block in enumerate(blocks):
        for j in range(BLOCK_SIZE):
            deinterleaved_data[j] += block[j]

    return ''.join(deinterleaved_data)

def reed_solomon_encode(data):
    rs = RSCodec(ECC_SYMBOLS)  # 10 is the number of ECC symbols
    encoded_data = rs.encode(data)
    return encoded_data

def reed_solomon_decode(data):
    rs = RSCodec(ECC_SYMBOLS)
    decoded_data = rs.decode(data)
    return decoded_data


#####################################################################################################################################################################################################################################################################
#####################################################################################################################################################################################################################################################################




#####################################################################################################################################################################################################################################################################
# Modulation
#####################################################################################################################################################################################################################################################################


def qam_modulate(data, carrier_freq, sample_rate, use_hamming=False, use_reed_solomon=False, use_interleaving=False):

    # Convert data to bits
    bits = ''.join(format(ord(i), '08b') for i in data)

    if use_hamming:
        bits = hamming_encode(bits)
  #  if use_reed_solomon:
   #     bits = reed_solomon_encode(bits)
    if use_interleaving:
        bits = interleave(bits)


    # Group bits into symbols
    n = 4  # 4 bits per symbol for 16-QAM
    symbols = [bits[i:i+n] for i in range(0, len(bits), n)]

    # Convert symbols to complex numbers
    constellation = np.array([-3-3j, -3-1j, -3+3j, -3+1j, -1-3j, -1-1j, -1+3j, -1+1j, 3-3j, 3-1j, 3+3j, 3+1j, 1-3j, 1-1j, 1+3j, 1+1j])
    points = [constellation[int(symbol, 2)] for symbol in symbols]

    # Modulate the signal
    t = np.arange(0, len(points) / carrier_freq, 1 / sample_rate)
    signal = np.concatenate([np.real(point) * np.cos(2 * np.pi * carrier_freq * t[i:i+int(sample_rate/carrier_freq)]) - np.imag(point) * np.sin(2 * np.pi * carrier_freq * t[i:i+int(sample_rate/carrier_freq)]) for i, point in enumerate(points)])

    return signal
#####################################################################################################################################################################################################################################################################
#####################################################################################################################################################################################################################################################################


    
#####################################################################################################################################################################################################################################################################
# Demodulation
#####################################################################################################################################################################################################################################################################
def qam_demodulate(signal, carrier_freq, sample_rate, use_hamming=False, use_reed_solomon=False, use_interleaving=False):
    # Define the constellation
    constellation = np.array([-3-3j, -3-1j, -3+3j, -3+1j, -1-3j, -1-1j, -1+3j, -1+1j, 3-3j, 3-1j, 3+3j, 3+1j, 1-3j, 1-1j, 1+3j, 1+1j])

    # Demodulate the signal
    t = np.arange(0, len(signal) / carrier_freq, 1 / sample_rate)
    points = [signal[i:i+int(sample_rate/carrier_freq)] * np.exp(-2j * np.pi * carrier_freq * t[i:i+int(sample_rate/carrier_freq)]) for i in range(0, len(signal), int(sample_rate/carrier_freq))]

    # Convert points to symbols
    symbols = [np.argmin([np.abs(point - c) for c in constellation]) for point in np.mean(points, axis=1)]

    # Convert symbols to bits
    bits = ''.join(format(symbol, '04b') for symbol in symbols)

    # If using error correction, decode the bits
    if use_interleaving:
        bits = deinterleave(bits)
  #  if use_reed_solomon:
        #bits = reed_solomon_decode(bits)
    if use_hamming:
        bits = hamming_decode(bits)

    # Convert bits to data
    data = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

    return data
#####################################################################################################################################################################################################################################################################
#####################################################################################################################################################################################################################################################################
