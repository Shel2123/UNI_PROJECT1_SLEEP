import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
path = 'Sleep_health_and_lifestyle_dataset.csv'
df = pd.read_csv(path)

def generate_gender_chart():
    value_counts_gender = df['Gender'].value_counts()
    fig_gender = go.Figure(data=[
    go.Pie(
        labels=value_counts_gender.index,
        values=value_counts_gender.values,
        hole=0.6,
        marker=dict(colors=['rgb(135, 206, 235)', 'rgb(238, 130, 238)']),
        textinfo='label+percent'
        )
    ])
    fig_gender.update_layout(
        title_text='Gender Stats',
        template='plotly_dark',
        showlegend=False
    )
    return fig_gender
    