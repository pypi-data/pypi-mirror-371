# RL-Problems

RL-Problems is a Python package that provides clean and modular implementations of classic **Reinforcement Learning (RL) algorithms**. The package is designed to make RL experiments and learning accessible, with functions and classes that can be imported and used directly, similar to standard Python libraries like NumPy. It focuses on clarity, reusability, and extendability, making it suitable for both beginners and researchers who want to experiment with RL strategies.  

Currently, the package includes **K-Armed Bandits** with standard epsilon-greedy and contextual strategies, as well as linear and exponential epsilon decay variants for exploration control. Each algorithm is implemented as a class or function, allowing users to quickly test different RL scenarios, track rewards, and analyze arm selection behavior. Future updates will expand the library with more RL algorithms and evaluation utilities.  

### **Examples**

```python

from RL_Problems.Bandit_Problem.linear_decreasing import LinearDecresingEpsilonBandit

s1 = LinearDecresingEpsilonBandit(n_runs=1000,epsilon_start=1.0,epsilon_end=0.01,num_arms=10)

results = s1.run_linear_epsilon_decreasing()
print(results)
```