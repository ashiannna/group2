import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load and clean the data
df_clean = pd.read_csv('ds_salaries_final.csv')

# Get the top 10 most frequent job titles for the dropdown
top_10_job_titles = df_clean['job_title'].value_counts().nlargest(10).index.tolist()
top_10_job_titles.append("Analyze All")

# Initialize the Dash app
app = dash.Dash(__name__, serve_locally=True, external_stylesheets=["/assets/styles.css"])

# Define the layout of the app
app.layout = html.Div(style={'backgroundColor': '#000814', 'margin': '0', 'padding': '200px', 'padding-top': '40px'},
                      children=[
                          html.H1("Data Science Salaries Dashboard", style={'textAlign': 'center', 'color': 'white'}),
                             html.A('Cookbook', href='https://alizas-organization.gitbook.io/group2/', className='dash-link', target='_blank'),


                          html.Div([
                              dcc.Dropdown(
                                  id='job-title-dropdown',
                                  options=[{'label': i, 'value': i} for i in top_10_job_titles],
                                  value='Analyze All'
                              )
                          ], style={'width': '50%', 'margin': 'auto'}),
                          
                          html.Div(id='summary-stats', style={
                              'display': 'flex',
                              'padding': '10px',
                              'margin': '20px 0',
                              'background-color': '#000814',
                          }),
                          
                          html.Div([
                              dcc.Graph(id='figure1', style={'width': '48%', 'margin-bottom': '40px'}),
                              dcc.Graph(id='figure2', style={'width': '48%', 'margin-bottom': '40px'}),
                          ], style={
                              'display': 'flex',
                              'flexDirection': 'row',
                              'justifyContent': 'space-between'
                              # 'overflowX': 'auto',  # Allow horizontal scrolling if needed
                          }),
                          
                          dcc.Graph(id='figure3', config={'displayModeBar': False}),
                          
                          html.Div([
                              dcc.Graph(id='figure4', style={'width': '48%', 'margin-top': '40px'}),
                              dcc.Graph(id='figure5', style={'width': '48%', 'margin-top': '40px'}),
                          ], style={
                              'display': 'flex',
                              'flexDirection': 'row',
                              'justifyContent': 'space-between'
                              # 'overflowX': 'auto',  # Allow horizontal scrolling if needed
                          }),
                      ])

# Define a function to apply dark mode styling to a figure
def apply_dark_mode_style(figure):
    figure.update_layout(
        plot_bgcolor='#383434',
        paper_bgcolor='#383434',
        font_color='lightblue',
        title_font_color='lightblue'
    )
    
    return figure

# Define callback to update graphs and summary statistics
@app.callback(
    [
        Output('summary-stats', 'children'),
        Output('figure1', 'figure'),
        Output('figure2', 'figure'),
        Output('figure3', 'figure'),
        Output('figure4', 'figure'),
        Output('figure5', 'figure'),     
    ],
    [Input('job-title-dropdown', 'value')]
)

def update_dashboard(selected_job_title):
    if selected_job_title != "Analyze All":
        filtered_data = df_clean[df_clean['job_title'] == selected_job_title]
    else:
        filtered_data = df_clean
        
    # Calculate average salary over the years (2020-2023)
    avg_salary_over_years = filtered_data.groupby('year')['salary_in_usd'].mean().reset_index()

    # Create the average salary line chart
    figure1 = apply_dark_mode_style(px.line(avg_salary_over_years, x='year', y='salary_in_usd',
                                    title='Average Salary by Work Year'))

    # Calculate average salary by job title
    avg_salary_by_job_title = filtered_data[filtered_data['job_title'].isin(top_10_job_titles[:-1])] \
    .groupby('job_title')['salary_in_usd'].mean().reset_index()

    # Create the average salary by job title bar chart
    if selected_job_title != "Analyze All":
        figure2 = apply_dark_mode_style(px.histogram(filtered_data, x='salary_in_usd', nbins=20,
                                title='Salary Distribution'))
    else:
        figure2 = apply_dark_mode_style(px.bar(avg_salary_by_job_title, x='job_title', y='salary_in_usd',
                                                title='Average Salary by Job Title'))

    # Calculate average salary by experience level and year
    avg_salary_by_experience_level_year = filtered_data.groupby(['year', 'experience_level'])['salary_in_usd'].mean().reset_index()

    # Create the clustered bar chart for average salary by experience level and year
    figure3 = apply_dark_mode_style(px.bar(avg_salary_by_experience_level_year, x='year', y='salary_in_usd', 
                    color='experience_level', 
                    title='Average Salary by Experience Level and Year',
                    labels={'year': 'Year', 'salary_in_usd': 'Average Salary'},
                    barmode='group'))

    # Calculate work year distribution
    work_year_distribution = filtered_data['year'].value_counts().reset_index()
    work_year_distribution.columns = ['year', 'count']

    # Create the work year distribution pie chart
    figure4 = apply_dark_mode_style(px.pie(work_year_distribution, names='year', values='count',
                                title='Work Year Distribution'))

    # Calculate the remote ratio distribution
    remote_ratio_distribution = filtered_data['remote_ratio'].value_counts().reset_index()
    remote_ratio_distribution.columns = ['Remote Ratio', 'Count']
    
    # Create a donut chart
    figure5 = apply_dark_mode_style(px.pie(remote_ratio_distribution, names='Remote Ratio', values='Count', hole=0.4,
                     title='Remote Ratio Distribution'))
    figure5.update_traces(textinfo='percent+label')
    
    # Calculate and display summary statistics
    avg_salary = filtered_data['salary_in_usd'].mean()
    max_salary = filtered_data['salary_in_usd'].max()
    min_salary = filtered_data['salary_in_usd'].min()
    summary_stats = [
        html.Div(f"Average Salary: ${avg_salary:.2f}", style={'background-color': '#fbb1bd', 'margin': '10px', 'border-radius': '10px', 'padding': '50px', 'font-size': '20px', 'flex-grow': '1', 'text-align': 'center'}),
        html.Div(f"Maximum Salary: ${max_salary:.2f}", style={'background-color': '#fbb1bd', 'margin': '10px', 'border-radius': '10px', 'padding': '50px', 'font-size': '20px', 'flex-grow': '1', 'text-align': 'center'}),
        html.Div(f"Minimum Salary: ${min_salary:.2f}", style={'background-color': '#fbb1bd', 'margin': '10px', 'border-radius': '10px', 'padding': '50px', 'font-size': '20px', 'flex-grow': '1', 'text-align': 'center'})
    ]

    return summary_stats, figure1, figure2, figure3, figure4, figure5

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
