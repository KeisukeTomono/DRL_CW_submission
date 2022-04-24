#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

# In[9]:


import random
import json
import gym
from gym import spaces
import pandas as pd
import numpy as np

MAX_ACCOUNT_BALANCE = 2147483647
MAX_NUM_SHARES = 2147483647
MAX_SHARE_PRICE = 5000 
MAX_OPEN_POSITIONS = 5
MAX_STEPS = 20000

INITIAL_ACCOUNT_BALANCE = 10000


class StockTradingEnv(gym.Env):
    """A stock trading environment for OpenAI gym"""
    metadata = {'render.modes': ['human']} 

    def __init__(self, df):
        super(StockTradingEnv, self).__init__()

        self.df = df
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)
#self.terminal = False #added from paper code

        # Actions of the format Buy x%, Sell x%, Hold, etc.
        self.action_space = spaces.Discrete(3)


        # Prices contains the OHCL values for the last five prices
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(11,), dtype=np.float16)#Not specofy the range of columns
    
        #store the data for the graph
#        self.asset_memory=[INITIAL_ACCOUNT_BALANCE]
#        self.rewards_memory=[]
    

    
    def _next_observation(self):
        # Get the stock data points for the last 5 days and scale to between 0-1
        obs = np.array([
            self.df.loc[self.current_step: self.current_step 
                        , 'Open'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step 
                        , 'High'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step 
                        , 'Low'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step 
                        , 'Close'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step 
                        , 'Volume'].values / MAX_NUM_SHARES,
            self.balance / MAX_ACCOUNT_BALANCE,
            self.shares_held / MAX_NUM_SHARES,
            self.cost_basis / MAX_SHARE_PRICE,
            self.total_shares_sold / MAX_NUM_SHARES,
            self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE),
            self.profit / MAX_ACCOUNT_BALANCE
        ],dtype=np.float16)


        return obs

    def _take_action(self, action):

        current_price = random.uniform(
            self.df.loc[self.current_step, "Open"], self.df.loc[self.current_step, "Close"])

        action_type = action
        amount = 1 #exchange amount 1 or 0.5 for simplicity and chech the convergence


        if action_type < 1:
            # Buy amount % of balance in shares
            total_possible = int(self.balance / current_price)
            shares_bought = int(total_possible * amount)
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price

            self.balance -= additional_cost
            self.cost_basis = (
                prev_cost + additional_cost) / (self.shares_held + shares_bought)
            self.shares_held += shares_bought

        elif action_type < 2:
            # Sell amount % of shares held
            shares_sold = int(self.shares_held * amount)
            self.balance += shares_sold * current_price
            self.shares_held -= shares_sold
            self.total_shares_sold += shares_sold
            self.total_sales_value += shares_sold * current_price
        
        self.net_worth = self.balance + self.shares_held * current_price
        

        if self.net_worth > self.max_net_worth:
            self.max_net_worth = self.net_worth

        if self.shares_held == 0:
            self.cost_basis = 0

            
            
            
    def step(self, action):
# Execute one time step within the environment
        self._take_action(action)

#        df_total_value=pd.DataFrame(self.asset_memory)#added from paper code
#        df_rewards=pd.DataFrame(self.rewards_memory)#added from paper code
        
        
        self.current_step += 1
        
        
        if self.current_step > len(self.df.loc[:, 'Open'].values) - 6:
            self.current_step = 0
            
            

        delay_modifier = (self.current_step / MAX_STEPS)
        


        
        obs = self._next_observation()

        self.profit = self.net_worth - INITIAL_ACCOUNT_BALANCE
        max_net_worth= self.max_net_worth
#        self.asset_memory.append(max_net_worth)#added from paper code
#        self.rewards_memory.append(reward)#added from paper code


        done = self.net_worth <= 0.5*INITIAL_ACCOUNT_BALANCE#changed from net_worh to balance,
        #meaning that if my networth <my initial half balance, then stop this episode!!
    

        reward = self.profit * delay_modifier#changed from self.balance to self.profit
    
        return obs, reward, done, {}


    
    
    def reset(self):

        # Reset the state of the environment to an initial state
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.net_worth = INITIAL_ACCOUNT_BALANCE
        self.max_net_worth = INITIAL_ACCOUNT_BALANCE
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.profit =0 # this is added for done and reward by my self.


        # Set the current step to a random point within the data frame
        self.current_step = random.randint(
            0, len(self.df.loc[:, 'Open'].values) - 6)


        return self._next_observation()



    def render(self, mode='human', close=False):
        # Render the environment to the screen
        profit = self.profit #self.net_worth - INITIAL_ACCOUNT_BALANCE
        max_net_worth= self.max_net_worth
        current_step=self.current_step
        current_balance=self.balance
        shares_held = self.shares_held
        total_shares_sold=self.total_shares_sold
        cost_basis=self.cost_basis
        total_sales_value=self.total_sales_value
        net_worth=self.net_worth
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(
            f'Shares held: {self.shares_held} (Total sold: {self.total_shares_sold})')
        print(
            f'Avg cost for held shares: {self.cost_basis} (Total sales value: {self.total_sales_value})')
        print(
            f'Net worth: {self.net_worth} (Max net worth: {self.max_net_worth})')
        print(f'Profit: {profit}')
        
        episode_output=[profit, max_net_worth,current_step,current_balance,shares_held,total_shares_sold,cost_basis,total_sales_value,net_worth]
        return episode_output


# In[ ]:






# In[ ]:




