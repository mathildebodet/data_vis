import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_plotly_events import plotly_events
import altair as alt

df = pd.read_csv("food_preprocessed.csv")

st.title("What Shapes Student Eating Habits?")
col1, col2 = st.columns([0.3, 0.7], gap="medium")

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
            width=330,   # largeur forcée
            height=330   # hauteur forcée pour être carré
        )

        selected = plotly_events(fig, click_event=True)

    with col4:
        st.write("")  # espace pour aligner verticalement
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
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
            st.write("This chart explores whether students with different financial situations perceive their diet differently. Employment status can partially reflect access to financial resources, as students with part-time jobs may have more money to spend on food. However, the results show that unemployed students report similar or even higher perceptions of healthy eating compared to those with part-time jobs. This suggests that financial constraints may not be the primary factor influencing how students eat.")
            

        elif choice == "Time":
            st.header("Time constraints")
            cook_dist = df["Cook Frequency"].value_counts(normalize=True).reset_index()
            cook_dist.columns = ["Cook Frequency", "Proportion"]
            cook_dist["Proportion"] *= 100

            chart_cook = alt.Chart(cook_dist).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("Proportion:Q", title=""),
                color=alt.Color("Cook Frequency:N", scale=alt.Scale(scheme="pastel1")),
                tooltip=["Cook Frequency:N", alt.Tooltip("Proportion:Q", format=".1f")]
            ).properties(
                title="Cooking Frequency among Students"
            )
            st.altair_chart(chart_cook, use_container_width=True)
            st.write("Many students report that they would like to cook more often, but in reality, they mostly cook only whenever they can, indicating that time constraints strongly limit their ability to prepare meals at home.")

            eat_out_dist = (
            df.groupby(["Living Situation", "Eating Out Frequency"])
                .size()
                .reset_index(name="count")
            )
            eat_out_dist["percentage"] = (
                eat_out_dist.groupby("Living Situation")["count"]
                .transform(lambda x: x / x.sum() * 100)
            )

            # --- Grouped bar chart ---
            chart_eat_out = alt.Chart(eat_out_dist).mark_bar().encode(
                x=alt.X("Living Situation:N", title="Living Situation", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("percentage:Q", title="Percentage of students"),
                color=alt.Color("Eating Out Frequency:N", legend=alt.Legend(title="Eating Out Frequency"),scale=alt.Scale(scheme="pastel1")),
                column=alt.Column("Eating Out Frequency:N", title=None, spacing=10),  # optionnel, pour séparer par catégorie
                tooltip=[
                    alt.Tooltip("Living Situation:N"),
                    alt.Tooltip("Eating Out Frequency:N"),
                    alt.Tooltip("percentage:Q", format=".1f")
                ]
            ).properties(
                title="Eating Out Frequency by Living Situation",
                width=400,
                height=400
            )
            st.altair_chart(chart_eat_out)
            st.write("Students who live off campus or have long commutes tend to eat out more frequently, while those on campus eat out less. This shows that time availability and commuting heavily influence eating-out habits.")
        elif choice == "Workload":
            st.header("Academic stress")

            reason_map = {1: "Stress", 2: "Boredom", 3: "Depression/Sadness", 4: "Hunger", 5: "Laziness", 6: "Other", 7: "Other", 8: "Other", 9: "Never eat comfort food"}
            grade_map = {1: "Freshman", 2: "Sophomore", 3: "Junior", 4: "Senior"}

            df["Reason"] = df["comfort_food_reasons_coded"].map(reason_map)
            df["Grade Level"] = df["grade_level"].map(grade_map)

            # Filtrer uniquement les raisons pertinentes
            df_filtered = df.dropna(subset=["Reason"])

            # Calculer les proportions par grade
            stacked_df = (
                df_filtered.groupby(["Grade Level", "Reason"])
                .size()
                .reset_index(name="count")
            )

            stacked_df["percentage"] = stacked_df.groupby("Grade Level")["count"].transform(lambda x: x / x.sum() * 100)
            reason_order = ["Stress", "Boredom", "Depression/Sadness", "Hunger", "Laziness", "Other", "Never eat comfort food"]
            # Stacked bar chart
            chart_stack = alt.Chart(stacked_df).mark_bar().encode(
                x=alt.X("Grade Level:N", title="Grade Level"),
                y=alt.Y("percentage:Q", title="Percentage of students"),
                color=alt.Color("Reason:N",sort=reason_order, legend=alt.Legend(title="Reason for Comfort Food"), scale=alt.Scale(scheme="pastel1")),
                tooltip=[
                    alt.Tooltip("Grade Level:N"),
                    alt.Tooltip("Reason:N"),
                    alt.Tooltip("percentage:Q", format=".1f", title="Percentage")
                ]
            ).properties(
                title="Comfort Food Reasons by Grade Level",
                width=600,
                height=400
            )
            st.altair_chart(chart_stack, use_container_width=True)
            st.write("The chart shows that Stress, Boredom, and Depression/Sadness are the predominant reasons why students turn to comfort food. This highlights that emotional responses related to academic workload strongly influence eating habits, and these patterns are consistent across all grade levels.")