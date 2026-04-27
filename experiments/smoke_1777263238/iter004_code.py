import numpy as np
import matplotlib.pyplot as plt

def test_clt_hypothesis():
    # Parameters
    num_trials = 10000
    sample_size = 30
    true_mean = 1.0
    true_std = 1.0

    # Generate data and compute sample means
    samples = np.random.exponential(scale=1/true_mean, size=(num_trials, sample_size))
    sample_means = np.mean(samples, axis=1)

    # Compute empirical statistics
    empirical_mean = np.mean(sample_means)
    empirical_std = np.std(sample_means)

    # Theoretical predictions
    theoretical_mean = true_mean
    theoretical_std = true_std / np.sqrt(sample_size)

    # Print errors and pass/fail message
    abs_error_mean = np.abs(empirical_mean - theoretical_mean)
    rel_error_mean = abs_error_mean / theoretical_mean * 100
    abs_error_std = np.abs(empirical_std - theoretical_std)
    rel_error_std = abs_error_std / theoretical_std * 100

    print(f"Absolute error in sample mean: {abs_error_mean:.4f}")
    print(f"Relative error in sample mean: {rel_error_mean:.2f}%")
    print(f"Absolute error in sample std: {abs_error_std:.4f}")
    print(f"Relative error in sample std: {rel_error_std:.2f}%")

    if rel_error_mean < 5 and rel_error_std < 5:
        print("PASS")
    else:
        print("FAIL")
        print(f"Mean: {abs_error_mean:.4f} ({rel_error_mean:.2f}%)")
        print(f"Std: {abs_error_std:.4f} ({rel_error_std:.2f}%)")

    # Plot histogram of sample means
    plt.hist(sample_means, bins=30, density=True)
    x = np.linspace(theoretical_mean - 3*theoretical_std, theoretical_mean + 3*theoretical_std, 100)
    y = np.exp(-(x-theoretical_mean)**2 / (2 * theoretical_std**2)) / (np.sqrt(2*np.pi) * theoretical_std)
    plt.plot(x, y, 'r-', lw=2)
    plt.title('Histogram of Sample Means')
    plt.xlabel('Mean')
    plt.ylabel('Probability Density')
    plt.savefig('output.png')

test_clt_hypothesis()