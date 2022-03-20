"""
Run the code from wealth_simulator.py
"""

from wealth_simulator import MoneySimulator

list_salary = [30, 30, 30]
list_bonus = [i * 0.1 for i in list_salary]  # As % of salary

wealth_class = MoneySimulator(salary_list=list_salary,
                              bonus_list=list_bonus,
                              initial_saving=5)

df_scenario = wealth_class.run_scenario()
