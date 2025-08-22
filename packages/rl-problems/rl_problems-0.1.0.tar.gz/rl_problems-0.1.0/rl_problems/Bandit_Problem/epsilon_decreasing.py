import numpy as np
import random

class ExponentialDecresingEpsilonBandit:
    """
    K-Armed Bandit using an exponentially decreasing epsilon-greedy strategy.

    Epsilon-greedy selects a random action with probability epsilon (exploration)
    and the action with the highest estimated value with probability 1 - epsilon 
    (exploitation). In this variant, epsilon decreases exponentially over time.

    Attributes:
        n_runs (int): Total number of time steps.
        epsilon_start (float): Initial exploration probability.
        epsilon_end (float): Minimum exploration probability.
        decay_rate (float): Exponential decay rate for epsilon.
        num_arms (int): Number of arms.
        true_q (np.ndarray): True mean reward of each arm (hidden from the agent).
        q_i (np.ndarray): Estimated action values for each arm.
        n_i (np.ndarray): Number of times each arm has been selected.
    """

    def __init__(self, n_runs: int, epsilon_start: float, epsilon_end: float, decay_rate: float, num_arms: int):
        """
        Initialize the K-Armed Bandit environment.

        Args:
            n_runs (int): Total number of time steps.
            epsilon_start (float): Initial probability of selecting a random arm.
            epsilon_end (float): Minimum probability of selecting a random arm.
            decay_rate (float): Rate at which epsilon decays exponentially.
            num_arms (int): Number of arms in the bandit problem.
        """
        self.n_runs = n_runs
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.decay_rate = decay_rate
        self.num_arms = num_arms
        
        self.true_q = np.random.normal(0, 1, num_arms)
        self.q_i = np.zeros(num_arms)
        self.n_i = np.zeros(num_arms, dtype=int)

    def _exp_epsilon(self, step: int) -> float:
        """
        Compute exponentially decreasing epsilon at a given time step.

        Args:
            step (int): Current time step.

        Returns:
            float: Current epsilon value after exponential decay.
        """
        epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * np.exp(-self.decay_rate * step)
        return max(self.epsilon_end, epsilon)  # ensure epsilon does not go below epsilon_end

    def _run(self) -> None:
        """Execute the exponential epsilon-greedy algorithm over all time steps."""
        for t in range(1, self.n_runs + 1):
            epsilon = self._exp_epsilon(t)

            # Select action
            if random.random() < epsilon:
                action = random.randint(0, self.num_arms - 1)  # exploration
            else:
                action = np.argmax(self.q_i)                    # exploitation

            # Sample reward
            reward = np.random.normal(self.true_q[action], 1)

            # Incremental update of Q-value
            self.n_i[action] += 1
            self.q_i[action] += (reward - self.q_i[action]) / self.n_i[action]

    def run_exponential_epsilon_decreasing(self) -> dict:
        """
        Execute the bandit strategy and return results.

        Returns:
            dict: Contains true rewards, estimated action values, and selection counts.
                - "True_Q" (np.ndarray): True mean rewards of each arm.
                - "Estimated_Q" (np.ndarray): Estimated action values.
                - "Counts" (np.ndarray): Number of times each arm was selected.
        """
        self._run()
        return {
            "True_Q": self.true_q,
            "Estimated_Q": self.q_i,
            "Counts": self.n_i
        }
