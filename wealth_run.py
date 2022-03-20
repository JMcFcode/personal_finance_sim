"""
Run the code from wealth_simulator.py
"""

from wealth_simulator import MoneySimulator

list_salary = [70, 90, 100, 110, 130, 145, 165]
# list_bonus = [70, 80, 100, 120, 120, 130, 140]  # Optimistic Scenario
list_bonus = [i * 0.7 for i in list_salary]  # As % of salary

wealth_class = MoneySimulator(salary_list=list_salary,
                              bonus_list=list_bonus,
                              initial_saving=70)


df_scenario = wealth_class.run_scenario()
