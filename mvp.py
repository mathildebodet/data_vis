import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_plotly_events import plotly_events
import altair as alt

df = pd.read_csv("food_preprocessed.csv")

st.title("What Shapes Student Eating Habits?")
col1, col2 = st.columns([0.3, 0.7])

st.set_page_config(
    page_title="Student Eating Habits",
    layout="wide"
)


with col1:
    st.write("Click on a constraint to explore how it shapes student eating habits.")

    col3, col4 = st.columns([3, 1])  # 3:1 pour que le pie soit plus large

    labels = ["Budget", "Time", "Workload"]
    values = [20, 35, 45]  # valeurs proportionnelles

    pie_df = pd.DataFrame({
        "constraint": labels,
        "value": values
    })
    pie_df["value"] = pie_df["value"].astype(float)

    with col3:
        
        # Pie chart
        fig = px.pie(
            pie_df,
            names="constraint",
            values="value",
        )

        fig.update_traces(
            textinfo="label",
            textposition="inside",
            marker=dict(colors=["#FF9999", "#66B2FF", "#99FF99"]),
            hoverinfo="skip",
            hovertemplate=None
        )

        fig.update_layout(
            showlegend=False,
            autosize=False,
            width=300,   # largeur forcée
            height=300   # hauteur forcée pour être carré
        )

        selected = plotly_events(fig, click_event=True)

    with col4:
        st.write("")  # espace pour aligner verticalement
        st.write("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        st.image("fourchette.png", width=100)  # ajuster width pour la faire à la même hauteur que le pie


with col2:
    if selected:
        index = selected[0]["pointNumber"]
        choice = labels[index]
        st.write("Explore how ", choice, " shapes student eating habits.")

    if selected:
        index = selected[0]["pointNumber"]
        choice = labels[index]

        if choice == "Budget":
            st.header("Budget and diet")
            grouped = (
                df.groupby(["Income Group", "Vegetable Eating Likelihood"])
                .size()
                .reset_index(name="count")
            )

            grouped["percentage"] = (
                grouped.groupby("Income Group")["count"]
                .transform(lambda x: x / x.sum() * 100)
            )

            # Graphique Altair
            chart_veg = alt.Chart(grouped).mark_bar(size=30).encode(
                x=alt.X(
                    "Income Group:N",
                    title="Income category",
                    axis=alt.Axis(labelAngle=0, labelFontSize=12)
                ),
                y=alt.Y(
                    "percentage:Q",
                    title="Percentage of students"
                ),
                xOffset="Vegetable Eating Likelihood:N",
                color=alt.Color(
                    "Vegetable Eating Likelihood:N",
                    title="Veggie Eating Likelihood",
                    sort=["unlikely", "neutral", "likely"],
                    scale=alt.Scale(range=["#FF9999", "#FFC966", "#66B2FF"])
                ),
                tooltip=[
                    alt.Tooltip("Income Group:N", title="Income Group"),
                    alt.Tooltip("Vegetable Eating Likelihood:N", title="Veggie Eating Likelihood"),
                    alt.Tooltip("percentage:Q", title="Percentage", format=".1f")
                ]
            ).properties(
                title="Income vs Vegetable Eating Likelihood"
            )

            st.altair_chart(chart_veg, use_container_width=True)
            st.write("One might expect income to strongly influence vegetable consumption. However, the distribution across income groups is relatively balanced. Even students with little or no income report similar or higher vegetable consumption, suggesting that income alone may not strongly determine this aspect of students’ diets.")


            health_dist = (
                df.groupby(["Employment Status", "Healthy Feeling Group"])
                .size()
                .reset_index(name="count")
            )

            health_dist["percentage"] = (
                health_dist.groupby("Employment Status")["count"]
                .transform(lambda x: x / x.sum() * 100)
            )

            # Graphique Altair
            chart_health = alt.Chart(health_dist).mark_bar(size=30).encode(
                x=alt.X(
                    "Employment Status:N",
                    title="Employment status",
                    axis=alt.Axis(labelAngle=0, labelFontSize=12)
                ),
                y=alt.Y(
                    "percentage:Q",
                    title="Percentage of students"
                ),
                xOffset="Healthy Feeling Group:N",
                color=alt.Color(
                    "Healthy Feeling Group:N",
                    title="Diet Health Perception",
                    sort=["Unhealthy", "Moderately healthy", "Healthy"],
                    scale=alt.Scale(range=["#FF6666", "#FFCC66", "#66B2FF"])
                ),
                tooltip=[
                    alt.Tooltip("Employment Status:N", title="Employment Status"),
                    alt.Tooltip("Healthy Feeling Group:N", title="Diet Health Perception"),
                    alt.Tooltip("percentage:Q", title="Percentage", format=".1f")
                ]
            ).properties(
                title="Perceived Diet Healthiness by Employment Status"
            )

            st.altair_chart(chart_health, use_container_width=True)
            st.write("This chart explores whether students with different financial situations perceive their diet differently. Employment status can partially reflect access to financial resources, as students with part-time jobs may have more money to spend on food. However, the results show relatively similar perceptions of diet healthiness across groups, suggesting that financial differences alone may not strongly influence how healthy students feel their diet is.")
            

        elif choice == "Time":
            st.header("Time constraints")

            fig, ax = plt.subplots()
            df["cook"].value_counts().plot(kind="bar", ax=ax)
            st.pyplot(fig)

        elif choice == "Workload":
            st.header("Academic stress")

            fig, ax = plt.subplots()
            df["comfort_food_reasons"].value_counts().plot(kind="bar", ax=ax)
            st.pyplot(fig)