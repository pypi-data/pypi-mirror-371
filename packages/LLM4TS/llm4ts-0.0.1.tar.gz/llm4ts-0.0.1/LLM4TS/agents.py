import numpy as np

class ThompsonSamplingBayesLRAgent():
  """
  Thompson Sampling agent for contextual bandits using a Bayesian linear regression model.
  
  Attributes:
      n_arms (int): Number of available actions/arms.
      sigma_y (float): Noise standard deviation for Bayesian updates.
      prior_coeff_mu_b (dict): Prior mean for bias term per arm.
      prior_coeff_mu_w (dict): Prior mean for weights per arm.
      prior_coeff_sigma (dict): Prior covariance matrices per arm.
      rng (np.random.Generator): Random number generator for sampling.
  """

  def __init__(self, n_arms, seed, sigma_y, prior_coeff_mu_b, prior_coeff_mu_w, prior_coeff_sigma):
    """Initialize the Thompson Sampling Bayesian Linear Regression agent."""
    # Tracking rewards and actions
    self.reward_list  = []
    self.return_value = 0
    self.agent_obs0_per_draw = []
    self.best_action_per_draw = []
    self.best_post_sample_per_draw = []
    self.reward_per_draw = []
    self.return_per_draw = []

    # Store priors
    self.n_arms = n_arms
    self.sigma_y = sigma_y
    self.prior_coeff_mu_b = {}
    self.prior_coeff_mu_w = {}
    self.prior_coeff_sigma = {}
    str_prior_info = ''

    # Initialize priors for each arm
    for arm in range(n_arms):
      self.prior_coeff_mu_b[arm]  = prior_coeff_mu_b[arm]
      self.prior_coeff_mu_w[arm]  = prior_coeff_mu_w[arm]
      self.prior_coeff_sigma[arm] = prior_coeff_sigma[arm]
      str_prior_info += '\nμb[{}]={}  μw[{}]={}'.format(
          arm, float(self.prior_coeff_mu_b[arm]), arm, self.prior_coeff_mu_w[arm])

    # Random generator
    self.seed = seed
    self.rng = np.random.default_rng(self.seed)

    # Save configuration
    self.config = {'sigma_y':self.sigma_y, 'prior_info':str_prior_info, 'seed':self.seed}

    # Initialize posterior distributions (start with priors)
    self.post_coeff_mu_dict = {}
    self.post_coeff_sigma_dict = {}
    for arm in range(self.n_arms):
      array1 = self.prior_coeff_mu_b[arm]
      array2 = self.prior_coeff_mu_w[arm]
      self.post_coeff_mu_dict[arm] = np.concatenate((array1, array2), axis=None)
      self.post_coeff_sigma_dict[arm] = np.array(self.prior_coeff_sigma[arm])

    # Keep copies for info/debugging
    self.prior_coeff_mu_info_dict = self.post_coeff_mu_dict.copy()
    self.prior_coeff_sigma_info_dict = self.post_coeff_sigma_dict.copy()  # covariance matrices

    # Store previous posterior (defaults to arm 0)
    self.previous_post_coeff_mu    = np.copy(self.post_coeff_mu_dict[0])
    self.previous_post_coeff_sigma = np.copy(self.post_coeff_sigma_dict[0])

    # Placeholders for GP-style inputs
    GP_X = np.array([])
    GP_Y = np.array([])

  def choose_action(self, obs, env_trajectory=None):
    """
    Choose an action using Thompson Sampling.
    
    Args:
        obs (array-like): Current observation/context.
    
    Returns:
        int: Chosen arm index.
    """
    agent_obs_list = list(obs)
    # Add intercept term
    self.agent_obs_with_intercept = np.array([1] + agent_obs_list)
    obs_coeff_samples = []

    # Sample from posterior for each arm
    for arm in range(self.n_arms):
      coeff_sample = self.rng.multivariate_normal(
          mean=self.post_coeff_mu_dict[arm],
          cov=self.post_coeff_sigma_dict[arm])
      obs_coeff_sample = self.agent_obs_with_intercept.T.dot(coeff_sample)
      obs_coeff_samples.append(obs_coeff_sample)

    # Select arm with max sampled reward
    chosen_action = int(np.argmax(obs_coeff_samples))
    self.agent_obs0_per_draw.append(agent_obs_list[0])
    self.best_action_per_draw.append(chosen_action)
    self.best_post_sample_per_draw.append(obs_coeff_samples[chosen_action])
    return chosen_action

  def store_rewards(self, reward):
    """
    Store observed reward and update cumulative return.
    
    Args:
        reward (float): Observed reward for chosen action.
    """
    self.reward_list.append(reward)
    self.return_value += reward
    self.reward_per_draw.append(reward)
    self.return_per_draw.append(self.return_value)

  def calculate_posterior_mean_sigma(self, sigma_y, prior_mu, prior_sigma_inv, X, Y):
    """
    Bayesian update for linear regression posterior.
    
    Args:
        sigma_y (float): Noise standard deviation.
        prior_mu (np.ndarray): Prior mean vector.
        prior_sigma_inv (np.ndarray): Inverse of prior covariance.
        X (np.ndarray): Observation matrix.
        Y (np.ndarray): Reward vector.
    
    Returns:
        tuple: (posterior mean, posterior covariance)
    """
    post_sigma = (sigma_y**2) * np.linalg.inv(X.T @ X + (sigma_y**2) * prior_sigma_inv)
    post_mu    = post_sigma @ ((X.T @ Y)/(sigma_y**2) + prior_sigma_inv @ prior_mu)
    return post_mu, post_sigma

  def update_posterior(self, chosen_action, reward):
    """
    Update posterior parameters for the chosen action using observed reward.
    
    Args:
        chosen_action (int): The action taken.
        reward (float): Observed reward for chosen action.
    """
    # Save previous posterior for chosen action
    self.previous_post_coeff_mu        = self.post_coeff_mu_dict[chosen_action]
    self.previous_post_coeff_sigma     = self.post_coeff_sigma_dict[chosen_action]
    self.previous_post_coeff_sigma_inv = np.linalg.inv(self.previous_post_coeff_sigma)

    # Create design matrix and response
    GP_X = np.array([self.agent_obs_with_intercept]).reshape(1,-1)
    GP_Y = np.array([reward])

    # Update posterior mean and covariance
    chosen_sigma_y = self.sigma_y
    self.post_coeff_mu_dict[chosen_action], self.post_coeff_sigma_dict[chosen_action] = \
        self.calculate_posterior_mean_sigma(
            chosen_sigma_y, self.previous_post_coeff_mu, self.previous_post_coeff_sigma_inv, GP_X, GP_Y)
