import pandas as pd

def calculate_discounted_cashflow(future_value, cashflow_pattern,interest_rates):
    discounted_cashflows = []
    for j in range(future_value["Group"].nunique()):
        period_based_cashflows = {"Group":future_value["Group"][j],"Value":[future_value["Value"][j] * ratio for ratio in cashflow_pattern["CF_Pattern"]]}
        for i in range(len(period_based_cashflows["Value"])):
            discount_factor = 1 / (1 + interest_rates["Rates"][i])
            discounted_cashflow = {"Group":period_based_cashflows["Group"],"Period":i,"Present_Value":period_based_cashflows["Value"][i] * discount_factor}
            discounted_cashflows.append(discounted_cashflow)
    print(discounted_cashflows.__len__())
    return discounted_cashflows

