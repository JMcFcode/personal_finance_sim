#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 10:14:20 2022

@author: joelmcfarlane

"""

r_avg: float = 0.07  # Average return on liquid investments.
r_std: float = 0.10  # Standard deviation on the return on investments.

bonus_std_prop: float = 0.5  # Standard deviation on bonuses as a proportion of each year's bonus
bonus_spend_rate: float = 0.2  # Proportion of bonus after tax that is spent on non-asset purchases

month_non_rent: float = 1.4  # Amount in thousands spent per month not including rent.
spend_grow: float = 1.1  # Proportion per year that non-rent spending will grow by

year_home: int = 1  # Years living at home. Note that default order is:  live at home -> rent -> buy house
year_rent: int = 1  # Years renting out of the house after living at home but before buying a house

rent_home: float = 0.4  # Cost of living at home
rent_away: float = 2.1  # Cost of renting outside the home

deposit: float = 0.25  # Deposit on house as a proportion of house cost.
house_cost: float = 450  # Price paid for a house in thousands.
mortgage_rate: float = 0.055  # Interest rate on mortgage.
mortgage_length: int = 30  # Length of mortgage in years.
house_type: str = 'normal'  # Type of purchase on house, "normal" or "htb".

house_inf: float = 0.09  # Rate on house price inflation as a %
house_inf_std: float = 0.15  # Standard deviation on house price inflation as a %

show_breakdown: bool = True  # Show the mean liquid and illiquid assets
show_extra: bool = True   # Show the results of every simulation and results two sigma up and down.

color_main: str = 'orange'

# btl_dict: dict = {6: [300, 75, 3]
#                   }   # Key = Year, list = [house_price, deposit_amount, rent_per_month] (all in thousands)

btl_dict: dict = {}
