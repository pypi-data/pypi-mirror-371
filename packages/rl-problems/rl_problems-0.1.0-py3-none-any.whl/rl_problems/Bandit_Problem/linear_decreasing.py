import numpy as np
import random

class LinearDecresingEpsilonBandit:
    """
    K-Armed Bandit using a linearly decreasing epsilon-greedy strategy.

    The epsilon-greedy strategy selects a random action with probability epsilon
    (exploration) and selects the action with the highest estimated value with
    probability 1 - epsilon (exploitation). In this variant, epsilon decreases
    linearly from `epsilon_start` to `epsilon_end` over the total number of steps.

    Attributes:
        n_runs (int): Total number of time steps.
        epsilon_start (float): Initial exploration probability.
        epsilon_end (float): Final exploration probability.
        num_arms (int): Number of arms.
        true_q (np.ndarray): True mean reward of each arm (hidden from agent).
        q_i (np.ndarray): Estimated action values for each arm.
        n_i (np.ndarray): Number of times each arm has been selected.
    """

    def __init__(self, n_runs: int, epsilon_start: float, epsilon_end: float, num_arms: int):
        """
        Initialize the K-Armed Bandit environment.

        Args:
            n_runs (int): Total number of time steps.
            epsilon_start (float): Initial probability of selecting a random arm.
            epsilon_end (float): Final probability of selecting a random arm.
            num_arms (int): Number of arms in the bandit problem.
        """
        self.n_runs = n_runs
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.num_arms = num_arms
        
        self.true_q = np.random.normal(0, 1, num_arms)
        self.q_i = np.zeros(num_arms)
        self.n_i = np.zeros(num_arms, dtype=int)

    def _linear_epsilon(self, step: int) -> float:
        """
        Compute the linearly decreasing epsilon at a given time step.

        Args:
            step (int): Current time step.

        Returns:
            float: Current epsilon value.
        """
        return self.epsilon_start - step * (self.epsilon_start - self.epsilon_end) / self.n_runs

    def _run(self) -> None:
        """Execute the linear decreasing epsilon-greedy algorithm."""
        for t in range(1, self.n_runs + 1):
            epsilon = self._linear_epsilon(t)

            if random.random() < epsilon:
                action = random.randint(0, self.num_arms - 1)  # exploration
            else:
                action = np.argmax(self.q_i)                    # exploitation

            reward = np.random.normal(self.true_q[action], 1)

            self.n_i[action] += 1
            self.q_i[action] += (reward - self.q_i[action]) / self.n_i[action]

    def run_linear_epsilon_decreasing(self) -> dict:
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