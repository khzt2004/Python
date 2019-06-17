# https://www.reddit.com/r/learnpython/comments/5wnypp/how_to_do_an_if_case_statement_in_pandas/
import pandas as pd
import numpy as np

# read in the csv file
df = pd.read_csv('pivot_raw_data.csv')

# unpivot using melt
df_melt = pd.melt(df, 
id_vars=['Date_of_Week',
'Year', 'Month', 'Channel', 'Brand', 'Country', 'Category'],
value_vars = ['NMV', 'Item', 'ASP', 'PV'],
var_name = 'Metric', value_name = 'Values')

# pivot out and aggregate values column
df_pivot = pd.pivot_table(df_melt, values='Values', index=['Date_of_Week',
'Year', 'Month', 'Channel', 'Brand', 'Country', 'Category'],
columns=['Metric'], aggfunc=np.sum)

# reset the index after pivoting
df_pivot = df_pivot.reset_index()

# group by year and show NMV
df_year_NMV = df_pivot.groupby(['Year']).agg({'NMV':['sum','mean'],
                              'PV': ['mean']})

df_year_NMV.loc[df_year_NMV['Year'] == 2017] = 'Old'
df_year_NMV.loc[df_year_NMV['Year'] == 2018] = 'Current'


# pivot out using the category column and aggregate the values column
df_category_pivot = pd.pivot_table(df_melt, values='Values', index=['Date_of_Week',
'Year', 'Month', 'Channel', 'Brand', 'Country', 'Metric'],
columns=['Category'], aggfunc=np.sum)

# reset the index after pivoting
df_category_pivot = df_category_pivot.reset_index()
