import pandas as pd
import plotly.express as px

# Data from your example
phrases = [
    ("ChristianoRonaldo.txt", "Aspirin.txt", "Unknown", 0.07459803312148565),
    ("ChristianoRonaldo.txt", "iboprofen.txt", "Unknown", 0.09903397662116371),
    ("ChristianoRonaldo.txt", "JobRequirement.txt", "Unknown", 0.12538476261131676),
    ("ChristianoRonaldo.txt", "paracetomol.txt", "Unknown", 0.05216173653132632),
    ("ChristianoRonaldo.txt", "SachinTendulkarNewsArticle.txt", "Unknown", 0.393528248018886),
    ("JobProfileCDeveloper.txt", "Aspirin.txt", "jobvacancy", -0.016096263623203412),
    ("JobProfileCDeveloper.txt", "iboprofen.txt", "jobvacancy", 0.006234526462268183),
    ("JobProfileCDeveloper.txt", "JobRequirement.txt", "jobvacancy", 0.6863929709725499),
    ("JobProfileCDeveloper.txt", "paracetomol.txt", "jobvacancy", 0.0034207695091580774),
    ("JobProfileCDeveloper.txt", "SachinTendulkarNewsArticle.txt", "jobvacancy", 0.13486307131328207),
    ("MedicalHistory.txt", "Aspirin.txt", "Medical-MedicationSuggestion", 0.33195745429772733),
    ("MedicalHistory.txt", "iboprofen.txt", "Medical-MedicationSuggestion", 0.23717794093567096),
    ("MedicalHistory.txt", "JobRequirement.txt", "Medical-MedicationSuggestion", 0.15897824254820653),
    ("MedicalHistory.txt", "paracetomol.txt", "Medical-MedicationSuggestion", 0.23864067770371952),
    ("MedicalHistory.txt", "SachinTendulkarNewsArticle.txt", "Medical-MedicationSuggestion", 0.16838020131545448),
    ("MSDhoni.txt", "Aspirin.txt", "Unknown", 0.026687593772055433),
    ("MSDhoni.txt", "iboprofen.txt", "Unknown", 0.010836918179269881),
    ("MSDhoni.txt", "JobRequirement.txt", "Unknown", 0.11549445010066965),
    ("MSDhoni.txt", "paracetomol.txt", "Unknown", 0.02196351114889793),
    ("MSDhoni.txt", "SachinTendulkarNewsArticle.txt", "Unknown", 0.5415616921075621),
    ("SachinTendulkar.txt", "Aspirin.txt", "Unknown", 0.07521079460166216),
    ("SachinTendulkar.txt", "iboprofen.txt", "Unknown", 0.05243897282142897),
    ("SachinTendulkar.txt", "JobRequirement.txt", "Unknown", 0.10582298657778909),
    ("SachinTendulkar.txt", "paracetomol.txt", "Unknown", 0.08709043452917352),
    ("SachinTendulkar.txt", "SachinTendulkarNewsArticle.txt", "Unknown", 0.7395233999998398),
]

# Convert to DataFrame
df = pd.DataFrame(phrases, columns=['SourceDocument', 'DocSentByUserForComparison', 'Domain', 'SimilarityScore'])

# Map old domain names to new domain names
domain_name_mapping = {
    "jobvacancy": "Job Matching",
    "Medical-MedicationSuggestion": "Medical Suggestions",
    "Unknown": "Sports Insights"
}
df['Domain'] = df['Domain'].map(domain_name_mapping)

# Assign numeric values to each domain to create spacing
unique_domains = df['Domain'].unique()
domain_positions = {domain: i * 2 + 1 for i, domain in enumerate(unique_domains)}
df['DomainPosition'] = df['Domain'].map(domain_positions)

# Define thresholds for each domain with unique colors
domain_thresholds = {
    "Job Matching": {"threshold": 0.5, "color": "red", "name": "Job Vacancy Threshold"},
    "Medical Suggestions": {"threshold": 0.2, "color": "green", "name": "Medical Threshold"},
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
    x='DomainPosition',  # Use numeric positions instead of categories
    y='SimilarityScore',
    color='Relevance',
    hover_data={'SourceDocument': True, 'DocSentByUserForComparison': True, 'Domain': True, 'SimilarityScore': True},  # Detailed hover info
    title='Phrase Similarity Classification by Domain',
    labels={'DomainPosition': 'Domain', 'SimilarityScore': 'Similarity Score'},
    size_max=10  # Adjust marker size
)

# Set text position for better readability
fig.update_traces(marker=dict(size=12))

# Add threshold lines for each domain with unique colors
for domain, config in domain_thresholds.items():
    domain_x = domain_positions[domain]
    fig.add_shape(
        type="line",
        x0=domain_x - 0.4,  # Add padding
        x1=domain_x + 0.4,
        y0=config["threshold"], y1=config["threshold"],
        line=dict(color=config["color"], dash="dash"),
        xref="x", yref="y",
        name=config["name"]
    )

# Replace numeric x-axis values with domain names for readability
fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=list(domain_positions.values()),
        ticktext=list(domain_positions.keys())  # Display domain names
    ),
    legend_title_text='Relevance and Thresholds',
    showlegend=True
)

# Show the plot
fig.show()
