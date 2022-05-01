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
        self.dict_df = None
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

        self.colour_main = wealth_config.color_main

        house_label = 'No house. ' if len(salary_list) < self.year_home + self.year_rent\
            else self.house_type + ' in ' + str(self.year_home + self.year_rent) + 'y at ' \
                 + str(self.house_cost) + 'k. '
        btl_label = 'No BTL. ' if len(wealth_config.btl_dict) == 0 else str(len(wealth_config.btl_dict)) \
                                                                        + ' BTL house(s). '
        rent_label = str(self.year_home) + 'y home. ' + str(self.year_rent) + 'y rent. '

        self.label = house_label + btl_label + rent_label

        self.show_extra = wealth_config.show_extra
        self.show_breakdown = wealth_config.show_breakdown

    @staticmethod
    def tax_calc(salary: float, bonus: float, logs: bool = False) -> (float, str):
        """
        Calculate the amount left after tax.
        """
        tax_buckets = [0, 12.57, 50.27, 150, np.inf]
        tax_bands = ['Personal Allowance', 'Basic', 'Higher', 'Additional']
        tax_rate = [0, 0.2, 0.4, 0.45]
        tax_band = 'Personal Allowance'

        tax_income = salary + bonus
        tax_paid = 0

        if tax_income > 100:
            tax_paid += tax_rate[1] * (min(tax_income, 100 + 2 * tax_buckets[1]) - 100)

        for i in range(len(tax_buckets)):
            if tax_income > tax_buckets[i + 1]:
                tax_paid += (tax_buckets[i + 1] - tax_buckets[i]) * tax_rate[i]
            else:
                tax_band = tax_bands[i]
                tax_paid += (tax_income - tax_buckets[i]) * tax_rate[i]
                if logs:
                    print(tax_band)
                return tax_paid, tax_band

    @staticmethod
    def ni_calc(salary: float, bonus: float) -> float:
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

    def tax_ni(self, salary: float, bonus: float, logs: bool = False) -> float:
        """
        Find out how much tax + ni you've paid.
        """
        tax_paid, tax_band = self.tax_calc(salary, bonus)
        ni_paid = self.ni_calc(salary, bonus)

        net_income = salary + bonus - ni_paid - tax_paid
        if logs:
            print(f'The tax paid is {tax_paid}')
            print(f'The National Insurance paid is {ni_paid}')
            print(f'Take home income is {net_income}')
        return net_income

    def saving_calc(self, years: int) -> dict:
        """
        Calculate how much I will have saved of the cash and bonus.
        """
        list_curr_val = [self.initial_saving]
        list_liq = [self.initial_saving]
        list_ill = [0]
        liq_inv = self.initial_saving
        ill_inv = 0
        list_rental_income = [0]
        list_btl_capital_val = [0]
        list_btl_costs = [0]

        for i in range(years):

            btl_mortgage_payment = 0
            btl_interest_payment = 0
            btl_one_time_costs = 0
            rental_income = 0
            shift_liq_ill = 0

            if len(wealth_config.btl_dict) > 0:
                for year_purchased, list_info in wealth_config.btl_dict.items():
                    mortgage, interest, one_time, initial_dep, rent = self.btl_finance(year=i,
                                                                                       year_purchased=year_purchased,
                                                                                       list_info=list_info)
                    btl_mortgage_payment += mortgage * 12  # per year
                    btl_interest_payment += interest * 12  # per year
                    btl_one_time_costs += one_time  # per year
                    rental_income += rent  # per month
                    shift_liq_ill += initial_dep

            net_sal = self.tax_ni(salary=self.salary_list[i] + (rental_income - btl_interest_payment), bonus=0)

            bonus_rand = max(np.random.normal(self.bonus_list[i], self.bonus_list[i] * self.bonus_std_prop), 0)
            net_bonus = self.tax_ni(salary=self.salary_list[i], bonus=bonus_rand) - net_sal

            net_sal = net_sal - (btl_mortgage_payment - btl_interest_payment)
            # Take into account the fact that interest is tax-deductible but mortgage principal isn't

            sunk_cost_month, principal_month, equity_loan = self.month_costs(i)
            monthly_save = net_sal / 12 - sunk_cost_month

            liq_inv -= shift_liq_ill
            ill_inv += shift_liq_ill  # Deposit shifts from liquid to illiquid capital

            liq_inv = self.yearly_ret(start_val=liq_inv,
                                      month_save=monthly_save,
                                      r=np.random.normal(self.r_avg, self.r_avg))
            ill_inv = self.yearly_ret(start_val=ill_inv,
                                      month_save=principal_month + btl_mortgage_payment / 12,
                                      r=np.random.normal(self.house_inf, self.house_inf_std))

            liq_inv += net_bonus * (1 - self.bonus_spend_rate) - btl_one_time_costs

            if i + 1 == 5 + self.year_home + self.year_rent and self.house_type == 'htb':
                liq_inv = liq_inv - equity_loan
                ill_inv = ill_inv + equity_loan

            if i + 1 == self.year_home + self.year_rent:
                if len(wealth_config.btl_dict) != 0 and i + 1 < min(wealth_config.btl_dict.keys()):
                    first_home = True
                else:
                    first_home = False
                liq_inv = liq_inv - (self.stamp_duty_calc(self.house_cost, first_home=first_home)
                                     + 5 + self.deposit * self.house_cost)
                ill_inv += self.deposit * self.house_cost

            curr_val = liq_inv + ill_inv

            list_curr_val.append(curr_val)
            list_liq.append(liq_inv)
            list_ill.append(ill_inv)

            list_btl_costs.append(btl_interest_payment + btl_one_time_costs)
            list_btl_capital_val.append(btl_mortgage_payment + shift_liq_ill)
            list_rental_income.append(rental_income)

        data = {
            'Current Value': list_curr_val,
            'Liquid': list_liq,
            'Illiquid': list_ill,
            'BTL Costs': list_btl_costs,
            'BTL Capital': list_btl_capital_val,
            'Rental Income': list_rental_income
        }

        return data

    def month_costs(self, year: int, house_type: str = 'htb') -> (float, float, float):
        """
        Calculate the amount spend on rent.
        """
        principal = 0
        equity_loan = 0
        non_rent_costs = self.month_non_rent * self.spend_grow ** year

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
                monthly_payment, interest = self.mortgage_normal(house_cost=self.house_cost,
                                                          r=self.mortgage_rate,
                                                          mortgage_length=25,
                                                          deposit=self.deposit)
                principal = monthly_payment - interest
                return interest + non_rent_costs, principal, equity_loan

    @staticmethod
    def yearly_ret(start_val: float, month_save: float, r: float) -> float:
        """
        Calculate earnings at the monthly rate.
        """
        curr_val = copy(start_val)
        for i in range(12):
            curr_val = (curr_val + month_save) * (1 + r / 12)
        return curr_val

    @staticmethod
    def stamp_duty_calc(house_cost: float, main_residence: bool = True, first_home: bool = True) -> float:
        """
        Calculate the stamp duty when buying a house
        """
        if house_cost <= 500 and first_home:
            stamp_duty = 0.05 * (max(house_cost, 300) - 300)
            return stamp_duty
        else:
            sdlt_rates = [0, 0.02, 0.05, 0.1, 0.12]
            if not main_residence:
                sdlt_rates = [r + 0.03 for r in sdlt_rates]
            sdlt_buckets = [0, 125, 250, 925, 1500, np.inf]
            stamp_duty = 0
            for i in range(len(sdlt_buckets)):
                if house_cost > sdlt_buckets[i + 1]:
                    stamp_duty += (sdlt_buckets[i + 1] - sdlt_buckets[i]) * sdlt_rates[i]
                else:
                    stamp_duty += (house_cost - sdlt_buckets[i]) * sdlt_rates[i]
                    return stamp_duty

    @staticmethod
    def mortgage_htb(house_cost: float, r: float, mortgage_length: float, deposit: float = 0.05) -> \
            (float, float, float):
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
    def mortgage_normal(house_cost: float, r: float, mortgage_length: int, deposit: float = 0.20) -> (float, float):
        """
        Calculate the initial cost plus the monthly interest and principal payment.
        NOT HELP TO BUY.
        """
        mortgage = house_cost * (1 - deposit)
        monthly_payment = mortgage * (r / 12 * (1 + r / 12) ** (mortgage_length * 12)) / (
                (1 + r / 12) ** (mortgage_length * 12) - 1)
        interest_payment = (monthly_payment * 12 * mortgage_length - mortgage) / (mortgage_length * 12)
        return monthly_payment, interest_payment

    def btl_finance(self, year: int, year_purchased: int, list_info: list) -> (float, float, float, float):
        """
        Calculate the net cost of BTL in any given year.
        """
        house_price = list_info[0]
        deposit = list_info[1]
        rent = list_info[2]

        if year < year_purchased:
            return 0, 0, 0, 0, 0

        elif year == year_purchased:
            other_costs_buy = 5
            stamp_duty = self.stamp_duty_calc(house_cost=house_price, first_home=False, main_residence=False)
            initial_dep = deposit
        else:
            other_costs_buy = 0
            stamp_duty = 0
            initial_dep = 0

        total_one_time = stamp_duty + other_costs_buy

        mortgage_payment, interest_payment = self.mortgage_normal(house_cost=house_price,
                                                           r=self.mortgage_rate,
                                                           mortgage_length=25,
                                                           deposit=deposit / house_price)

        other_costs_ongoing = rent * 0.1  # Estimated other costs as 10% of the rent.
        return mortgage_payment, interest_payment + other_costs_ongoing, total_one_time, initial_dep, rent

    def run_scenario(self, scenarios: int = 1000) -> pd.DataFrame:
        """
        Run a set of random scenarios.
        """
        if len(self.salary_list) != len(self.bonus_list):
            raise Exception("Length of salaries and bonuses not equal!")
        years = len(self.salary_list)
        years_array = np.arange(years + 1)

        data_str = ['Current Value', 'Liquid', 'Illiquid', 'BTL Capital', 'BTL Costs', 'Rental Income']
        data_all_scenario = {x: [] for x in data_str}

        for i in range(scenarios):
            data_scenario = self.saving_calc(years)

            for cat_data in data_str:
                data_all_scenario[cat_data].append(data_scenario[cat_data])

            if self.show_extra:
                plt.plot(years_array, data_scenario['Current Value'], linewidth=0.1, color='b')

        dict_df = {}
        for cat in data_str:
            dict_df[cat] = pd.DataFrame(data_all_scenario[cat]).T

        df = pd.DataFrame(data={'Mean': dict_df['Current Value'].mean(axis=1),
                                'Liquid': dict_df['Liquid'].mean(axis=1),
                                'Illiquid': dict_df['Illiquid'].mean(axis=1),
                                'Rental Income': dict_df['Rental Income'].mean(axis=1),
                                'BTL Costs': dict_df['BTL Costs'].mean(axis=1),
                                'BTL Capital': dict_df['BTL Capital'].mean(axis=1),
                                'Mean - 2 sigma': dict_df['Current Value'].mean(axis=1) - 2 *
                                                  dict_df['Current Value'].std(axis=1),
                                'Mean + 2 sigma': dict_df['Current Value'].mean(axis=1) + 2 *
                                                  dict_df['Current Value'].std(axis=1),
                                'Std': dict_df['Current Value'].std(axis=1)})

        plt.xlabel('Years')
        plt.ylabel('Net Worth £ (k)')

        plt.plot(years_array, df['Mean'], '--', linewidth=2, color=self.colour_main, label='Average: ' + self.label)
        if self.show_extra:
            plt.plot(years_array, df['Mean + 2 sigma'], '--', linewidth=1, color='red', label='Mean + 2 sigma')
            plt.plot(years_array, df['Mean - 2 sigma'], '--', linewidth=1, color='red', label='Mean - 2 sigma')
        if self.show_breakdown:
            plt.plot(years_array, df['Liquid'], '--', linewidth=2, color='green', label='Liquid Assets')
            plt.plot(years_array, df['Illiquid'], '--', linewidth=2, color='purple', label='Illiquid Assets')

        plt.legend(loc='best')

        self.dict_df = dict_df

        return df

    def get_all_data(self) -> dict:
        """
        Access the complete results of the simulation.
        """
        return self.dict_df
