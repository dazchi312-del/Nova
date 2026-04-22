import numpy as np
import matplotlib.pyplot as plt
import math
import random
import collections
import itertools

# Function to check if a number is prime
def is_prime(n):
    """Check if number is prime"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Generate a sequence of prime numbers up to 'n'
def generate_primes(n):
    """Generate sequence of primes up to 'n'"""
    return [i for i in range(2, n) if is_prime(i)]

# Auditory Feedback using Beep (for Windows)
import winsound
def beep(frequency=2500, duration=1000):
    """Produce a beep sound for auditory feedback"""
    winsound.Beep(frequency, duration)

# Main Function to Explore Prime Number Sequences and Harmonic Frequencies
def explore_primes_and_harmonics():
    """Explore relationship between prime numbers and harmonic frequencies"""
    max_num = 100  # Upper limit for generating primes
    primes = generate_primes(max_num)
    
    # Calculate corresponding harmonic frequencies (assuming base frequency of 440 Hz)
    frequencies = [440 * p / min(primes) for p in primes]
    
    # Print Statements for Output
    print("Generated Prime Numbers:", primes[:5], "...", ["Total:", len(primes)])
    print("Corresponding Harmonic Frequencies (Hz):", frequencies[:5], "...")

    # Auditory Feedback - Beep for each prime found (demo: first 5 primes)
    for p, f in list(zip(primes, frequencies))[:5]:
        beep(int(f), 500)  # Adjust frequency and duration as needed
        print(f"Prime: {p}, Frequency: {f:.2f} Hz")
    
    # Visualization
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(primes, marker='o', linestyle='-')
    plt.title('Prime Number Sequence up to {}'.format(max_num))
    plt.xlabel('Index')
    plt.ylabel('Prime Value')  # Completed ylabel
    
    plt.subplot(1, 2, 2)
    plt.plot(frequencies, marker='o', linestyle='-')
    plt.title('Harmonic Frequencies Corresponding to Primes')
    plt.xlabel('Index (Matching Prime Sequence)')
    plt.ylabel('Frequency (Hz)')  # Enhanced Visualization with Second Plot
    
    plt.tight_layout()
    plt.savefig('prime_harmonics_output.png')
    plt.close()

# Execute Main Function
if __name__ == "__main__":
    explore_primes_and_harmonics()