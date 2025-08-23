import pandas as pd
import numpy as np
import collections
import matplotlib.pyplot as plt

# Plotting parameters
fontsize_TITLE=10; fontsize=9; fontsize_LEGEND=5
bbox_to_anchor=(.5, -.85); ncol=3
CHOSEN_Y_LIM=(0,2200); y_lim_reward=(0,1750)
fig_size_plot=(2.8,2)

def set_random_seed(seed):
  """Set numpy random seed for reproducibility."""
  np.random.seed(seed)

def get_key(sigma, δd, εd, seed, chosen_obs_name):
  """Generate unique key string for experiment configuration."""
  str_detail = 'σ={} δd={} εd={} seed={} obs={}'.format(sigma, δd, εd, seed, '-'.join(chosen_obs_name))
  str_key = str_detail.replace('.','').replace(' ','_').replace('-','').replace('=','')
  return str_key

def plot_cum_rewards(plot_title, obs_names, cum_rewards, color, y_lim=(-200,2000), figsize=(4,1.8)):
  """Plot cumulative rewards over episodes."""
  plt.figure(figsize=figsize)
  plt.plot(cum_rewards, color=color)
  plt_title = '{}'.format(plot_title)
  plt.title(plt_title)
  plt.ylim(y_lim); plt.xlabel('episode'); plt.ylabel('Cumulative reward')
  plt.grid(); plt.tight_layout(); plt.show()

def get_key_LLM4TS(b_use_LLM, chosen_pW01, chosen_pW11, LLM_model,
                   trial, episode, LLM_prompt_obs, chosen_window, chosen_params_dict,
                   NAME_STANDARD='onlyTS', NAME_LLM4TS='LLM4TS'):
  """Generate descriptive key string for LLM4TS vs standard TS experiments."""
  pW00 = 1-chosen_pW01
  str_use_LLM = NAME_LLM4TS if b_use_LLM else NAME_STANDARD
  long_str_key = '{} pW11 pW00 = {} {:.1f}'.format(str_use_LLM, chosen_pW11, pW00)
  long_str_key += ' '+LLM_model+' trial{} ep{} prompt_obs= {} {} {}'.format(trial, episode, str(chosen_window), LLM_prompt_obs, chosen_params_dict)
  return long_str_key

def get_str_chosen_params(chosen_params_dict, b_shorten=False):
  """Convert chosen parameters dict into string (optionally shortened)."""
  str_chosen_params = ''
  for k,v in chosen_params_dict.items():
    if b_shorten:
      if k.find('η') >= 0 or k.find('εd') >=0:
        str_chosen_params += '{}={} '.format(k,v)
    else:
      str_chosen_params += '{}={} '.format(k,v)
  return str_chosen_params.strip()

def plot_LLM4TS(prompting_strategy, b_use_LLM, data_dict_plot, LLM_model,
                chosen_pW01, chosen_pW11, LLM_prompt_obs, chosen_window, chosen_params_dict, 
                n_trials_plot, n_episodes_plot, n_steps_plot, figsize=(11,2), figsize2=(7,2),
                chosen_trials_for_plot=None, chosen_agent_for_plot=None,
                y_lim_action_hist=None, y_lim_cum_reward=y_lim_reward):
  """Plot action histograms and cumulative rewards for LLM4TS or standard TS."""

  str_chosen_params = get_str_chosen_params(chosen_params_dict)
  if chosen_trials_for_plot is None:
    # Default: plot last 2 trials
    chosen_trials_for_plot = range(max(0,n_trials_plot-2), max(1,n_trials_plot))
  chosen_episodes = [n_episodes_plot-1]

  # Extract probabilities from simulation results
  pW01 = None; pW11 = None
  for trial in chosen_trials_for_plot:
    for episode in chosen_episodes:
      key=get_key_LLM4TS(b_use_LLM, chosen_pW01, chosen_pW11, LLM_model,
                         trial, episode, LLM_prompt_obs, chosen_window, chosen_params_dict)
      for item_dict in data_dict_plot[key]:
        for k,v in item_dict.items():
          if k.find('pref_LLM_a_pw1100') >= 0:
            for time_t, item_i in enumerate(v):
              if (time_t < 3) or (time_t > len(v)-4):
                pW01 = item_i[3]
                pW11 = item_i[4]

  # Titles
  str_episodes = '' if n_episodes_plot <= 1 else 'episodes={}'.format(chosen_episodes)
  str_env = f"\n{str_chosen_params}"
  if b_use_LLM:
    main_title = f"LLM4TS{str_env}"
    short_plot_title = 'LLM4TS'
  else:
    main_title = 'standard TS{}'.format(str_env)
    short_plot_title = 'standard TS'

  # Collect cumulative rewards
  all_cum_rewards = []; min_episodes = float('inf')
  for trial in range(n_trials_plot):
    for episode in chosen_episodes:
      key=get_key_LLM4TS(b_use_LLM, chosen_pW01, chosen_pW11, LLM_model,
                         trial, episode, LLM_prompt_obs, chosen_window, chosen_params_dict)
      for item_dict in data_dict_plot[key]:
        for k,v in item_dict.items():
          if (k.find('cumulative_reward') >= 0):
            min_episodes = min(min_episodes, len(v))
            all_cum_rewards.append(v)

  # Pad rewards to same length
  for i, item in enumerate(all_cum_rewards):
    new_item = item
    pad = n_steps_plot - len(new_item)
    if pad > 0:
      new_item = list(new_item) + [item[-1]] * pad
    all_cum_rewards[i] = np.array(new_item)
  all_cum_rewards = np.array(all_cum_rewards)

  # Mean & SD across trials
  cum_reward_mean = np.mean(all_cum_rewards, axis=0)
  cum_reward_sd   = np.std(all_cum_rewards, axis=0)
  xs_reward = np.arange(len(cum_reward_mean))   

  # Plot action histograms
  plt.figure(figsize=fig_size_plot)
  plt.subplot(111)
  plt.title("{}\nAction histogram ({} trials)".format(short_plot_title, n_trials_plot), fontsize=fontsize)
  all_trials_actions = collections.defaultdict(int)
  for trial in range(n_trials_plot):
    for episode in chosen_episodes:
      key=get_key_LLM4TS(b_use_LLM, chosen_pW01, chosen_pW11, LLM_model,
                         trial, episode, LLM_prompt_obs, chosen_window, chosen_params_dict)
      for item_dict in data_dict_plot[key]:
        for k,v in item_dict.items():
          if k.find('action') >= 0:
            for item in list(v):
              all_trials_actions[item] += 1
  color_i = 'dimgray' if not b_use_LLM else 'dodgerblue'
  for a_i in range(4):
    plt.bar(a_i, height=all_trials_actions[a_i], label='action', width=0.25, color=color_i, align='center')
  plt.xticks(range(0,4), fontsize=fontsize); plt.yticks(fontsize=fontsize)
  plt.xlabel('Selected action', fontsize=fontsize); plt.ylabel('Frequency', fontsize=fontsize)
  plt.ylim(y_lim_action_hist); plt.xlim(-1,4)
  plt.tight_layout(); plt.show()

  # Plot cumulative reward
  plt.figure(figsize=fig_size_plot)
  plt.subplot(111)
  plt.title("{}\nCumulative reward".format(main_title), fontsize=fontsize)
  plt.plot(cum_reward_mean, color=color_i)
  plt.fill_between(xs_reward, cum_reward_mean-cum_reward_sd, cum_reward_mean+cum_reward_sd,
                   alpha=.2, label='mean+/-sd', color=color_i)
  plt.ylabel('Cumulative reward', fontsize=fontsize); plt.xlabel('t', fontsize=fontsize)
  plt.xticks(fontsize=fontsize); plt.yticks(fontsize=fontsize)
  plt.ylim(y_lim_cum_reward); plt.xlim(-.5,n_steps_plot-.5)
  plt.tight_layout(); plt.show()
