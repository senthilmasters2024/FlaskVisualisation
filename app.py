import json
import pandas as pd
import plotly.express as px
from flask import Flask, render_template_string
import os

# Load the dataset
# Get the path of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the relative path to your file
file_path = os.path.join(current_directory, 'data', 'output_dataset.json')
with open(file_path, "r") as file:
    data = json.load(file)

# Convert data to DataFrame
df = pd.DataFrame(data)

# Ensure required columns exist
required_columns = {'FileName1', 'FileName2', 'domain', 'SimilarityScore'}
if not required_columns.issubset(df.columns):
    raise ValueError(f"Dataset must contain columns: {required_columns}")

# Map old domain names to new domain names
domain_name_mapping = {
    "jobvacancy": "Job Matching",
    "Medical-MedicationSuggestion": "Medical Suggestions",
    "Unknown": "Sports Insights"
}
df['Domain'] = df['domain'].map(domain_name_mapping)

# Assign numeric values to each domain to create spacing
unique_domains = df['Domain'].unique()
domain_positions = {domain: i * 2 + 1 for i, domain in enumerate(unique_domains)}
df['DomainPosition'] = df['Domain'].map(domain_positions)

# Define thresholds for each domain with unique colors
domain_thresholds = {
    "Job Matching": {"threshold": 0.5, "color": "red", "name": "Job Vacancy Threshold"},
    "Medical Suggestions": {"threshold": 0.5, "color": "green", "name": "Medical Threshold"},
    "Sports Insights": {"threshold": 0.7, "color": "blue", "name": "Sports Threshold"},
}

# Apply domain-specific thresholds to classify relevance
df['Relevance'] = df.apply(
    lambda row: 'Relevant' if row['SimilarityScore'] >= domain_thresholds[row['Domain']]["threshold"] else 'Irrelevant',
    axis=1
)

# Create a scatter plot with Plotly
fig = px.scatter(
    df,
    x='DomainPosition',
    y='SimilarityScore',
    color='Relevance',
    hover_data={'FileName1': True, 'FileName2': True, 'Domain': True, 'SimilarityScore': True},
    title='Phrase Similarity Classification by Domain',
    labels={'DomainPosition': 'Domain', 'SimilarityScore': 'Similarity Score'},
    size_max=10
)

# Add threshold lines for each domain with unique colors
for domain, config in domain_thresholds.items():
    domain_x = domain_positions[domain]
    fig.add_shape(
        type="line",
        x0=domain_x - 0.4,
        x1=domain_x + 0.4,
        y0=config["threshold"], y1=config["threshold"],
        line=dict(color=config["color"], dash="dash"),
        xref="x", yref="y",
    )

# Replace numeric x-axis values with domain names for readability
fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=list(domain_positions.values()),
        ticktext=list(domain_positions.keys())
    ),
    legend_title_text='Relevance and Thresholds',
    showlegend=True
)

# Restore hover tooltips with full Phrase1 and Phrase2
fig.update_traces(
    hovertemplate='<b>FileName1:</b> %{customdata[0]}<br>' +
                  '<b>FileName2:</b> %{customdata[1]}<br>' +
                  '<b>Domain:</b> %{customdata[2]}<br>' +
                  '<b>Similarity Score:</b> %{customdata[3]:.2f}<extra></extra>',
    customdata=df[['FileName1', 'FileName2', 'Domain', 'SimilarityScore']].values
)

# Convert the Plotly figure to an HTML string
plotly_html = fig.to_html(full_html=False)

# Create a Flask app
app = Flask(__name__)

# Route to display the Plotly graph
@app.route('/')
def index():
    return render_template_string('''
        <html>
            <head>
                <title>Phrase Similarity</title>
            </head>
            <body>
                {{ plotly_html|safe }}
            </body>
        </html>
    ''', plotly_html=plotly_html)

if __name__ == '__main__':
    app.run(debug=True)
