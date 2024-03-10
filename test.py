import pandas as pd
import numpy as np
import datetime

# rates = pd.read_excel("QUOTES.xlsx")
# cashflow = pd.read_excel("cashflow.xlsx")
# future_value = pd.read_excel("future_value.xlsx")
def calculate_discounted_cashflow(rates, cashflow,future_value):
    rates2 = rates.copy()
    rates["Var1"] = datetime.datetime.now().year -1 - rates["Year"]
    rates["Var2"] = rates["Var1"] * 12
    rates["Var3"] = np.where(rates["Period"] <700, rates["Var2"] + 1 + rates["Period"] -1,1)
    rates["Var4"] = rates["Var3"]-1
    rates["Var5"] = (rates["Var3"]/12) - (1/24)
    rates["Left_Key"] = rates["Year"].astype(str) +  (rates["Var4"]+13).astype(str) + rates["Currency"]
    rates["Left_Key2"] = rates["Year"].astype(str) +  rates["Var2"].astype(str) + rates["Currency"]
    #print(1/(((1+0.0302091)**9.0416667)/((1+0.0294893048)**9)))
    rates2["avg"] = rates2.groupby('Year')["Rate"].transform(lambda x : x.rolling(2,min_periods=1).mean())
    rates2["Right_Key"] = rates2["Year"].astype(str) + rates2["Period"].astype(str) + rates["Currency"]
    avg_joined = pd.merge(rates, rates2, left_on='Left_Key', right_on='Right_Key', how='left').drop(['Right_Key','Year_y','Period_y','Rate_y'], axis=1)
    rate_joined = pd.merge(avg_joined, rates2, left_on='Left_Key2', right_on='Right_Key', how='left')
    rate_joined["disc_rate"] = 1/(((1+rate_joined["avg_x"])**rate_joined["Var5"])/((1+rate_joined["Rate"])**rate_joined["Var1"]))
    rate_joined.fillna(0,inplace=True)
    rate_joined.drop(['Rate_x','Var1','Var2','Var3','Var4','Var5','Left_Key','Left_Key2','Currency_y','avg_x','Year','Period','Currency','Rate','avg_y','Right_Key'], axis=1,inplace=True)
    rate_joined["key"] = rate_joined["Year_x"].astype(str)+rate_joined["Period_x"].astype(str)+rate_joined["Currency_x"]
    cf_joined = pd.merge(future_value, cashflow, left_on='Group', right_on='UoA', how='left')
    cf_joined["key"] = cf_joined["Year"].astype(str)+cf_joined["Period"].astype(str)+cf_joined["Currency"]
    all_joined = pd.merge(cf_joined, rate_joined, left_on='key', right_on='key', how='left')
    all_joined["disc_amount"] = all_joined["Value"]*all_joined["CF_Pattern"]*all_joined["disc_rate"]
    all_joined.drop(['Year','Currency','Value','UoA','CF_Pattern','key','Year_x','Period_x','Currency_x','disc_rate'],axis=1,inplace=True)
    #rates2.to_excel("avg.xlsx")
    #rates.to_excel("disc_rates.xlsx")
    #avg_joined.to_excel("joined.xlsx")
    #rate_joined.to_excel("rate_joined.xlsx",index=False)
    #all_joined.to_excel("all_joined.xlsx",index=False)
    discounted_cashflows = []
    for i in range(len(all_joined['disc_amount'])):
        cf = {"Group":all_joined["Group"][i],"Period":int(all_joined["Period"][i]),"Amount":float(all_joined["disc_amount"][i])}
        discounted_cashflows.append(cf)
    return discounted_cashflows








