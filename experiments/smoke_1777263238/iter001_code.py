import numpy as np
import matplotlib.pyplot as plt

# Set seed for reproducibility
np.random.seed(0)

# Parameters of the exponential distribution
mu = 1.0
sigma = 1.0

# Sample size
N = 30

# Number of trials
num_trials = 10000

# Initialize arrays to store sample means
sample_means = np.zeros(num_trials)

# Generate trial sample means and compute empirical mean and std
for i in range(num_trials):
    # Draw N samples from the exponential distribution
    samples = np.random.exponential(scale=sigma, size=N)
    
    # Compute the sample mean
    sample_mean = np.mean(samples)
    
    # Store the sample mean
    sample_means[i] = sample_mean

# Compute empirical mean and std of the 10000 sample means
empirical_mean = np.mean(sample_means)
empirical_std = np.std(sample_means)

# Compute theoretical predictions
theoretical_mean = mu
theoretical_std = sigma / np.sqrt(N)

# Print absolute and relative errors for both
print(f"Absolute error in empirical mean: {np.abs(empirical_mean - theoretical_mean)}")
print(f"Relative error in empirical mean: {np.abs((empirical_mean - theoretical_mean) / theoretical_mean) * 100}%")
print(f"Absolute error in empirical std: {np.abs(empirical_std - theoretical_std)}")
print(f"Relative error in empirical std: {np.abs((empirical_std - theoretical_std) / theoretical_std) * 100}%")

# Print pass/fail message
if np.abs((empirical_mean - theoretical_mean) / theoretical_mean) * 100 < 5 and np.abs((empirical_std - theoretical_std) / theoretical_std) * 100 < 5:
    print('PASS')
else:
    print('FAIL')
    
    # Store offending values in a dictionary
    offending_values = {
        'Empirical mean': empirical_mean,
        'Theoretical mean': theoretical_mean,
        'Relative error in empirical mean': np.abs((empirical_mean - theoretical_mean) / theoretical_mean) * 100,
        'Empirical std': empirical_std,
        'Theoretical std': theoretical_std,
        'Relative error in empirical std': np.abs((empirical_std - theoretical_std) / theoretical_std) * 100
    }
    
    # Print offending values
    for key, value in offending_values.items():
        print(f"{key}: {value}%")

# Plot histogram of sample means
plt.hist(sample_means, bins=50, density=True)
plt.xlabel('Sample Mean')
plt.ylabel('Frequency')
plt.title('Histogram of Sample Means')
plt.savefig('output.png')

print("Plot saved as output.png")