import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_plotly_events import plotly_events

df = pd.read_csv("food_coded.csv")

labels = ["Budget", "Time", "Workload"]
values = [40, 35, 25]
col1, col2 = st.columns([1,2])

st.title("What Shapes Student Eating Habits?")

with col1:
    st.write("Click on a constraint to explore how it shapes student eating habits.")

    pie_df = pd.DataFrame({
    "constraint": labels,
    "value": values
    })

    fig = px.pie(
    pie_df,
    names="constraint",
    values="value"
    )

    fig.update_traces(textinfo="label", textposition="inside", marker=dict(colors=["#FF9999", "#66B2FF", "#99FF99"]), hoverinfo = "skip", hovertemplate = None)
    fig.update_layout(showlegend=False, width=400, height=400)

    selected = plotly_events(fig, click_event=True)


with col2:
    if selected:
        index = selected[0]["pointNumber"]
        choice = labels[index]
        st.write("You selected:", choice)

    if selected:
        index = selected[0]["pointNumber"]
        choice = labels[index]

        if choice == "Budget":
            st.header("Budget and diet")

            fig, ax = plt.subplots()
            df.groupby("income")[["fruit_day","veggies_day"]].mean().plot(kind="bar", ax=ax)
            st.pyplot(fig)

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