import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.title("Exploratory Dashboard")

st.markdown("Instructions: open up terminal")
st.markdown("enter this: streamlit run streamlit_property_rent_buy.py")
st.markdown("Reference app: https://netlify.causal.app/buy")
st.markdown("https://medium.com/nightingale/building-an-interactive-dashboard-in-less-than-50-lines-of-code-494b30a31905")

annual_investment_returns = st.number_input('Insert a number - annual investment returns in percent')
annual_property_appeciation_input = st.number_input('Insert a number - annual property appreciation in percent')

# buy property variables
property_cost = 600000
annual_property_appreciation = annual_property_appeciation_input/100
n_years_in_property = 8
final_property_value = property_cost*(1+annual_property_appreciation)**float(n_years_in_property)
down_payment = 0.1*property_cost
one_off_costs = 0.06*property_cost
loan_term = n_years_in_property
annual_loan_repayment = (property_cost - (down_payment+one_off_costs)) / loan_term


# rent property variables
initial_deposit = down_payment + one_off_costs
monthly_rent = 2000
rent_appreciation = 0.03
annual_rent = 2000*12
investment_annual_returns = annual_investment_returns/100

# calculate property dataframe
years_in_property_list = pd.Series(range(0,n_years_in_property))
years_in_loan = pd.Series(reversed(range(0,n_years_in_property)))
annual_property_appreciation_list = pd.Series([annual_property_appreciation]*n_years_in_property)
downpayment_one_off_costs = pd.Series([(down_payment+one_off_costs)] + [0] * (n_years_in_property-1))
annual_loan_repayment_costs = pd.Series([annual_loan_repayment]*n_years_in_property)
current_property_value_list = []
final_property_value_list = []

for i in years_in_property_list:
  years_in_property= i,
  current_property_value = property_cost*(1+annual_property_appreciation)**float(i)
  final_property_value = property_cost*(1+annual_property_appreciation)**float(i+1)

  current_property_value_list.append(current_property_value)
  final_property_value_list.append(final_property_value)


property_df = pd.DataFrame({
    'property_cost': current_property_value_list,
    'annual_property_appreciation': annual_property_appreciation_list,
    'year_number': years_in_property_list,
    'final_property_value': final_property_value_list,
    'years_left_loan': years_in_loan,
    'downpayments_oneoff_costs': downpayment_one_off_costs,
    'annual_loan_repayment_costs': annual_loan_repayment_costs,
    'net_wealth_buy_property': final_property_value_list - (downpayment_one_off_costs + annual_loan_repayment_costs)
}
)

# calculate rent dataframe
years_in_rental_property_list = pd.Series(range(0,n_years_in_property))
years_in_rental = pd.Series(reversed(range(0,n_years_in_property)))
investment_value = [(down_payment+one_off_costs)]
current_investment_value_list = []
final_investment_value_list = []
rental_cost_list = []

for i in years_in_property_list:
  years_in_rental_property = i,
  current_investment_value = (down_payment+one_off_costs+annual_loan_repayment_costs[i])*(1+investment_annual_returns)**float(i)
  final_investment_value = (down_payment+one_off_costs+annual_loan_repayment_costs[i])*(1+investment_annual_returns)**float(i+1)
  rental_cost = annual_rent*(1+rent_appreciation)**(float(i))

  current_investment_value_list.append(current_investment_value)
  final_investment_value_list.append(final_investment_value)
  rental_cost_list.append(rental_cost)

rent_invest_df = pd.DataFrame({
    'rental_cost': pd.Series(rental_cost_list),
    'annual_rent_appreciation': rent_appreciation,
    'year_number': years_in_property_list,
    'current_investment_value': current_investment_value_list,
    'final_investment_value': final_investment_value_list,
    'net_wealth_rent_property': pd.Series(final_investment_value_list) - pd.Series(rental_cost_list)
}
)


st.markdown("Data for buying a property")
if st.checkbox('Show Data for buying property'):
   st.dataframe(property_df)


st.markdown("Data for renting a property")
if st.checkbox('Show Data for renting property'):
   st.dataframe(rent_invest_df)

# area plot
wealth_plot_comparison = property_df[['year_number', 'net_wealth_buy_property']].merge(rent_invest_df[['year_number', 'net_wealth_rent_property']], left_on='year_number', right_on='year_number')
melted_wealth_plot_comparison = pd.melt(wealth_plot_comparison, 
                 id_vars = 'year_number', 
                 value_vars = ['net_wealth_buy_property', 'net_wealth_rent_property'],
                 var_name = 'attribute', 
                 value_name = 'net_wealth')

fig = px.line(melted_wealth_plot_comparison, x="year_number", y="net_wealth", color = 'attribute')
st.plotly_chart(fig, use_container_width=True)