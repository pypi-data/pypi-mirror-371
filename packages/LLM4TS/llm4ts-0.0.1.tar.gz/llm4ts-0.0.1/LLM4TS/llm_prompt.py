import pandas as pd
import numpy as np
import timeit
import ast
import re

def get_usage_tokens(max_tokens, response):
  '''This is to get the LLM usage tokens.'''
  usage_prompt_tokens = response.usage.prompt_tokens
  usage_completion_tokens = response.usage.completion_tokens
  usage_total_tokens = response.usage.total_tokens
  usage_total_time = response.usage.total_time
  return usage_prompt_tokens, usage_completion_tokens, usage_total_tokens, usage_total_time

def create_LLM_prompt(prompting_strategy, user_state_description, data_so_far_dict, LLM_prompt_obs, chosen_window, info, b_display_usage):
  '''This constructs the LLM prompt based on prompting_strategy, using user_state_description, data_so_far_dict, LLM_prompt_obs and chosen_window.
  LLM_prompt_obs contains the list of obs variables to be included in the LLM prompt (e.g., LLM_prompt_obs = 'CHD').
  chosen_window is the number of rows of LLM prompt data to be included (e.g., chosen_window = 4).'''
  # prompting_strategy can be: BFQH, BFQ, BF.
  # (B) a description of the adaptive intervention domain and hypothesized behavioral dynamics,
  # (F) the free text participant provided state description
  # (Q) intermediate reasoning questions to guide LLM inference,
  # (H) a short trajectory history consisting of the four most recent (state, action, reward) tuples.

  LLM_prompt_data = []
  str_previous = "\n"
  rows = chosen_window
  previous_list_for_LLM = []

  if len(data_so_far_dict) > 0:
      len_previous_data = len(data_so_far_dict['H'])
      if rows is None:
          n_last_rows = len_previous_data
      else:
          n_last_rows = int(rows)
      start = max(0, len_previous_data-n_last_rows)
      end = len_previous_data

      previous_C = np.array(data_so_far_dict['C'])[start:end]
      previous_H = np.array(data_so_far_dict['H'])[start:end]
      previous_D = np.array(data_so_far_dict['D'])[start:end]
      previous_T = np.array(data_so_far_dict['T'])[start:end]
      previous_action = np.array(data_so_far_dict['action'])[start:end]
      previous_reward = np.array(data_so_far_dict['reward'])[start:end]
      previous_cumulative_reward = np.array(data_so_far_dict['cumulative_reward'])[start:end]

      LLM_prompt_data = []
      for i in range(len(previous_C)):
          data_row = {'C': int(previous_C[i]),
                      'H': float(round(previous_H[i], 3)),
                      'D': float(round(previous_D[i], 3))}
          if len(previous_action) > i:
              data_row['action'] = int(previous_action[i])
              data_row['reward'] = float(round(previous_reward[i], 1))
          if LLM_prompt_obs.find('T') >= 0:
              data_row['T'] = previous_T[i]
          LLM_prompt_data.append(data_row)

  n_len_LLM_prompt_data = int(len(LLM_prompt_data))
  str_LLM_prompt_data = str(LLM_prompt_data)
  if n_len_LLM_prompt_data <= 0:
      str_add_data = ''
  elif n_len_LLM_prompt_data == 1:
      str_add_data = f"""
The current user data in json format is: {str_LLM_prompt_data}."""
  else:
      str_add_data = f"""
The latest and current user data in json format are: {str_LLM_prompt_data}."""

  if (user_state_description is None) or (user_state_description == 'None'):
      prompt_user_state_description = ''
  else:
      prompt_user_state_description = f"""
This morning, when we asked the user how they felt, the user reply was: {user_state_description}."""

  prompt_ask_LLM_User = r"""
Given the user reply, should the mobile health app send a message to the user?
Answer must be boolean True (send) or False (do not send) in json format {'send': , 'reason': }.
"""

  prompt_ask_LLM_reasonning = r"""
answer the following questions:
provide the reason for sending a message to the user,
provide the reason for not sending a message to the user,
is there any risk to the user?
will the user disengage from the study?
is there some long term consequence?
Answer must be in json format:

answer1 =
{
  'reason for sending': string,
  'reason for not sending': string,
  'risk': string,
  'disengage': string,
  'long term consequence': string,
}

Given these answers, provide the final answer to this question:
should the mobile health app send a message to the user?
Answer must be boolean True (send) or False (do not send),
and provide the reason for this answer.
The final answer must be in json format:

answer2 =
{
  'send': boolean,
  'reason': string,
}
"""

  prompt_ask_LLM_User_Quest = f"""
Given the user reply,{prompt_ask_LLM_reasonning}
"""

  prompt_ask_LLM_Hist_User_Quest = f"""
Given the user current state and user reply,{prompt_ask_LLM_reasonning}
"""

  prompt_description = r"""
A mobile health app can send a message to the user to encourage the user to walk."""

  prompt_behavioral_dynamics = r"""
A mobile health app can send a message to the user to encourage the user to walk.
Sending a message causes the habituation level to increase.
Not sending a message causes the habituation level to decrease.
An incorrectly tailored message causes the disengagement risk to increase.
A correctly tailored message causes the disengagement risk to decrease.
The reward is the surplus step count, beyond a baseline count, attenuated by the habituation level.
If the user is sick, injured or cannot walk, then the mobile health app should not send a message."""

  prompt_history_data = f"""
C is the user context, H is the user habituation level, D is user disengagement risk.
C is an integer with value 0 (at home) or 1 (not at home), H is a real number in [0,1], D is a real number in [0,1].
The message can be generic, tailored to context 0, or tailored to context 1.
There are 4 possible actions for the mobile health app:
0 (do not send a message),
1 (send a generic message),
2 (send a message tailored to context 0),
3 (send a message tailored to context 1).{str_add_data}"""

  prompt_end = r"""
Do not add anything else in the response."""

  # prompting_strategy can be 'BFQH', 'BFQ', 'BF'
  if prompting_strategy == 'BF':
      prompt = prompt_behavioral_dynamics + prompt_user_state_description + prompt_ask_LLM_User + prompt_end
  elif prompting_strategy == 'BFQ':
      prompt = prompt_behavioral_dynamics + prompt_user_state_description + prompt_ask_LLM_User_Quest + prompt_end
  elif prompting_strategy == 'BFQH':
      prompt = prompt_behavioral_dynamics + prompt_history_data + prompt_user_state_description + prompt_ask_LLM_Hist_User_Quest + prompt_end
  else:
      error_message = f"prompting_strategy = {prompting_strategy} does not exist!"
      assert (1 == 2), error_message

  return prompt


def extract_from_LLM_response(string, b_display_more=False):
  list_of_items_in_curly_braces = re.findall(r"\{(.*?)\}", string)
  # example: result = ast.literal_eval("{'a': 1}")
  list_of_items = []
  for item in list_of_items_in_curly_braces:
    str_item = str(item).replace("false", "False").replace("true", "True").replace("user's", "user")
    str_item = str_item.replace("It's", "It is").replace("it's", "it is").replace("app's","app")
    str_item = str_item.replace("doctor's", "doctor").replace("There's", "There is").replace("'s ", " ")
    str_item = str_item.replace("n't", " not").replace("'ve", " have")
    b_Ok = True
    if str_item.find('send') >= 0:
      if (((str_item.find('False') <  0) and (str_item.find('True') <  0)) or
          ((str_item.find('False') >= 0) and (str_item.find('True') >= 0))):
        b_Ok = False
    if b_Ok:
      str_item = '{' + str_item + '}'
      new_item = ast.literal_eval(str_item)
      list_of_items.append(new_item)
  return list_of_items


def generate_LLM_response(time_t, prompting_strategy, chosen_LLM_model, client, temperature, max_tokens, user_state_description, data_so_far_dict, LLM_prompt_obs, chosen_window, episode_statistics,
                          info, b_display_usage):
  '''This generates the LLM response using the chosen LLM. A call to the LLM is made by passing the LLM prompt.
  The LLM prompt is constructed based on prompting_strategy, using user_state_description, data_so_far_dict, LLM_prompt_obs and chosen_window.
  LLM_prompt_obs contains the list of obs variables to be included in the LLM prompt (e.g., LLM_prompt_obs = 'CHD').
  chosen_window is the number of rows of LLM prompt data to be included (e.g., chosen_window = 4).'''

  prompt_NEW = create_LLM_prompt(prompting_strategy, user_state_description, data_so_far_dict, LLM_prompt_obs, chosen_window, info, b_display_usage)

  start_LLM_time = timeit.default_timer()

  response = client.chat.completions.create(
      model=chosen_LLM_model,
      messages= [{ "role": "user", "content": prompt_NEW },],
      temperature=temperature,
      max_tokens=max_tokens,
      stop=None,
  )

  stop_LLM_time = timeit.default_timer()
  LLM_duration = stop_LLM_time - start_LLM_time

  result = response.choices[0].message.content

  usage_prompt_tokens, usage_completion_tokens, usage_total_tokens, usage_total_time = get_usage_tokens(max_tokens, response)

  if prompting_strategy == 'BF':
    str_result = result.replace("\n"," ").replace("json","").strip()
    LLM_results_list = extract_from_LLM_response(str_result)
  elif prompting_strategy == 'BFQ' or prompting_strategy == 'BFQH':
    str_result = result.replace("\n"," ").replace("json","").strip()
    pos = str_result.find('answer2 =')
    len_answer2 = len('answer2 =')
    str_result = str_result[pos+len_answer2:].strip().replace("\\"," ")
    LLM_results_list = extract_from_LLM_response(str_result)
  else:
    error_message = f"error in generate_LLM_response! cannot find prompting_strategy={prompting_strategy}..."
    print(error_message)
    assert(1==2), error_message

  episode_statistics['LLM_time_t'].append(int(time_t))
  episode_statistics['LLM_prompt'].append(str(prompt_NEW).strip())
  episode_statistics['LLM_response'].append(str(result).strip())
  episode_statistics['LLM_count'].append(1)
  episode_statistics['LLM_duration'].append(LLM_duration)
  episode_statistics['usage_input_tokens'].append(usage_prompt_tokens)
  episode_statistics['usage_output_tokens'].append(usage_completion_tokens)
  episode_statistics['usage_total_tokens'].append(usage_total_tokens)
  episode_statistics['usage_total_time'].append(usage_total_time)
  return prompt_NEW, LLM_results_list, result, episode_statistics