import plotly.express as px
import plotly.graph_objects as go
from typing import List, Tuple, Dict


class GenerateGraph:
    def __init__(self, data): 
        self.df = data

    def generate_gender_chart(self):
        value_counts_gender = self.df['Gender'].value_counts()
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


    def generate_occupation_chart(self):
        # group occupation data
        value_counts_occupation = self.df['Occupation'].value_counts()

        # set occupation statistics
        fig_occupation = go.Figure(data=[
            go.Pie(
                labels=value_counts_occupation.index,
                values=value_counts_occupation.values,
                hole=0.3,
                textinfo='label+percent'
            )
        ])

        # decorate
        fig_occupation.update_layout(
            title_text='Occupation Stats',
            template='plotly_dark',
            showlegend=False
        )

        # show
        return fig_occupation


    def generate_stress_occupation_chart(self):
        # group data
        average_stress_table = self.df.groupby('Occupation').agg(
            average_stress_level=('Stress Level', 'mean'),
            count=('Stress Level', 'size')
        ).reset_index()

        # sort
        average_stress_table = average_stress_table.sort_values(by='average_stress_level',
                                                                ascending=False
        )

        # draw the graph
        fig_chart_occupation_stress = px.bar(
                average_stress_table,
                x='Occupation',
                y='average_stress_level',
                title='Occupation increases Stress Level',
                labels={'average_stress_level': 'Average Stress Level', 'Occupation': 'Occupation'},
                text='count',
                hover_data={'count': True}
        )

        # decorate
        fig_chart_occupation_stress.update_layout(xaxis_title="Occupation",
                                                yaxis_title="Average Stress Level",
                                                xaxis_tickangle=-45,
                                                template='plotly_dark'
        )

        # show the graph
        return fig_chart_occupation_stress


    def generate_spray_graph(self):
        fig_spray = go.Figure()
        # add sleep duration data
        fig_spray.add_trace(go.Histogram2d(
            x = self.df['Age'],
            y = self.df['Sleep Duration'],
            colorscale=[
                [0, 'rgba(0, 0, 0, 0)'],
                [0.5, 'rgba(0, 130, 180, 0.5)'],
                [1, 'rgb(0, 130, 180)']
            ],
            nbinsx=60,
            nbinsy=30,
            opacity=0.75,
            colorbar=dict(title='Sleep Freq', x=1.0),
            showscale=True
        ))

        # add stress level data
        fig_spray.add_trace(go.Histogram2d(
            x = self.df['Age'],
            y = self.df['Stress Level'],
            colorscale=[
                [0, 'rgba(0, 0, 0, 0)'],
                [0.5, 'rgba(205, 92, 92, 0.5)'],
                [1, 'rgb(205, 92, 92)']
            ],
            nbinsx=60,
            nbinsy=30,
            opacity=0.75,
            colorbar=dict(title='Stress Freq', x=1.2),
            showscale=True
        ))

        # decorate
        fig_spray.update_layout(
            title='Sleep Duration vs Stress Level',
            xaxis_title='Age',
            yaxis_title='Value',
            barmode='overlay',
            template='plotly_dark'
        )

        # show
        return fig_spray


    def generate_average_chart(self):
        # find every useful points
        def fnd(values: List[float]) -> Tuple[List[int], List[int]]:
            peaks = []
            downs = []
            mx = max(values)
            mn = min(values)
            for i in range(1, len(values) - 1):
                if values[i] > values[i - 1] and values[i] > values[i + 1] and values[i] != mx:
                    peaks.append(i)
                elif values[i] < values[i - 1] and values[i] < values[i + 1] and values[i] != mn:
                    downs.append(i)
            return downs, peaks

        fig_graph = go.Figure()
        
        # group data into two columns by average values: average sleep and average stress
        grouped_df = self.df.groupby('Age').agg(
            average_sleep=('Sleep Duration', 'mean'),
            average_stress=('Stress Level', 'mean')
        ).reset_index()

        # find peaks and downs
        sleep_min = grouped_df.loc[grouped_df["average_sleep"].idxmin()]
        sleep_max = grouped_df.loc[grouped_df["average_sleep"].idxmax()]

        stress_min = grouped_df.loc[grouped_df["average_stress"].idxmin()]
        stress_max = grouped_df.loc[grouped_df["average_stress"].idxmax()]

        # finding them
        sleep_mins, sleep_maxes = fnd(grouped_df['average_sleep'].values)
        stress_mins, stress_maxes = fnd(grouped_df['average_stress'].values)

        # define common line styles
        line_styles: Dict[str, Dict[str, str]] = {
            "average_sleep": dict(color='rgb(0, 130, 180)'),
            "average_stress": dict(color='rgb(205, 92, 92)'),
        }

        marker_styles: Dict[str, Dict[str, str]] = {
            "sleep_down": dict(color='blue', size=10, symbol="triangle-down"),
            "sleep_up": dict(color='blue', size=10, symbol="triangle-up"),
            "stress_down": dict(color='red', size=10, symbol="triangle-down"),
            "stress_up": dict(color='red', size=10, symbol="triangle-up"),
            "peak_marker": dict(size=10, symbol="arrow-bar-up"),
        }

        # add average lines
        for metric, style in line_styles.items():
            fig_graph.add_trace(go.Scatter(
                x=grouped_df['Age'],
                y=grouped_df[metric],
                mode='lines',
                name=f'Average {metric.split("_")[1]}',
                line=style
            ))

        # add markers for sleep and stress changes
        changes = [
            ("Age", "average_sleep", sleep_maxes, "sleep_down"),
            ("Age", "average_sleep", sleep_mins, "sleep_up"),
            ("Age", "average_stress", stress_maxes, "stress_down"),
            ("Age", "average_stress", stress_mins, "stress_up"),
        ]

        for age_col, metric_col, indices, marker_key in changes:
            fig_graph.add_trace(go.Scatter(
                x=grouped_df[age_col].iloc[indices],
                y=grouped_df[metric_col].iloc[indices],
                mode='markers',
                name=marker_key.replace('_', ' ').title(),
                marker=marker_styles[marker_key]
            ))

        # add peaks and downs
        peak_data = [
            ("Age", "average_sleep", sleep_min, sleep_max, 'blue', 'Sleep peak'),
            ("Age", "average_stress", stress_min, stress_max, 'red', 'Stress peak'),
        ]

        for age_col, metric_col, min_data, max_data, color, name in peak_data:
            fig_graph.add_trace(go.Scatter(
                x=[min_data[age_col], max_data[age_col]],
                y=[min_data[metric_col], max_data[metric_col]],
                mode='markers+text',
                name=name,
                text=["min", "max"],
                textposition="top center",
                marker=dict(color=color, **marker_styles["peak_marker"])
            ))

        # decorate
        fig_graph.update_layout(
            title='Average Sleep Duration vs Average Stress Level',
            xaxis_title='Age',
            yaxis_title='Average Values',
            legend_title='Value',
            template='plotly_dark'
        )

        # show
        return fig_graph


    def generate_phys_sleep_chart(self):
        fig_phyz = go.Figure()
        # group data by average values
        grouped_df = self.df.groupby('Age').agg(
            average_physical=('Physical Activity Level', 'mean'),
            average_quality=('Quality of Sleep', 'mean'),
            average_stress=('Stress Level', 'mean')
        ).reset_index()

        # add average sleep quality line
        fig_phyz.add_trace(go.Scatter(
            x=grouped_df['Age'],
            y=grouped_df['average_quality'],
            mode='lines',
            name='Average Quality of Sleep',
            line=dict(color='rgb(0, 130, 180)')
        ))

        # add average stress level line
        fig_phyz.add_trace(go.Scatter(
            x=grouped_df['Age'],
            y=grouped_df['average_stress'],
            mode='lines',
            name='Average Stress Level',
            line=dict(color='rgb(205, 92, 92)')
        ))

        # add physical activity line
        fig_phyz.add_trace(go.Scatter(
            x=grouped_df['Age'],
            y=grouped_df['average_physical'] / 10,
            mode='lines',
            name='Average Physical Activity Level',
            line=dict(color='orange')
        ))

        # decorate
        fig_phyz.update_layout(
            title='Average Sleep Quality vs Average Stress Level vs Average Physical Activity',
            xaxis_title='Age',
            yaxis_title='Average values',
            legend_title='Value',
            template='plotly_dark'
        )

        # show
        return fig_phyz


    def generate_duration_vs_quality_vs_phys_chart(self):
        fig_duration_vs_quality_vs_phyz = go.Figure()
        # group data by average values
        grouped_df = self.df.groupby('Age').agg(
            average_physical=('Physical Activity Level', 'mean'),
            average_quality=('Quality of Sleep', 'mean'),
            average_duration=('Sleep Duration', 'mean')
        ).reset_index()

        # add average sleep quality line
        fig_duration_vs_quality_vs_phyz.add_trace(go.Scatter(
            x=grouped_df['Age'],
            y=grouped_df['average_quality'],
            mode='lines',
            name='Average Quality of Sleep',
            line=dict(color='rgb(0, 130, 180)')
        ))

        # add average sleep duration line
        fig_duration_vs_quality_vs_phyz.add_trace(go.Scatter(
            x=grouped_df['Age'],
            y=grouped_df['average_duration'],
            mode='lines',
            name='Average Sleep Duration',
            line=dict(color='rgb(205, 92, 92)')
        ))

        # add average physical activity line
        fig_duration_vs_quality_vs_phyz.add_trace(go.Scatter(
            x=grouped_df['Age'],
            y=grouped_df['average_physical'] / 10,
            mode='lines',
            name='Average Physical Activity Level',
            line=dict(color='orange')
        ))

        # decorate
        fig_duration_vs_quality_vs_phyz.update_layout(
            title='Average Quality of Sleep vs Average Sleep Duration vs Average Physical Activity',
            xaxis_title='Age',
            yaxis_title='Average values',
            legend_title='Value',
            template='plotly_dark'
        )

        # show
        return fig_duration_vs_quality_vs_phyz


    def generate_pearsons_mtx(self):
        columns = ['Sleep Duration', 'Quality of Sleep', 'Physical Activity Level', 'Stress Level']
        grouped_df = self.df[columns]

        correl_mtx = grouped_df.corr(method='pearson')
        fig_temp = px.imshow(
            correl_mtx,
            text_auto=True,
            color_continuous_scale='RdBu',
            range_color=[-1, 1],
            labels=dict(color="Pearson's Corellation"),
            x=correl_mtx.columns,
            y=correl_mtx.index,
            title="Pearson's Correlations"
        )

        fig_temp.update_layout(
            xaxis_title="Values",
            yaxis_title="Values",
            template='plotly_dark'
        )

        return fig_temp
