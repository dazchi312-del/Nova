import numpy as np
import matplotlib.pyplot as plt

# Parameters
N = 30  # number of draws per trial
n_trials = 10000  # number of trials
mu_true = 1.0  # true mean
sigma_true = 1.0  # true standard deviation (for exponential distribution)
lambda_true = 1.0  # rate parameter for exponential distribution

# Generate samples and compute empirical statistics
samples = np.random.exponential(scale=1/lambda_true, size=(n_trials, N))
sample_means = np.mean(samples, axis=1)

empirical_mean = np.mean(sample_means)
empirical_std = np.std(sample_means)

# Theoretical predictions
theoretical_mean = mu_true
theoretical_std = sigma_true / np.sqrt(N)

# Compute errors
abs_error_empirical_mean = abs(empirical_mean - theoretical_mean)
rel_error_empirical_mean = abs_error_empirical_mean / theoretical_mean * 100

abs_error_empirical_std = abs(empirical_std - theoretical_std)
rel_error_empirical_std = abs_error_empirical_std / theoretical_std * 100

print(f"Absolute error of empirical mean: {abs_error_empirical_mean}")
print(f"Relative error of empirical mean: {rel_error_empirical_mean}%")
print(f"Absolute error of empirical standard deviation: {abs_error_empirical_std}")
print(f"Relative error of empirical standard deviation: {rel_error_empirical_std}%")

if rel_error_empirical_mean < 5 and rel_error_empirical_std < 5:
    print("PASS")
else:
    print("FAIL")
    print(f"The empirical mean's relative error is {rel_error_empirical_mean}%, which is above 5%. The empirical standard deviation's relative error is {rel_error_empirical_std}%, which is also above 5%.")

# Plot histogram of sample means
plt.hist(sample_means, bins=50, density=True)
plt.xlabel('Sample Mean')
plt.ylabel('Probability Density')
plt.title(f'Histogram of Sample Means (N={N}, Trials={n_trials})')
plt.savefig('output.png')

print("Plot saved to output.png")