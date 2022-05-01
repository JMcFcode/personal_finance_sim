#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 10:14:20 2022

@author: joelmcfarlane

"""

r_avg = 0.07  # Average return on liquid investments.
r_std = 0.15  # Standard deviation on the return on investments.

bonus_std_prop = 0.5  # Standard deviation on bonuses as a proportion of each year's bonus
bonus_spend_rate = 0.2  # Proportion of bonus after tax that is spent on non-asset purchases

month_non_rent = 1.4  # Amount in thousands spent per month not including rent.
spend_grow = 1.1  # Proportion per year that non-rent spending will grow by

year_home = 1  # Years living at home. Note that default order is:  live at home -> rent -> buy house
year_rent = 2  # Years renting out of the house after living at home but before buying a house

rent_home = 0.4  # Cost of living at home
rent_away = 1.5  # Cost of renting outside the home

deposit = 0.25  # Deposit on house as a proportion of house cost.
house_cost = 800  # Price paid for a house in thousands.
mortgage_rate = 0.03  # Interest rate on mortgage.
house_type = 'normal'  # Type of purchase on house, "normal" or "htb"

house_inf = 0.09  # Rate on house price inflation as a %
house_inf_std = 0.15  # Standard deviation on house price inflation as a %

show_breakdown = True  # Show the mean liquid and illiquid assets
show_extra = True   # Show the results of every simulation and results two sigma up and down.

color_main = 'orange'

# btl_dict = {6: [300, 75, 3],
            # }   # Key = Year, list = [house_price, deposit_amount, rent_per_month] (all in thousands)

btl_dict = {}
