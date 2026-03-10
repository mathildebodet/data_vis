import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("food_coded.csv")

# st.title("What Shapes Student Eating Habits?")

# constraint = st.selectbox(
#     "Choose a constraint to explore:",
#     ["Budget", "Time constraints", "Academic stress"]
# )

# # BUDGET
# if constraint == "Budget":

#     st.header("Income and diet quality")

#     fig, ax = plt.subplots()
#     df.groupby("income")[["fruit_day","veggies_day"]].mean().plot(kind="bar", ax=ax)
#     ax.set_ylabel("Average portions per day")
#     st.pyplot(fig)

#     st.header("Income and eating out")

#     fig, ax = plt.subplots()
#     sns.countplot(data=df, x="income", hue="eating_out", ax=ax)
#     ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
#     st.pyplot(fig)


# # TIME
# elif constraint == "Time constraints":

#     st.header("Cooking frequency")

#     fig, ax = plt.subplots()
#     df["cook"].value_counts().plot(kind="bar", ax=ax)
#     ax.set_ylabel("Number of students")
#     st.pyplot(fig)

#     st.header("Cooking vs eating out")

#     fig, ax = plt.subplots()
#     sns.countplot(data=df, x="cook", hue="eating_out", ax=ax)
#     ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
#     st.pyplot(fig)


# # STRESS
# elif constraint == "Academic stress":

#     st.header("Reasons for comfort food")

#     fig, ax = plt.subplots()
#     df["comfort_food_reasons"].value_counts().plot(kind="bar", ax=ax)
#     ax.set_ylabel("Number of students")
#     st.pyplot(fig)

#     st.header("Eating changes since college")

#     fig, ax = plt.subplots()
#     df["eating_changes"].value_counts().plot(kind="bar", ax=ax)
#     ax.set_ylabel("Number of students")
#     st.pyplot(fig)

import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events

labels = ["Budget", "Time", "Workload"]
values = [1,1,1]

fig = px.pie(
    names=labels,
    values=values,
    title="What shapes student eating habits?"
)

selected = plotly_events(fig, click_event=True)

st.plotly_chart(fig)

if selected:
    choice = selected[0]["label"]
    st.write("You selected:", choice)

if selected:
    choice = selected[0]["label"]

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