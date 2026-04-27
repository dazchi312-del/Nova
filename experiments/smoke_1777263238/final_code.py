import numpy as np
import matplotlib.pyplot as plt

# Set seed for reproducibility
np.random.seed(0)

# Number of trials
num_trials = 10000

# Sample size (N)
sample_size = 30

# True parameters
true_mean = 1.0
true_rate = 1.0

# Theoretical predictions
theoretical_std_sample_mean = true_rate / np.sqrt(sample_size)

# Generate samples and compute sample means
samples = np.random.exponential(scale=1.0 / true_rate, size=(num_trials, sample_size))
sample_means = np.mean(samples, axis=1)

# Compute empirical mean and standard deviation of sample means
empirical_mean_sample_mean = np.mean(sample_means)
empirical_std_sample_mean = np.std(sample_means)

# Calculate errors
abs_error_empirical_mean = abs(empirical_mean_sample_mean - true_mean)
rel_error_empirical_mean = abs_error_empirical_mean / true_mean * 100

abs_error_empirical_std = abs(empirical_std_sample_mean - theoretical_std_sample_mean)
rel_error_empirical_std = abs_error_empirical_std / theoretical_std_sample_mean * 100

print("Absolute error in empirical mean: ", abs_error_empirical_mean)
print("Relative error in empirical mean: ", rel_error_empirical_mean, "%")
print("Absolute error in empirical std: ", abs_error_empirical_std)
print("Relative error in empirical std: ", rel_error_empirical_std, "%")

if rel_error_empirical_mean < 5 and rel_error_empirical_std < 5:
    print('PASS')
else:
    print('FAIL')

# Plot histogram of sample means
plt.hist(sample_means, bins=50, density=True)
x = np.linspace(0.7, 1.3, 100)
plt.plot(x, np.exp(-x) / (true_rate * true_mean), 'r', lw=2)
plt.title('Histogram of Sample Means')
plt.xlabel('Sample Mean')
plt.ylabel('Frequency')
plt.savefig('output.png')

print("Plot saved as output.png")