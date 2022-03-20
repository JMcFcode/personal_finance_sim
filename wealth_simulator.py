#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 17:47:03 2021

@author: joelmcfarlane
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from copy import copy

import wealth_config

sns.set()


class MoneySimulator:
    """
    Tools for the modelling of personal finance.
    """

    def __init__(self, initial_saving: float, salary_list: list, bonus_list: list):
        self.initial_saving = initial_saving
        self.salary_list = salary_list
        self.bonus_list = bonus_list

        self.bonus_spend_rate = wealth_config.bonus_spend_rate
        self.r_avg = wealth_config.r_avg
        self.r_std = wealth_config.r_std
        self.bonus_std_prop = wealth_config.bonus_std_prop
        self.month_non_rent = wealth_config.month_non_rent
        self.spend_grow = wealth_config.spend_grow
        self.year_home = wealth_config.year_home
        self.year_rent = wealth_config.year_rent

        self.rent_home = wealth_config.rent_home
        self.rent_away = wealth_config.rent_away

        self.deposit = wealth_config.deposit
        self.house_cost = wealth_config.house_cost
        self.mortgage_rate = wealth_config.mortgage_rate
        self.house_type = wealth_config.house_type

        self.house_inf = wealth_config.house_inf
        self.house_inf_std = wealth_config.house_inf_std

        self.colour_main = 'orange'
        self.label = self.house_type + ' £' + str(self.house_cost) + 'k. ' + str(
            self.year_home) + ' years at home. ' + str(self.year_rent) + ' years rent.'

        self.show_extra = False
        self.show_breakdown = True

    @staticmethod
    def tax_calc(salary: float, bonus: float) -> float:
        """
        Calculate the amount left after tax.
        """
        tax_buckets = [0, 12.57, 50.27, 150, np.inf]
        tax_rate = [0, 0.2, 0.4, 0.45]

        tax_income = salary + bonus
        tax_paid = 0

        if tax_income > 100:
            tax_paid += tax_rate[1] * (min(tax_income, 100 + 2 * tax_buckets[1]) - 100)

        for i in range(len(tax_buckets)):
            if tax_income > tax_buckets[i + 1]:
                tax_paid += (tax_buckets[i + 1] - tax_buckets[i]) * tax_rate[i]
            else:
                tax_paid += (tax_income - tax_buckets[i]) * tax_rate[i]
                return tax_paid

    @staticmethod
    def ni_calc(salary, bonus):
        """
        Calculate the amount of national insurance paid.
        """
        ni_buckets = [0, 9.55, 50.25, np.inf]
        ni_rate = [0, 0.1325, 0.0325]

        ni_income = salary + bonus
        ni_paid = 0
        for i in range(len(ni_buckets)):
            if ni_income > ni_buckets[i + 1]:
                ni_paid += (ni_buckets[i + 1] - ni_buckets[i]) * ni_rate[i]
            else:
                ni_paid += (ni_income - ni_buckets[i]) * ni_rate[i]
                return ni_paid

    def tax_ni(self, salary, bonus, logs=False):
        "Find out how much tax + ni you've paid."
        tax_paid = self.tax_calc(salary, bonus)
        ni_paid = self.ni_calc(salary, bonus)

        net_income = salary + bonus - ni_paid - tax_paid
        if logs:
            print(f'The tax paid is {tax_paid}')
            print(f'The National Insurance paid is {ni_paid}')
            print(f'Take home income is {net_income}')
        return net_income

    def saving_calc(self, years):
        """
        Calculate how much I will have saved of the cash and bonus.
        """

        curr_val = copy(self.initial_saving)
        list_curr_val = [self.initial_saving]
        list_liq = [self.initial_saving]
        list_ill = [0]
        liq_inv = self.initial_saving
        ill_inv = 0

        for i in range(years):

            net_sal = self.tax_ni(salary=self.salary_list[i], bonus=0)

            bonus_rand = max(np.random.normal(self.bonus_list[i], self.bonus_list[i] * self.bonus_std_prop), 0)
            net_bonus = self.tax_ni(salary=self.salary_list[i], bonus=bonus_rand) - net_sal

            sunk_cost_month, principal_month, equity_loan = self.month_costs(i)
            monthly_save = net_sal / 12 - sunk_cost_month

            liq_inv = self.yearly_ret(start_val=liq_inv,
                                      month_save=monthly_save,
                                      r=np.random.normal(self.r_avg, self.r_avg))
            ill_inv = self.yearly_ret(start_val=ill_inv,
                                      month_save=principal_month,
                                      r=np.random.normal(self.house_inf, self.house_inf_std))

            liq_inv += net_bonus * (1 - self.bonus_spend_rate)

            if i + 1 == 5 + self.year_home + self.year_rent and self.house_type == 'htb':
                liq_inv = liq_inv - equity_loan
                ill_inv = ill_inv + equity_loan

            if i + 1 == self.year_home + self.year_rent:
                liq_inv = liq_inv - (self.stamp_duty_calc(self.house_cost) + 5 + self.deposit * self.house_cost)
                ill_inv += self.deposit * self.house_cost

            curr_val = liq_inv + ill_inv

            list_curr_val.append(curr_val)
            list_liq.append(liq_inv)
            list_ill.append(ill_inv)
        return list_curr_val, list_liq, list_ill

    def month_costs(self, year, house_type='htb'):
        "Calculate the amount spend on rent."
        principal = 0
        equity_loan = 0
        non_rent_costs = self.month_non_rent * (self.spend_grow) ** year

        if year + 1 <= self.year_home:
            return self.rent_home + non_rent_costs, principal, equity_loan
        elif year + 1 <= self.year_rent + self.year_home:
            return self.rent_away + non_rent_costs, principal, equity_loan
        else:
            if house_type == 'htb':
                monthly_payment, interest, equity_loan = self.mortgage_htb(house_cost=self.house_cost,
                                                                           r=self.mortgage_rate,
                                                                           mortgage_length=25,
                                                                           deposit=self.deposit)
                principal = monthly_payment - interest
                return interest + non_rent_costs, principal, equity_loan
            elif house_type == 'normal':
                monthly_payment, interest = self.mortgage(house_cost=self.house_cost,
                                                          r=self.mortgage_rate,
                                                          mortgage_length=25,
                                                          deposit=self.deposit)
                principal = monthly_payment - interest
                return interest + non_rent_costs, principal, equity_loan

    @staticmethod
    def yearly_ret(start_val, month_save, r):
        """
        Calculate earnings at the monthly rate.
        """
        curr_val = copy(start_val)
        for i in range(12):
            curr_val = (curr_val + month_save) * (1 + r / 12)
        return curr_val

    @staticmethod
    def stamp_duty_calc(house_cost):
        if house_cost <= 500:
            stamp_duty = 0.05 * (max(house_cost, 300) - 300)
            return stamp_duty
        else:
            sdlt_rates = [0, 0.02, 0.05, 0.1, 0.12]
            sdlt_buckets = [0, 125, 250, 925, 1500, np.inf]
            stamp_duty = 0
            for i in range(len(sdlt_buckets)):
                if house_cost > sdlt_buckets[i + 1]:
                    stamp_duty += (sdlt_buckets[i + 1] - sdlt_buckets[i]) * sdlt_rates[i]
                else:
                    stamp_duty += (house_cost - sdlt_buckets[i]) * sdlt_rates[i]
                    return stamp_duty

    @staticmethod
    def mortgage_htb(house_cost, r, mortgage_length, deposit=0.05):
        """
        Calculate the initial cost plus the monthly interest and principal payment.
        HELP TO BUY.
        """
        mortgage = house_cost * (1 - (deposit + 0.4))
        monthly_payment = mortgage * (r / 12 * (1 + r / 12) ** (mortgage_length * 12)) / (
                    (1 + r / 12) ** (mortgage_length * 12) - 1)
        interest_payment = (monthly_payment * 12 * mortgage_length - mortgage) / (mortgage_length * 12)

        inflation = 0.05
        equity_loan = house_cost * 0.4 * (1 + inflation) ** 5

        return monthly_payment, interest_payment, equity_loan

    @staticmethod
    def mortgage(house_cost, r, mortgage_length, deposit=0.20):
        """
        Calculate the initial cost plus the monthly interest and principal payment.
        NOT HELP TO BUY.
        """
        mortgage = house_cost * (1 - deposit)
        monthly_payment = mortgage * (r / 12 * (1 + r / 12) ** (mortgage_length * 12)) / (
                    (1 + r / 12) ** (mortgage_length * 12) - 1)
        interest_payment = (monthly_payment * 12 * mortgage_length - mortgage) / (mortgage_length * 12)
        return monthly_payment, interest_payment

    def run_scenario(self, scenarios=1000):
        """
        Run a set of random scenarios.
        """
        if len(self.salary_list) != len(self.bonus_list):
            raise Exception("Length of salaries and bonuses not equal!")
        years = len(self.salary_list)
        years_array = np.arange(years + 1)
        list_list_curr = []
        list_list_liq = []
        list_list_ill = []
        for i in range(scenarios):
            scenario_curr, scenario_liq, scenario_ill = self.saving_calc(years)

            list_list_curr.append(scenario_curr)
            list_list_liq.append(scenario_liq)
            list_list_ill.append(scenario_ill)
            if self.show_extra:
                plt.plot(years_array, scenario_curr, linewidth=0.1, color='b')

        df = pd.DataFrame(list_list_curr).T
        df_liq = pd.DataFrame(list_list_liq).T
        df_ill = pd.DataFrame(list_list_ill).T

        df['Mean'] = df.mean(axis=1)
        df['Std'] = df.std(axis=1)
        df['Mean - 2 sigma'] = df.mean(axis=1) - 2 * df.std(axis=1)
        df['Mean + 2 sigma'] = df.mean(axis=1) + 2 * df.std(axis=1)

        df_liq['Mean'] = df_liq.mean(axis=1)
        df_ill['Mean'] = df_ill.mean(axis=1)

        plt.xlabel('Years')
        plt.ylabel('Net Worth £ (k)')

        plt.plot(years_array, df['Mean'], '--', linewidth=2, color=self.colour_main, label='Average: ' + self.label)
        if self.show_extra:
            plt.plot(years_array, df['Mean + 2 sigma'], '--', linewidth=1, color='red', label='Mean + 2 sigma')
            plt.plot(years_array, df['Mean - 2 sigma'], '--', linewidth=1, color='red', label='Mean - 2 sigma')
        if self.show_breakdown:
            plt.plot(years_array, df_liq['Mean'], '--', linewidth=2, color='green', label='Liquid Assets')
            plt.plot(years_array, df_ill['Mean'], '--', linewidth=2, color='purple', label='Illiquid Assets')

        plt.legend(loc='best')

        return df


# list_salary = [70, 90, 100, 110, 130, 145, 165]
# list_bonus = [70,80,100,120,120,130,140]    # Optimistic Scenario
# list_bonus = [i * 0.5 for i in list_salary]  # Multiple of salary|

# test_class = MoneySimulator(salary_list=list_salary, bonus_list=list_bonus, initial_saving=60)
# net_income = test_class.tax_ni(salary=65, bonus=60, logs=True)
# list_net_worth = test_class.saving_calc(7)

# df_scenario = test_class.run_scenario()

# stamp_duty = test_class.stamp_duty_calc(500)
# monthly_payment, interest, equity_loan = test_class.mortgage_htb(500, r=0.0359, mortgage_length=25) 
# monthly_payment, interest = test_class.mortgage(700, r=0.02, mortgage_length=25) 

# net_income = test_class.tax_ni(salary = 65, bonus = 65, logs=True)
# net_bonus = net_income - test_class.tax_ni(salary = 65, bonus = 0, logs=False)


# sim_class = MoneySimulator(initial_saving=0, salary_list=0, bonus_list=0)
# after_tax_olha = sim_class.tax_ni(salary=58, bonus=0)
