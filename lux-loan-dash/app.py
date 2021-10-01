import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# import the csv into a dataframe
lux_loan = pd.read_csv('LuxuryLoanPortfolio.csv')


# create the dataframe for first plot
term_df = lux_loan.groupby(['purpose']).agg({'loan_id': ['nunique'],
                                             'duration years': ['mean'],
                                             'funded_amount': ['mean']}).reset_index()

term_df.columns = ["_".join(a) for a in term_df.columns.to_flat_index()]

term_df.rename(columns={'purpose_': 'purpose', 
                             'loan_id_nunique': 'number_of_loans'}, inplace=True)


term_df_melt = term_df.melt(id_vars=['purpose'], 
                value_vars=['number_of_loans', 'duration years_mean', 'funded_amount_mean'], 
                var_name=['metric'],
                value_name='value')


# create the dataframe for second plot
time_series_df = lux_loan.groupby(['funded_date', 'purpose',
                                   '10 yr treasury index date funded',
                                   'interest rate percent']).agg({'loan_id': ['nunique']}).reset_index()

time_series_df.columns = ["_".join(a) for a in time_series_df.columns.to_flat_index()]

time_series_df = time_series_df[['funded_date_', 
                                               'purpose_', 
                                               '10 yr treasury index date funded_',
                                               'interest rate percent_']]

time_series_df.rename(columns={'funded_date_': 'funded_date', 
                             'purpose_': 'purpose',
                             '10 yr treasury index date funded_': '10 yr treasury index date funded',
                             'interest rate percent_': 'interest rate percent'}, inplace=True)

def f(x):
    return x.div(100)

time_series_df[['10 yr treasury index date funded',
                'interest rate percent']] = time_series_df[['10 yr treasury index date funded',
                                                             'interest rate percent']].apply(f)


# create the dataframe for third plot
lux_loan['funding_year'] = pd.DatetimeIndex(lux_loan['funded_date']).year

prop_df = lux_loan[['funding_year', 'BUILDING CLASS CATEGORY', 'property value', 'funded_amount', 'purpose']]



############################################################

# render the first plot
fig = px.bar(term_df_melt, x="purpose", y="value", color="purpose", barmode="group",
             facet_row="metric", 
            #  facet_col="xx",
             category_orders={"purpose": ["boat", "commerical property", "home", "plane"]
                              },
             width=800, 
             height=750)


fig.update_yaxes(matches=None)

# render the seond plot

time_fig = px.line(time_series_df, 
              x="funded_date", 
              y=time_series_df.columns, 
              # color="purpose",
              # facet_row="purpose_", 
              facet_col="purpose",
              facet_col_wrap = 2,
              width=900, 
              height=650)

time_fig.update_yaxes(matches=None, tickformat='.0%')

# render the third plot 

dot_fig = px.strip(prop_df, 
             x="funding_year",
             y="property value",
             color="BUILDING CLASS CATEGORY",
             facet_col = "funding_year",
             facet_col_wrap = 3,
             hover_data={'funded_amount', 'purpose'},
            #  points = "all",
             width=1100, 
             height=1000)

dot_fig.update_yaxes(matches=None)
dot_fig.update_xaxes(matches=None)


# components

# components for first plot
app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='This is my first interesting plot.'),

        html.Div(children='''
            This shows that luxury items like boats and planes may have high funding requirement but have quite a low time to payback.'''),
        
        html.Div(html.Br()),
        
        html.Div(children= '''If such loans are shown to have lower risk and faster time to payback, it might be worth spending more effort and resources to market these to eligible customers.
        '''),

        dcc.Graph(
            id='graph1',
            figure=fig
        ),  
    ]),

# components for second plot
    html.Div([
        html.H1(children='This is my second interesting plot.'),

        html.Div(children='''
            This shows a clear fluctuation of interest rates with 10 year treasury index rates. The interest rates do not differ much by purpose.
        '''),

        html.Div(html.Br()),

         html.Div(children='''
        This might be 
        an opportunity for increasing revenue by means of personalised interest rates according to a user's credit score and risk profile.
        '''),       

        dcc.Graph(
            id='graph2',
            figure=time_fig
        ),  
    ]),

# components for third plot
    html.Div([
        html.H1(children='This is my third interesting plot.'),

        html.Div(children='''
            This shows a clear outlier in terms of funded amount in 2018, which was for a plane purchase.
        '''),

        dcc.Graph(
            id='graph3',
            figure=dot_fig
        ),  
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)