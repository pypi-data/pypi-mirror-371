import numpy as np

class KArmedBanditUCB:
    """
    K-Armed Bandit implementation using the Upper Confidence Bound (UCB) strategy.

    The UCB algorithm balances exploration and exploitation by selecting the arm
    with the highest upper confidence bound:

        a_t = argmax_a [ Q_t(a) + c * sqrt(ln(t) / N_t(a)) ]

    where:
        - Q_t(a) : estimated value of arm `a` at time `t`
        - N_t(a) : number of times arm `a` has been selected
        - t      : current time step
        - c      : exploration parameter

    This method ensures each arm is selected at least once and gradually favors
    arms with higher estimated rewards while still exploring under-sampled arms.
    
    Attributes:
        n_runs (int): Total number of iterations (time steps) to run the algorithm.
        num_arms (int): Number of arms in the bandit problem.
        c (float): Exploration parameter controlling the balance between exploration
                   and exploitation. Higher `c` favors more exploration.
        true_q (np.ndarray): True mean reward of each arm (hidden from the agent).
        q_i (np.ndarray): Estimated action values for each arm.
        n_i (np.ndarray): Number of times each arm has been selected.
    """

    def __init__(self, n_runs: int, num_arms: int, c: float = 2):
        """
        Initialize the K-Armed Bandit environment for UCB.

        Args:
            n_runs (int): Total number of time steps.
            num_arms (int): Number of arms in the bandit problem.
            c (float): Exploration parameter for UCB. Default is 2.
        """
        self.n_runs = n_runs
        self.num_arms = num_arms
        self.c = c
        
        self.true_q = np.random.normal(0, 1, num_arms)  # Hidden true mean rewards
        self.q_i = np.zeros(num_arms)                   # Estimated action values
        self.n_i = np.zeros(num_arms, dtype=int)       # Counts of selections

    def run_bandit_ucb(self) -> dict:
        """
        Execute the UCB algorithm over `n_runs` time steps.

        Returns:
            dict: A dictionary containing:
                - "True_Q" (np.ndarray): True mean rewards of each arm.
                - "Estimated_Q" (np.ndarray): Estimated action values after running.
                - "Counts" (np.ndarray): Number of times each arm was selected.
                - "Rewards" (list[float]): Rewards received at each time step.
        """
        rewards = []
        
        for t in range(1, self.n_runs + 1):
            # Compute UCB values for all arms
            ucb_values = np.zeros(self.num_arms)
            for a in range(self.num_arms):
                if self.n_i[a] == 0:
                    ucb_values[a] = float('inf')  # Ensure each arm is selected at least once
                else:
                    ucb_values[a] = self.q_i[a] + self.c * np.sqrt(np.log(t) / self.n_i[a])

            # Select the arm with the highest UCB value
            action = np.argmax(ucb_values)
            
            # Sample reward from true distribution
            reward = np.random.normal(self.true_q[action], 1)
            
            # Incrementally update estimated value
            self.n_i[action] += 1
            self.q_i[action] += (reward - self.q_i[action]) / self.n_i[action]

            rewards.append(reward)
        
        return {
            "True_Q": self.true_q,
            "Estimated_Q": self.q_i,
            "Counts": self.n_i,
            "Rewards": rewards
        }