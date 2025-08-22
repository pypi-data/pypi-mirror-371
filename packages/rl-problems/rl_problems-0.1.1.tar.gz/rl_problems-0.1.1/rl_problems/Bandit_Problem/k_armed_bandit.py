import random
import numpy as np

class KArmedBandit:

    """
    ## The Multi-Armed Bandit Problem

    The Multi-Armed Bandit (MAB) problem is a classic reinforcement learning scenario that models a fundamental decision-making challenge: how to balance exploration and exploitation to maximize rewards when facing uncertain outcomes.

    **Core Scenario:**

    Imagine you’re in a casino with a row of slot machines (the "bandits"). Each machine has a secret probability of paying out a reward when you pull its lever. You don’t know what those probabilities are – that’s the core of the problem. Your goal is to maximize your total reward over a series of pulls.

    **Key Components:**

    *   **Arms:** Each slot machine is an “arm.” These are the options you can choose from.
    *   **Rewards:** When you pull an arm, you get a reward (typically a numerical value, like $1 for a payout, or 0 for no payout). These rewards are *random* and based on the *unknown* probability of each arm.
    *   **Exploration vs. Exploitation:**  The central conflict:
        *   **Exploration:** Trying out different arms to gather more information about their payout probabilities.  It’s taking a risk to *learn*.
        *   **Exploitation:** Pulling the arm that you currently believe is the best (based on your past experience). You’re sticking with what you know works *so far*.

    **How it Works:**

    1.  **Initial Stage (Exploration):**  Initially, you’ll likely try all arms (or a significant subset) to get a basic sense of their reward distributions.

    2.  **Learning:** As you pull arms and observe the rewards, you update your estimate of each arm's reward probability. You’ll start to notice that some arms are consistently more rewarding than others.

    3.  **Adaptive Strategy:** You’ll then shift towards exploitation, pulling the arm with the highest estimated reward probability. However, you’ll still occasionally pull other arms to make sure your estimate is accurate and to potentially discover that the “best” arm has changed.

    **Why is it Important?**

    The MAB problem is a powerful theoretical framework because it models many real-world decision-making scenarios where you need to learn from uncertain outcomes. It's used to understand:

    *   **Website A/B Testing:** Which version of a website (A or B) is more effective?
    *   **Personalized Recommendations:** Which product to recommend to a user to maximize clicks or purchases?
    *   **Clinical Trials:** Which treatment is most effective for a particular patient population?
    *   **Resource Allocation:** How to assign limited resources to different projects or initiatives.
        
### Examples
        ```python
bandit = KArmedBandit(n_runs=1000, epsilon=0.1, num_arms=5)
results = bandit.run_epsilon_greedy()
print("True values:", results["True_Q"])
print("Estimated values:", results["Estimated_Q"])
print("Arm counts:", results["Counts"])
```
                
        """

    
    def __init__(self,n_runs : int,epsilon : float,num_arms : int):
        """
        Initialize the K-Armed Bandit environment.

        Args:
            n_runs (int): Number of iterations (steps) to run the bandit.
            epsilon (float): Probability of exploration (random arm selection).
            num_arms (int): Number of arms in the bandit problem.

        Attributes:
            true_q (list[float]): The true mean reward for each arm 
                                  (sampled from N(0,1), hidden from agent).
            q_i (list[float]): Estimated action-value for each arm, updated incrementally.
            n_i (list[int]): Count of how many times each arm has been selected.
        
        ### Examples
        ```python
        bandit = KArmedBandit(n_runs=1000, epsilon=0.1, num_arms=5)
        results = bandit.run_epsilon_greedy()
        print("True values:", results["True_Q"])
        print("Estimated values:", results["Estimated_Q"])
        print("Arm counts:", results["Counts"])
        ```
        
        """
        self.__n_runs = n_runs
        self.__epsilon = epsilon
        self.__num_arms = num_arms
        self.true_q = np.random.normal(0, 1, num_arms)
        self.__q_i = np.zeros(num_arms).tolist()
        self.__n_i = np.zeros(self.__num_arms,dtype=int).tolist()

    def __run(self) -> None:

        """
        Run the epsilon-greedy algorithm for n_runs iterations.

        Algorithm:
        1. With probability epsilon → explore (choose a random arm).
        2. Otherwise → exploit (choose the arm with the highest estimated value).
        3. Observe reward ~ N(true_q[arm], 1).
        4. Update the estimated value of the chosen arm using **incremental mean**:

            Q_{n+1}(a) = Q_n(a) + (1 / N(a)) * (R - Q_n(a))

            where:
              - Q_n(a) = current estimate of arm 'a'
              - N(a)   = number of times arm 'a' has been chosen
              - R      = observed reward
        """

        for _ in range(1,self.__n_runs):

            if random.random() < self.__epsilon: #here random.random returns 0 to 1 range random number
                index = random.randint(0,self.__num_arms - 1)
            
            else:
                index = np.argmax(self.__q_i)
            
            reward = np.random.normal(self.true_q[index], 1)
            
            self.__n_i[index] += 1

            self.__q_i[index] = self.__q_i[index] + (1 / self.__n_i[index]  * (reward - self.__q_i[index])) 

    def run_epsilon_greedy(self) -> dict:
        """
    Execute the bandit using the ε-greedy algorithm.

    At each step:
      - With probability ε, a random arm is selected (exploration).
      - With probability (1 - ε), the best estimated arm is selected (exploitation).
      - Rewards are generated based on the true distribution of each arm.
      - Action-value estimates (Q-values) are updated incrementally.

    Returns:
    dict: A dictionary containing the following keys:
        - "True_Q" (np.ndarray): The true underlying reward values of each arm.
        - "Estimated_Q" (np.ndarray): The estimated reward values learned for each arm.
        - "Counts" (np.ndarray): The number of times each arm was selected.


    ### Examples
    ```python
    bandit = KArmedBandit(n_runs=500, epsilon=0.1, num_arms=3)
    results = bandit.run_epsilon_greedy()
    print(results["Estimated_Q"])
    ```
    """

        self.__run()
        
        return  {
            "True_Q": self.true_q,
            "Estimated_Q": self.__q_i,
            "Counts": self.__n_i
        }
