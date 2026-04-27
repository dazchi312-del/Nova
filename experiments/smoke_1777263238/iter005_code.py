import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def test_clt_hypothesis(distribution_type, n_samples=30, n_trials=10000):
    # Generate N trials of sample means from the specified distribution
    if distribution_type == 'exponential':
        lambda_param = 1.0
        true_mean = 1.0
        true_std = 1.0
        empirical_dist = stats.expon(scale=lambda_param)
    elif distribution_type in ['normal', 't']:
        mean = np.random.uniform(0, 10)  # random mean between 0 and 10
        std = np.random.uniform(0.1, 2.5)  # random std between 0.1 and 2.5
        empirical_dist = stats.norm(loc=mean, scale=std)
    else:
        raise ValueError("Invalid distribution type")

    sample_means = []
    for _ in range(n_trials):
        samples = empirical_dist.rvs(size=n_samples)
        sample_mean = np.mean(samples)
        sample_means.append(sample_mean)

    # Compute empirical mean and std of the 10000 sample means
    empirical_mean = np.mean(np.array(sample_means))
    empirical_std = np.std(np.array(sample_means))

    # Theoretical predictions for N=30 draws from an exponential distribution with lambda=1.0
    theoretical_mean = true_mean
    theoretical_std = true_std / np.sqrt(n_samples)

    # Print absolute and relative error for both against the theoretical predictions
    print(f"Empirical mean: {empirical_mean:.4f}")
    print(f"Theoretical mean: {theoretical_mean:.4f}")
    print(f"Absolute error (mean): {abs(empirical_mean - theoretical_mean):.6f}")
    print(f"Relative error (mean): {(abs(empirical_mean - theoretical_mean) / theoretical_mean)*100:.2f}%")

    print(f"Empirical std: {empirical_std:.4f}")
    print(f"Theoretical std: {theoretical_std:.4f}")
    print(f"Absolute error (std): {abs(empirical_std - theoretical_std):.6f}")
    print(f"Relative error (std): {(abs(empirical_std - theoretical_std) / theoretical_std)*100:.2f}%")

    # Pass/Fail criterion
    if (abs(empirical_mean - theoretical_mean) / theoretical_mean * 100 < 5) and \
       (abs(empirical_std - theoretical_std) / theoretical_std * 100 < 5):
        print("PASS")
    else:
        print("FAIL")
        diff_mean = empirical_mean - theoretical_mean
        rel_diff_mean = abs(diff_mean) / theoretical_mean * 100
        diff_std = empirical_std - theoretical_std
        rel_diff_std = abs(diff_std) / theoretical_std * 100
        print(f"Offending values: Mean={diff_mean:.6f} ({rel_diff_mean:.2f}%), Std={diff_std:.6f} ({rel_diff_std:.2f}%)")

    # Save plot as output.png
    plt.hist(sample_means, bins=30, density=True)
    x = np.linspace(theoretical_mean - 3*theoretical_std, theoretical_mean + 3*theoretical_std, 100)
    y = stats.norm.pdf(x, loc=theoretical_mean, scale=theoretical_std)
    plt.plot(x, y, 'r-', label='Theoretical Normal Distribution')
    plt.legend()
    plt.savefig('output.png')

test_clt_hypothesis(distribution_type='exponential', n_samples=30, n_trials=10000)