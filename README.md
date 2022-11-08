# Wealth Simulator
Wealth Simulator is a class that enables you to track your net worth in the UK
given a set of scenarios.

Currently, supported are investing in the equity market, investing in buy to let 
property with a mortgage that repays principle, and buying a house to live in.

The code runs a large number of scenarios with various different random variables.
Salary each year is treated as a static variable, however bonuses, market performance,
and house price change are all treated as random variables.

The code fully takes into account income tax and national insurance
calculations as they will be from 2022 onwards.

## Installation
Following imports required:

```python
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from copy import copy
```


## Usage:
```python
from wealth_simulator import MoneySimulator

list_salary: list = []
list_bonus: list = []
initial_saving: float = 0

wealth_class = MoneySimulator(salary_list=list_salary,
                              bonus_list=list_bonus,
                              initial_saving=initial_saving)
df = wealth_class.run_scenario()
```
In `wealth_config.py` the vast majority of the parameters are located for the
simulation. Explanations for params also here.

`list_salary` and `list_bonus` should be each be expressed as a list of floats, 
representing the salary/bonus per year that is expected in thousands.

The file `wealth_run.py` contains examples on how to run the code.

A graph with the results is plotted. 

The df from `wealth_class.run_scenario()` contains the results. 
The results of each simulation can also be accessed by running `wealth_class.get_all_data()`

## Standalone Methods:
Use `wealth_class.tax_ni(**args)` to calculate the total tax and national insurance
paid in a given tax year.

Use `wealth_class.stamp_duty_calc(**args)` to calculate the amount of stamp duty paid 
on a property.

Use `wealth_class.mortgage(**args)` and `wealth_class.mortgage_htb(**args)`
to calculate the monthly payments on interest and principal.

## Contributing:
Pull requests are welcome. For major changes,
please open an issue first to discuss what you would like to change.

## License:
[MIT](https://choosealicense.com/licenses/mit/)
