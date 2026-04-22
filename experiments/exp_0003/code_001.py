import numpy as np
import matplotlib.pyplot as plt
import math
import random
import collections

# Function to check if a number is prime
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Generate prime numbers up to a limit
limit = 1000
primes = [i for i in range(2, limit) if is_prime(i)]

# Map prime numbers to musical frequencies (simple linear mapping for demonstration)
frequencies = [440 * (prime / min(primes)) for prime in primes]

# Audio-Visual Representation: Plot distribution pattern of primes and their mapped frequencies
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.scatter(range(len(primes)), primes, s=2, c='blue', alpha=0.5)
plt.title('Prime Number Distribution')
plt.xlabel('Index')
plt.ylabel('Prime Number Value')

plt.subplot(1, 2, 2)
plt.scatter(range(len(frequencies)), frequencies, s=2, c='red', alpha=0.5)
plt.title('Mapped Musical Frequencies')
plt.xlabel('Index (Matching Prime Index)')
plt.ylabel('Frequency (Hz)')

plt.tight_layout()
plt.savefig('prime_frequencies_output.png')
plt.close()

# Print statements for a glimpse into the data
print("First 10 Primes:", primes[:10])
print("Mapped Frequencies for First 10 Primes:", frequencies[:10])
print("Total Primes Found Under", limit, ":", len(primes))