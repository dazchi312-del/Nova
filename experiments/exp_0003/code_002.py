import numpy as np
import matplotlib.pyplot as plt
import math
import random
from collections import OrderedDict
import itertools

# Function to check if a number is prime
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Generate prime numbers up to user-defined limit
def get_primes(limit):
    primes = []
    for num in range(2, limit+1):
        if is_prime(num):
            primes.append(num)
    return primes

# Map prime numbers to frequencies (user-defined mapping function)
def freq_mapping(prime, func='linear'):
    if func == 'linear':
        return prime * 100  # Simple linear mapping
    elif func == 'exponential':
        return math.pow(2, prime) * 100  # Exponential mapping
    else:
        raise ValueError("Invalid mapping function. Choose 'linear' or 'exponential'.")

# Auditory Feedback (Simple Beep Representation)
def beep(frequency, duration=1):
    print(f"Beep at {frequency} Hz for {duration} second(s)")

# Main Program
if __name__ == "__main__":
    # User-defined parameters
    prime_limit = 20
    mapping_func = 'linear'

    primes = get_primes(prime_limit)
    freqs = [freq_mapping(p, mapping_func) for p in primes]

    # Visual Representation
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(primes, marker='o')
    plt.title('Prime Numbers up to {}'.format(prime_limit))
    plt.xlabel('Index')
    plt.ylabel('Prime Number')

    plt.subplot(1, 2, 2)
    plt.plot(freqs, marker='o')
    plt.title('Mapped Frequencies using {}'.format(mapping_func.capitalize()))
    plt.xlabel('Index (Matching Prime)')
    plt.ylabel('Frequency (Hz)')
    
    plt.tight_layout()
    plt.savefig('output.png')
    plt.close()

    # Auditory Feedback
    for prime, freq in zip(primes, freqs):
        print(f"Prime: {prime}, Frequency: {freq} Hz")
        beep(freq)  # Simple text representation of beeps; actual audio output not possible without additional libraries/extensions