import numpy as np
import random

class ContextualBandit:
    """
    Contextual Bandit implementation with ε-greedy strategy.

    A contextual bandit is a simplified reinforcement learning setting where:
      - At each step, the agent observes a *context* (a feature vector).
      - Based on the context, the agent selects one of several possible *arms* (actions).
      - The environment returns a *reward* depending on the chosen arm and context.
      - The agent learns to maximize rewards by balancing exploration vs exploitation.

    This implementation:
      - Models each arm's expected reward as a linear function of the context.
      - Uses ε-greedy strategy for action selection.
      - Updates estimates online with incremental learning.
    """
    
    def __init__(self, n_runs: int, epsilon: float, num_arms: int, context_dim: int):
        """
        Initialize the contextual bandit experiment.

        Args:
            n_runs (int): Number of iterations (time steps) to run the bandit.
            epsilon (float): Probability of choosing a random action (exploration).
            num_arms (int): Number of arms (actions) available.
            context_dim (int): Dimension of context feature vector.

        Attributes:
            true_q (np.ndarray): True underlying mean rewards of each arm (unknown to agent).
            __q_i (np.ndarray): Agent's estimated weights for each arm (shape: num_arms × context_dim).
            __n_i (np.ndarray): Count of how many times each arm has been selected.
        
        ### Examples
            
        ```python
        bandit = ContextualBandit(n_runs=1000, epsilon=0.1, num_arms=5, context_dim=3)
        results = bandit.run_contextual_bandit()
        print("True values shape:", results["True_Q"].shape)
        print("Estimated values shape:", results["Estimated_Q"].shape)
        print("Arm counts:", results["Counts"])
        ```
        
        """
        self.__num_arms = num_arms
        self.__context_dim = context_dim
        self.__n_runs = n_runs
        self.__epsilon = epsilon

        # True underlying reward means for each arm (environment's hidden rule)
        # self.true_q = np.random.normal(0, 1, num_arms)
        self.true_q = np.random.normal(0, 1, (self.__num_arms, self.__context_dim))

        # Agent's estimated weights for each arm
        self.__q_i = np.zeros((self.__num_arms, self.__context_dim))

        # Counter of times each arm is chosen
        self.__n_i = np.zeros(self.__num_arms, dtype=int)
    
    
    def __get_context(self) -> np.ndarray:
        """
        Generate a random context vector (environment features).

        Returns:
            np.ndarray: A context vector sampled from N(0,1) distribution.
        """
        return np.random.normal(0, 1, self.__context_dim)
    
    def __select_action(self, context: np.ndarray) -> int:
        """
        Select an action using ε-greedy strategy.

        With probability ε → pick a random action (exploration).
        With probability (1-ε) → pick the action with highest estimated reward (exploitation).

        Args:
            context (np.ndarray): Current context vector.

        Returns:
            int: Index of the chosen arm.
        """
        if random.random() < self.__epsilon:
            return random.randint(0, self.__num_arms - 1)  # Explore
        
        estimated_rewards = [np.dot(self.__q_i[a], context) for a in range(self.__num_arms)]
        return int(np.argmax(estimated_rewards))  # Exploit
    
    def __get_reward(self, action: int, context: np.ndarray) -> float:
        """
        Compute reward from environment for a given action and context.

        The reward is modeled as:
            reward = (true_q[action] · context) + noise

        Args:
            action (int): Chosen arm index.
            context (np.ndarray): Current context vector.

        Returns:
            float: Observed reward.
        """
        return np.dot(self.true_q[action], context) + np.random.normal(0, 0.1)

    def __update_estimates(self, action: int, reward: float, context: np.ndarray) -> None:
        """
        Update the estimated weights for the chosen arm using online gradient update.

        Args:
            action (int): Chosen arm index.
            reward (float): Observed reward.
            context (np.ndarray): Context vector used for this action.
        """
        self.__n_i[action] += 1
        lr = 1 / self.__n_i[action]  # Decaying learning rate
        error = reward - np.dot(self.__q_i[action], context)
        self.__q_i[action] += lr * error * context

    def __run(self) -> None:
        """
        Execute the bandit for n_runs iterations.
        """
        for _ in range(self.__n_runs):
            context = self.__get_context()
            action = self.__select_action(context)
            reward = self.__get_reward(action, context)
            self.__update_estimates(action, reward, context)

    def run_contextual_bandit(self) -> dict:
        """
        Run the contextual bandit experiment and return results.

        Returns:
            dict: Results summary containing:
                - "True_Q" (np.ndarray): True underlying mean rewards of each arm.
                - "Estimated_Q" (np.ndarray): Learned weight vectors for each arm.
                - "Counts" (np.ndarray): Number of times each arm was selected.
        
        ### Examples
        ```python
        bandit = ContextualBandit(n_runs=1000, epsilon=0.1, num_arms=5, context_dim=10)
        results = bandit.run_contextual_bandit()
        print("True values (weights):", results["True_Q"])
        print("Estimated values (weights):", results["Estimated_Q"])
        print("Arm counts:", results["Counts"])
        ```
                
        """
        self.__run()
        return {
            "True_Q": self.true_q,
            "Estimated_Q": self.__q_i,
            "Counts": self.__n_i
        }
