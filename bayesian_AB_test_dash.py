import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.figure_factory as ff

import pymc3
import numpy as np
import pandas as pd

#This is the known data: impressions and conversions for the Control and Test set
imps_ctrl,convs_ctrl=8500, 1410 
imps_A,convs_A=8500, 1500

# Calculating the parameters for posterior (prior is assumed to be 1,1 - the uninformed guess)
alpha_ctrl, beta_ctrl = 1 + convs_ctrl, 1 + imps_ctrl - convs_ctrl
alpha_A, beta_A = 1 + convs_A, 1 + imps_A - convs_A

# Draw 10000 samples from the distribution
ctrl_simulation = np.random.beta(alpha_ctrl,beta_ctrl,10000)
A_simulation = np.random.beta(alpha_A,beta_A,10000)

simulations = [ctrl_simulation, A_simulation]
simulations_hpd = [pymc3.stats.hpd(ctrl_simulation, alpha=0.05), pymc3.stats.hpd(A_simulation, alpha=0.05)]

# Scoring to determine the best variant
score = np.zeros(2)
for i in range(10000):
    test = [ctrl_simulation[i], A_simulation[i]]
    test = pd.Series(test)
    rankings = test.rank(ascending=False)
    
    j = 0
    for value in rankings:
        if value == 1.0:
            score[j] += 1
        j += 1
score = np.round(score/sum(score) * 100,2)
indices = np.argsort(score)[::-1]
best = indices[0]

variants = ['Control', 'A', 'B', 'C']
test_variants = ['f(A-ctrl)', 'f(B-ctrl)', 'f(C-ctrl)']
plotly_colours = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)', 'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                  'rgb(148, 103, 189)', 'rgb(140, 86, 75)', 'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                  'rgb(188, 189, 34)', 'rgb(23, 190, 207)']
threshold = 0.001
rope = 0.001

class variantsCount():
    no_of_variants = 2
    def updateVariants(self, variants_count):
        self.no_of_variants = int(variants_count)

class statesCount():
    all_states = [State('input_control_imps', 'value'), State('input_control_conv', 'value'),
                  State('input_A_imps', 'value'), State('input_A_conv', 'value')]
    def resetStates(self):
        self.all_states = [State('input_control_imps', 'value'), State('input_control_conv', 'value'),
                    State('input_A_imps', 'value'), State('input_A_conv', 'value')]
    def updateStates(self, state):
        self.all_states.append(state)
        
# Initialise the input states class object
variants_total = variantsCount()
states_total = statesCount()

# Calculate expected loss for all the variants
loss = np.zeros(2)
for i in range(len(loss)):
    if i != indices[0]: # If not the best variant
        loss_val = ((simulations[best] - simulations[i])/simulations[0])[simulations[best] > simulations[i]]
        loss[i] += np.mean(loss_val) * np.mean(simulations[best] > simulations[i])
    else: 
        for k in [j for j in range(2) if j != best]: # Sum losses for best variant
            loss_val = ((simulations[k] - simulations[best])/simulations[0])[simulations[k] > simulations[best]]
            if loss_val.size == 0:
                loss[best] += 0
            else:
                loss[best] += np.mean(loss_val) * np.mean(simulations[k] > simulations[best])

d = {
    'Variant': ['Control', 'A'],
    'Samples': [imps_ctrl, imps_A],
    'Conversions': [convs_ctrl, convs_A],
    'Conversion Rate (%)': np.round([convs_ctrl/imps_ctrl, convs_A/imps_A], 5) * 100,
    'Probability to be Best (%)': np.round(score,2),
    'Expected Loss (%)': np.nan_to_num(np.round(loss * 100,2)) #np.nan_to_num(np.round([ctrl_loss, A_loss, B_loss], 2))
}
df = pd.DataFrame(data=d)

dist_plots = ff.create_distplot(simulations ,variants[:2], show_hist = False, show_rug = False)
dist_plots.layout.update(legend = {'traceorder': 'normal'})
dist_plots.layout.update(title='Posterior simulation of variants')
dist_plots.layout.title.update(x=0.5)

simulations_diff = A_simulation - ctrl_simulation

dist_plots_diff = ff.create_distplot([simulations_diff], [test_variants[0]], show_hist = False, show_rug = False, colors=plotly_colours[1:])
dist_plots_diff.layout.update(legend = {'traceorder': 'normal'})
dist_plots_diff.layout.update(title='Posterior simulation of difference (Expected Loss)')
dist_plots_diff.layout.title.update(x=0.5)

dist_plots_rope = ff.create_distplot([simulations_diff], [test_variants[0]], show_hist = False, show_rug = False, colors=plotly_colours[best:])
dist_plots_rope.layout.update(legend = {'traceorder': 'normal'})
dist_plots_rope.layout.update(title='Posterior simulation of difference (ROPE)') # ROPE: Region of Practical Equivalence
dist_plots_rope.layout.title.update(x=0.5)

rope = 0.001

lines_loss = [
    {
        'type': 'line',
        'yref': 'paper',
        'x0': threshold,
        'x1': threshold,
        'y0': 0,
        'y1': 1,
        'line': {
            'color': 'rgb(0, 0, 0)',
            'width': 3,
            'dash': 'dash'
        }
    }
]    

for i in range(2):
    lines_loss.append({
        'type': 'line',
        'yref': 'paper',
        'x0': loss[i],
        'x1': loss[i],
        'y0': 0,
        'y1': 1,
        'line': {
            'color': plotly_colours[i],
            'width': 3
        }
    })

lines_rope = [
    {
        'type': 'line',
        'yref': 'paper',
        'x0': 0,
        'x1': 0,
        'y0': 0,
        'y1': 1,
        'line': {
            'color': 'rgb(0, 0, 0)',
            'width': 3
        }
    },
    {
        'type': 'line',
        'yref': 'paper',
        'x0': -rope,
        'x1': -rope,
        'y0': 0,
        'y1': 1,
        'line': {
            'color': 'rgb(0, 0, 0)',
            'width': 3,
            'dash': 'dash'
        }
    },
    {
        'type': 'line',
        'yref': 'paper',
        'x0': rope,
        'x1': rope,
        'y0': 0,
        'y1': 1,
        'line': {
            'color': 'rgb(0, 0, 0)',
            'width': 3,
            'dash': 'dash'
        }
    }
] 

hpd = pymc3.stats.hpd(simulations_diff)
lines_rope.append({
    'type': 'line',
    'yref': 'paper',
    'x0': hpd[0],
    'x1': hpd[1],
    'y0': 0,
    'y1': 0,
    'line': {
        'color': plotly_colours[best],
        'width': 3
    }
})

if (hpd[1] < -rope):
    winning_str = 'Variant ' +  variants[best] + ' is the winner!'
    explanation_str = 'Since the HPD lies outside the ROPE and is negative, the recommendation is to implement the control variant.'
    rope_str = "End the experiment. Implement the control variant."
elif (hpd[0] > rope):
    winning_str = 'Variant ' +  variants[best] + ' is the winner!'
    explanation_str = 'Since the HPD lies outside the ROPE and is positive, the recommendation is to implement variant {}.'.format(variants[best])
    rope_str = "End the experiment. Implement variant {}.".format(variants[best])
elif (hpd[0] > -rope) & (hpd[1] < rope):
    winning_str = 'Both variants are equivalent.'
    explanation_str = 'Since the HPD lies solely inside the ROPE, the recommendation is to implement either variant.'
    rope_str = "End the experiment. Implement either variant."
else: 
    winning_str = 'No clear winner.'
    explanation_str = 'Since the HPD lies both inside and outside the ROPE, the recommendation is to keep testing as the results are inconclusive.'
    rope_str = "Continue the experiment as the results are inconclusive."

baseline = convs_ctrl/imps_ctrl
hpd_lower_percent = hpd[0]/baseline * 100
hpd_higher_percent = hpd[1]/baseline * 100
if variants[best] != 'Control':
    desc_str = "The 95% high posterior density (HPD) of the distribution of differences between the control variant and variant {} is from {:.5f} to {:.5f} ({}{:.2f}%, {}{:.2f}%). Given the minimum efect setting, \
            the region of practical equivalence (ROPE) is from {} to {}. {}" \
            .format(test_variants[best-1], hpd[0], hpd[1],
            '+' if hpd[0] > 0 else '', hpd_lower_percent, 
            '+' if hpd[1] > 0 else '', hpd_higher_percent, 
            -rope, rope, explanation_str)
else:
    desc_str = "The 95% high posterior density (HPD) of the distribution of differences between the control variant and variant {} is from {:.5f} to {:.5f} ({}{:.2f}%, {}{:.2f}%). Given the minimum efect setting, \
            the region of practical equivalence (ROPE) is from {} to {}. {}" \
            .format(test_variants[best-1], hpd[0], hpd[1],
            '+' if hpd[0] > 0 else '', hpd_lower_percent, 
            '+' if hpd[1] > 0 else '', hpd_higher_percent, 
            -rope, rope, explanation_str)

# for i in range(len(variants)-1):
#     hpd = pymc3.stats.hpd(simulations_diff[i])
#     lines_rope.append({
#         'type': 'line',
#         'yref': 'paper',
#         'x0': hpd[0],
#         'x1': hpd[1],
#         'y0': 0,
#         'y1': 0,
#         'line': {
#             'color': plotly_colours[i+1],
#             'width': 3
#         }
# })

dist_plots_diff.layout.update({'shapes': lines_loss})
dist_plots_rope.layout.update({'shapes': lines_rope})

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([

    html.H1('Bayesian AB Testing Dashboard',style={'font-family': 'verdana', 'margin-left': 15}),
    html.P(id='placeholder'),
    html.Div([
        html.Div([
            html.P('Find out if your test results are statistically significant. For each variation tested, input total sample size and the number of conversions.', style={'font-family': 'verdana'}),
            html.Div([
                html.B('Select the number of variants to test:',style={'font-family': 'verdana'}),
                dcc.Dropdown(
                id='variants-dropdown',
                options=[
                    {'label': '2', 'value': '2'},
                    {'label': '3', 'value': '3'},
                    {'label': '4', 'value': '4'}
                ],
                value='2',
                clearable=False,
                style={'font-family': 'verdana'}
                ),
                html.Br(),
                html.Div([
                    html.Div([
                        html.B('Samples',style={'font-family': 'verdana', 'margin-left': 77}),
                        html.B('Conversions',style={'font-family': 'verdana', 'margin-left': 79})
                    ], style={'margin-bottom': 10}),
                    html.Div([
                        html.B('Control',style={'font-family': 'verdana', 'margin-right': 13, 'color': plotly_colours[0]}),
                        dcc.Input(id='input_control_imps', type='number', value=8500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                        dcc.Input(id='input_control_conv', type='number', value=1410, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                    ], style={'margin-bottom': 10}),
                    html.Div([
                        html.B('A',style={'font-family': 'verdana', 'margin-right': 67, 'color': plotly_colours[1]}),
                        dcc.Input(id='input_A_imps', type='number', value=8500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                        dcc.Input(id='input_A_conv', type='number', value=1500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20 }),
                    ], style={'margin-bottom': 10}),
                    # html.Div([
                    #     html.B('B',style={'font-family': 'verdana', 'margin-right': 67, 'color': plotly_colours[2]}),
                    #     dcc.Input(id='input_B_imps', type='number', value=8500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                    #     dcc.Input(id='input_B_conv', type='number', value=1600, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                    # ], style={'margin-bottom': 10}),
                    # html.Div([
                    #     html.B('B',style={'font-family': 'verdana', 'margin-right': 67, 'color': plotly_colours[2]}),
                    #     dcc.Input(id='input_C_imps', type='number', value=8500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                    #     dcc.Input(id='input_C_conv', type='number', value=1600, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                    # ], style={'margin-bottom': 10})
                ],id='variants-container')
            ]),
            html.Div([
                html.Button('Calculate', id='calculate-button', style={'height': 45, 'width': 200,'font-family': 'verdana', 'font-size': 21})
            ]),
            html.Br(),
        ], style={'width': '50%', 'margin-left': 15}, className = 'six columns'),

        html.Div([
            html.P('Results:', style={'font-family': 'verdana'}),
            html.B(winning_str, style={'font-family': 'verdana', 'font-size': 18}, id='winner'),
            html.P('Based on 95% significance level', style={'font-family': 'verdana', 'font-size': 8, 'color': 'rgba(0,0,0,0.4)'}),
            html.P('Recommendation:', style={'font-family': 'verdana'}),
            html.B(rope_str,style={'font-family': 'verdana'}, id='recommendation'),
            html.P(desc_str,style={'font-family': 'verdana'}, id='desc')
        ], style={'width': '50%', 'margin-left': 15}, className = 'six columns')

    ], className = 'row'),

    html.Div([
        dcc.Graph(
            id='Probability to be best',
            figure={
                'data': [
                        go.Bar(
                            x = score,
                            y = ['Control', 'A', 'B'],
                            text = score,
                            textposition = 'auto',
                            orientation = 'h',
                            marker_color = plotly_colours[:3], 
                            hoverinfo = 'skip'
                        )
                ],
                'layout': {
                    'title': 'Probability to be Best',
                    'xaxis' : [0, 100],
                    'yaxis' : dict(autorange="reversed")
                }
            }
        ),
        dash_table.DataTable(
            id = 'table',
            data = df.to_dict('records'),
            columns = [{"name": i, "id": i} for i in df.columns],
            style_cell={'font_family': 'verdana', 'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_as_list_view=True
        ),
        dcc.Graph(
            id = 'Posteriors',
            figure = dist_plots
        ),
        dcc.Graph(
            id = 'Posteriors_diff',
            figure = dist_plots_diff
        ),
        dcc.Graph(
        id = 'Posteriors_rope',
        figure = dist_plots_rope
        )
    ])
])

@app.callback(Output('variants-container', 'children'),
              [Input('variants-dropdown', 'value')])
def generate_variant_divs(no_of_variants):
    print('Updating variant div')
    variants_total.updateVariants(no_of_variants)
    print(variants_total.no_of_variants)
    states_total.resetStates()
    variants_div = [   
        html.Div([
                html.Div([
                    html.B('Samples',style={'font-family': 'verdana', 'margin-left': 77}),
                    html.B('Conversions',style={'font-family': 'verdana', 'margin-left': 79})
                ], style={'margin-bottom': 10}),
                html.B('Control',style={'font-family': 'verdana', 'margin-right': 13, 'color': plotly_colours[0]}),
                dcc.Input(id='input_control_imps', type='number', value=8500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                dcc.Input(id='input_control_conv', type='number', value=1410, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
            ], style={'margin-bottom': 10}),
            html.Div([
                html.B('A',style={'font-family': 'verdana', 'margin-right': 67, 'color': plotly_colours[1]}),
                dcc.Input(id='input_A_imps', type='number', value=8500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                dcc.Input(id='input_A_conv', type='number', value=1500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
            ], style={'margin-bottom': 10})
        ]
    variant = 'B'
    for i in range(int(no_of_variants)-2):
        variant = chr(ord(variant) + i)
        variants_div.append(
            html.Div([
                html.B(variant,style={'font-family': 'verdana', 'margin-right': 67, 'color': plotly_colours[i+2]}),
                dcc.Input(id='input_' + variant + '_imps', type='number', value=8500, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
                dcc.Input(id='input_' + variant + '_conv', type='number', value=1600, style = {'height': 30, 'width': 130, 'font-size': 21, 'margin-right': 20}),
            ], style={'margin-bottom': 10})
        )
        imp = 'input_' + variant + '_imps'
        conv = 'input_' + variant + '_conv'
        states_total.updateStates(State(imp,'value'))
        states_total.updateStates(State(conv,'value'))
        print(states_total.all_states)
    return html.Div(variants_div)

@app.callback([Output('Probability to be best', 'figure'),
              Output('table', 'data'),
              Output('Posteriors', 'figure'),
              Output('Posteriors_diff', 'figure'),
              Output('Posteriors_rope', 'figure'),
              Output('winner', 'children'),
              Output('recommendation', 'children'),
              Output('desc', 'children')
              ], 
              [Input('calculate-button', 'n_clicks')],
              state=statesCount.all_states
              )
def update_graphs(n_clicks, *args):
    print(args)
    simulations = []
    samples = []
    conversions = []

    n = variants_total.no_of_variants
    print(n)
    for i in range(0,2*n,2):
        alpha, beta = 1 + args[i+1], 1 +  args[i] - args[i+1]
        simulation = np.random.beta(alpha,beta,10000)
        simulations.append(simulation)
        samples.append(args[i])
        conversions.append(args[i+1])

    # Computing the probability to be the best
    score = np.zeros(n)
    for i in range(10000):
        test = []
        for j in range(n): # Get the i-th entry for each of the simulations
            test.append(simulations[j][i])
        test = pd.Series(test)
        # Score the i-th round
        rankings = test.rank(ascending=False)
        k = 0
        for value in rankings:
            if value == 1.0:
                score[k] += 1
            k += 1

    score = np.round(score/sum(score) * 100,2)
    indices = np.argsort(score)[::-1]
    best = indices[0]

    loss = np.zeros(n)
    for i in range(n):
        if i != indices[0]: # If not the best variant
            loss_val = ((simulations[best] - simulations[i])/simulations[0])[simulations[best] > simulations[i]]
            loss[i] += np.mean(loss_val) * np.mean(simulations[best] > simulations[i])
        else: 
            for k in [j for j in range(len(loss)) if j != best]: # Sum losses for best variant
                loss_val = ((simulations[k] - simulations[best])/simulations[0])[simulations[k] > simulations[best]]
                if loss_val.size == 0:
                    loss[best] += 0
                else:
                    loss[best] += np.mean(loss_val) * np.mean(simulations[k] > simulations[best])
    
    winning_str = 'Variant ' + variants[best] + ' is the winner!'

    barplot={
        'data': [
            go.Bar(
                x = score,
                y = variants,
                orientation = 'h',
                text = score,
                textposition = 'auto', 
                marker_color = plotly_colours[:n],
                hoverinfo = 'skip',
                )
        ],
        'layout': {
            'title': 'Probability to be Best',
            'xaxis' : [0, 100],
            'yaxis' : dict(autorange="reversed")
        }
    }

    print(variants[:n])
    print(samples)
    print(conversions)
    print(score)
    print(loss)

    d = {
        'Variant': variants[:n],
        'Samples': samples,
        'Conversions': conversions,
        'Conversion Rate (%)': np.round(pd.Series(conversions)/pd.Series(samples), 5) * 100,
        'Probability to be Best (%)': np.round(score,2),
        'Expected Loss (%)': np.nan_to_num(np.round(loss * 100,2))
    }
    df = pd.DataFrame(d)

    dist_plots = ff.create_distplot(simulations, variants[:n], show_hist = False, show_rug = False)
    dist_plots.layout.update(legend = {'traceorder': 'normal'})
    dist_plots.layout.update(title='Posterior simulation of variants')
    dist_plots.layout.title.update(x=0.5)

    test_variants = variants[1:]
    simulations_diff = simulations[1:] - simulations[0]

    dist_plots_diff = ff.create_distplot(simulations_diff, test_variants[:n-1], show_hist = False, show_rug = False, colors=plotly_colours[1:])
    dist_plots_diff.layout.update(legend = {'traceorder': 'normal'})
    dist_plots_diff.layout.update(title='Posterior simulation of difference (Expected Loss)')
    dist_plots_diff.layout.title.update(x=0.5)

    dist_plots_rope = ff.create_distplot([simulations_diff[best-1]], [test_variants[best-1]], show_hist = False, show_rug = False, colors=plotly_colours[best:])
    dist_plots_rope.layout.update(legend = {'traceorder': 'normal'})
    dist_plots_rope.layout.update(title='Posterior simulation of difference (ROPE)')
    dist_plots_rope.layout.title.update(x=0.5)

    lines_loss = [
        {
            'type': 'line',
            'yref': 'paper',
            'x0': threshold,
            'x1': threshold,
            'y0': 0,
            'y1': 1,
            'line': {
                'color': 'rgb(0, 0, 0)',
                'width': 3,
                'dash': 'dash'
            }
        }
    ]   

    for i in range(1,n):
        lines_loss.append({
            'type': 'line',
            'yref': 'paper',
            'x0': loss[i],
            'x1': loss[i],
            'y0': 0,
            'y1': 1,
            'line': {
                'color': plotly_colours[i],
                'width': 3
            }
    })

    lines_rope = [
        {
            'type': 'line',
            'yref': 'paper',
            'x0': 0,
            'x1': 0,
            'y0': 0,
            'y1': 1,
            'line': {
                'color': 'rgb(0, 0, 0)',
                'width': 3
            }
        },
        {
            'type': 'line',
            'yref': 'paper',
            'x0': -rope,
            'x1': -rope,
            'y0': 0,
            'y1': 1,
            'line': {
                'color': 'rgb(0, 0, 0)',
                'width': 3,
                'dash': 'dash'
            }
        },
        {
            'type': 'line',
            'yref': 'paper',
            'x0': rope,
            'x1': rope,
            'y0': 0,
            'y1': 1,
            'line': {
                'color': 'rgb(0, 0, 0)',
                'width': 3,
                'dash': 'dash'
            }
        }
    ]   

    hpd = pymc3.stats.hpd(simulations_diff[best-1])
    lines_rope.append({
        'type': 'line',
        'yref': 'paper',
        'x0': hpd[0],
        'x1': hpd[1],
        'y0': 0,
        'y1': 0,
        'line': {
            'color': plotly_colours[best],
            'width': 3
        }
    })

    if (hpd[1] < -rope):
        winning_str = 'Variant ' +  variants[best] + ' is the winner!'
        explanation_str = 'Since the HPD lies outside the ROPE and is negative, the recommendation is to implement the control variant.'
        rope_str = "End the experiment. Implement the control variant."
    elif (hpd[0] > rope):
        winning_str = 'Variant ' +  variants[best] + ' is the winner!'
        explanation_str = 'Since the HPD lies outside the ROPE and is positive, the recommendation is to implement variant {}.'.format(variants[best])
        rope_str = "End the experiment. Implement variant {}.".format(variants[best])
    elif (hpd[0] > -rope) & (hpd[1] < rope):
        winning_str = 'Both variants are equivalent.'
        explanation_str = 'Since the HPD lies solely inside the ROPE, the recommendation is to implement either variant.'
        rope_str = "End the experiment. Implement either variant."
    else: 
        winning_str = 'No clear winner.'
        explanation_str = 'Since the HPD lies both inside and outside the ROPE, the recommendation is to keep testing as the results are inconclusive.'
        rope_str = "Continue the experiment as the results are inconclusive."
    
    hpd_lower_percent = hpd[0]/baseline * 100
    hpd_higher_percent = hpd[1]/baseline * 100
    if variants[best] != 'Control':
        desc_str = "The 95% high posterior density (HPD) of the distribution of differences between the control variant and variant {} is from {:.5f} to {:.5f} ({}{:.2f}%, {}{:.2f}%). Given the minimum efect setting, \
                the region of practical equivalence (ROPE) is from {} to {}. {}" \
                .format(test_variants[best-1], hpd[0], hpd[1],
                '+' if hpd[0] > 0 else '', hpd_lower_percent, 
                '+' if hpd[1] > 0 else '', hpd_higher_percent, 
                -rope, rope, explanation_str)
    else:
        desc_str = "The 95% high posterior density (HPD) of the distribution of differences between the control variant and variant {} is from {:.5f} to {:.5f} ({}{:.2f}%, {}{:.2f}%). Given the minimum efect setting, \
                the region of practical equivalence (ROPE) is from {} to {}. {}" \
                .format(test_variants[best-1], hpd[0], hpd[1],
                '+' if hpd[0] > 0 else '', hpd_lower_percent, 
                '+' if hpd[1] > 0 else '', hpd_higher_percent, 
                -rope, rope, explanation_str)

    # for i in range(len(variants)-1):
    #     hpd = pymc3.stats.hpd(simulations_diff[best-1])
    #     lines_rope.append({
    #         'type': 'line',
    #         'yref': 'paper',
    #         'x0': hpd[0],
    #         'x1': hpd[1],
    #         'y0': 0,
    #         'y1': 0,
    #         'line': {
    #             'color': plotly_colours[i+1],
    #             'width': 3
    #         }
    # })

    dist_plots_diff.layout.update({'shapes': lines_loss})
    dist_plots_rope.layout.update({'shapes': lines_rope})

    return barplot, df.to_dict('records'), dist_plots, dist_plots_diff, dist_plots_rope, winning_str, rope_str, desc_str

if __name__ == '__main__':
    app.run_server(debug=True)
