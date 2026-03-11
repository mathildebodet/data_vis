import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_plotly_events import plotly_events
import altair as alt

df = pd.read_csv("food_coded_2.csv")

st.title("What Shapes Student Eating Habits?")
col1, col2 = st.columns([0.5, 0.5])

st.set_page_config(
    page_title="Student Eating Habits",
    layout="wide"
)


with col1:
    st.write("Click on a constraint to explore how it shapes student eating habits.")
    labels = ["Budget", "Time", "Workload"]
    values = [20, 35, 45]  # valeurs proportionnelles

    # dataframe propre, forcer float
    pie_df = pd.DataFrame({
        "constraint": labels,
        "value": values
    })
    pie_df["value"] = pie_df["value"].astype(float)

    # pie chart
    fig = px.pie(
        pie_df,
        names="constraint",
        values="value"
    )


    fig.update_traces(textinfo="label", textposition="inside", marker=dict(colors=["#FF9999", "#66B2FF", "#99FF99"]), hoverinfo = "skip", hovertemplate = None)
    fig.update_layout(showlegend=False, autosize=True)

    selected = plotly_events(fig, click_event=True)


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
            st.write("One might expect income to strongly influence vegetable consumption. However, the distribution across income groups is relatively balanced. Even students with little or no income report similar or higher vegetable consumption, suggesting that income alone may not strongly determine this aspect of students’ diets.")

            mapping_income = {
            1: "less than $15,000",
            2: "$15,001 to $30,000",
            3: "$30,001 to $50,000",
            4: "$50,001 to $70,000",
            5: "$70,001 to $100,000",
            6: "higher than $100,000"
        }

            mapping_veg = {
                1: "very unlikely",
                2: "unlikely",
                3: "neutral",
                4: "likely",
                5: "very likely"
            }

            data_short = df[["income", "veggies_day"]].copy()

            data_short["income"] = data_short["income"].map(mapping_income)
            data_short["veggies_day"] = data_short["veggies_day"].map(mapping_veg)

            # regrouper very likely / very unlikely
            data_short.loc[data_short["veggies_day"] == "very likely", "veggies_day"] = "likely"
            data_short.loc[data_short["veggies_day"] == "very unlikely", "veggies_day"] = "unlikely"


            # --- regroupement income ---
            def income_group(x):
                if x == "less than $15,000":
                    return "No income"
                elif x in ["$15,001 to $30,000", "$30,001 to $50,000"]:
                    return "Low income (less than $50,000 a year)"
                else:
                    return "High income"

            data_short["income_group"] = data_short["income"].apply(income_group)


            # --- calcul pourcentage ---
            grouped = (
                data_short
                .groupby(["income_group", "veggies_day"])
                .size()
                .reset_index(name="count")
            )

            grouped["percentage"] = grouped.groupby("income_group")["count"].transform(lambda x: x / x.sum() * 100)


            # --- graphique Altair ---
            chart = alt.Chart(grouped).mark_bar().encode(
                x=alt.X("income_group:N", title="Income category",sort=["No income", "Low income (less than $50,000 a year)", "High income"],axis=alt.Axis(labelAngle=0)),
                y=alt.Y("percentage:Q", title="Percentage of students"),
                xOffset="veggies_day:N",
                color=alt.Color("veggies_day:N", title="Vegetable consumption likelihood",sort=["unlikely", "neutral", "likely"]),
                tooltip=["income_group", "veggies_day", "percentage"],
            ).properties(
                title="Income vs Likelihood of Eating Vegetables Daily",
                width=600,
            )
            st.altair_chart(chart, use_container_width=True)

            st.write("This chart explores whether students with different financial situations perceive their diet differently. Employment status can partially reflect access to financial resources, as students with part-time jobs may have more money to spend on food. However, the results show relatively similar perceptions of diet healthiness across groups, suggesting that financial differences alone may not strongly influence how healthy students feel their diet is.")
            df["employment_status"] = df["employment"].map({
                1: "Part-time employed",
                2: "Part-time employed",
                3: "Unemployed"
            })


            def healthy_group(x):
                if x <= 4:
                    return "Unhealthy"
                elif x <= 7:
                    return "Moderately healthy"
                else:
                    return "Healthy"


            df["healthy_group"] = df["healthy_feeling"].apply(healthy_group)
            print(df[["healthy_feeling", "healthy_group"]].head())
            health_dist = (
                df.groupby(["employment_status", "healthy_group"])
                .size()
                .reset_index(name="count")
            )

            health_dist["percentage"] = (
                health_dist.groupby("employment_status")["count"]
                .transform(lambda x: x / x.sum() * 100)
            )

            import altair as alt

            chart = alt.Chart(health_dist).mark_bar(size=30).encode(

                x=alt.X(
                    "employment_status:N",
                    title="Employment status",
                    axis=alt.Axis(labelAngle=0)
                ),

                y=alt.Y(
                    "percentage:Q",
                    title="Percentage of students"
                ),

                xOffset="healthy_group:N",

                color=alt.Color(
                    "healthy_group:N",
                    title="Perceived diet healthiness",
                    sort=["Unhealthy", "Moderately healthy", "Healthy"]
                )

            ).properties(
                title="Perceived Diet Healthiness by Employment Status",
                width=300
            )

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