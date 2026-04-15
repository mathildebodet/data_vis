
'''To run this Streamlit app, use the command: `streamlit run project.py` in your terminal.'''

import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Student Eating Habits",
    layout="wide"
)

# Remove white background from plate image
def remove_white_background(image_path, output_path="output.png", threshold=245):
    '''Remove white background from an image and save the result as a new image.'''
    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)
    rgb = data[:, :, :3]
    alpha = data[:, :, 3]
    white_mask = (rgb[:, :, 0] > threshold) & \
                 (rgb[:, :, 1] > threshold) & \
                 (rgb[:, :, 2] > threshold)
    alpha[white_mask] = 0
    result = np.dstack((rgb, alpha)).astype(np.uint8)
    output_img = Image.fromarray(result, "RGBA")
    return output_img

plate = remove_white_background("plate.jpg")

st.markdown("""
    <style>
    img { filter: invert(1); }
    </style>
""", unsafe_allow_html=True)

# Semantic color scales — one palette per variable

# Veggie
VEG_SORT   = ["unlikely", "neutral", "likely"]
VEG_SCALE  = alt.Scale(domain=VEG_SORT, range=["#e07b7b", "#f7c87a", "#82c982"])

# Health: red
HEALTH_SORT  = ["Unhealthy", "Moderately healthy", "Healthy"]
HEALTH_SCALE = alt.Scale(domain=HEALTH_SORT, range=["#e07b7b", "#f7c87a", "#82c982"])

# Comfort food
REASON_ORDER = ["Stress", "Boredom", "Depression/Sadness", "Other"]
REASON_SCALE = alt.Scale(
    domain=REASON_ORDER,
    range=["#e07b7b", "#f7c87a", "#7bb3e0", "#c0c0c0"]
)

# Eating out
EATOUT_SCALE = alt.Scale(scheme="blues")

# Cooking
COOK_SCALE = alt.Scale(scheme="tableau10")

# Constraint grouping colors — one color per constraint category value
INCOME_SCALE     = alt.Scale(scheme="oranges")
LIVING_SCALE     = alt.Scale(scheme="teals")
GRADE_SCALE      = alt.Scale(scheme="purplered")
GRADE_ORDER      = ["Freshman", "Sophomore", "Junior", "Senior"]

# Load preprocessed data
df = pd.read_csv("food_preprocessed.csv")

reason_map = {1: "Stress", 2: "Boredom", 3: "Depression/Sadness",
              4: "Other", 5: "Other", 6: "Other", 7: "Other", 8: "Other", 9: "Other"}
grade_map  = {1: "Freshman", 2: "Sophomore", 3: "Junior", 4: "Senior"}
df["Reason"]      = df["comfort_food_reasons_coded"].map(reason_map)
df["Grade Level"] = df["grade_level"].map(grade_map)

# helper functions

def make_veggie_chart(data, group_col, group_title, group_sort=None, group_scale=None):
    '''Stacked bar: X = Vegetable Eating Likelihood, color = group_col'''
    grouped = (
        data.groupby(["Vegetable Eating Likelihood", group_col])
        .size().reset_index(name="count")
    )
    grouped["percentage"] = grouped.groupby(group_col)["count"].transform(
        lambda x: x / x.sum() * 100)
    scale = group_scale or alt.Scale(scheme="tableau10")
    return (
        alt.Chart(grouped).mark_bar().encode(
            x=alt.X("Vegetable Eating Likelihood:N", title="Vegetable Eating Likelihood",
                    sort=VEG_SORT, axis=alt.Axis(labelAngle=0, labelFontSize=12)),
            y=alt.Y("percentage:Q", title="% of students"),
            xOffset=alt.XOffset(f"{group_col}:N", sort=group_sort),
            color=alt.Color(f"{group_col}:N", title=group_title,
                            sort=group_sort, scale=scale),
            tooltip=[
                alt.Tooltip("Vegetable Eating Likelihood:N"),
                alt.Tooltip(f"{group_col}:N", title=group_title),
                alt.Tooltip("percentage:Q", format=".1f", title="%")
            ]
        ).properties(height=320)
    )


def make_health_chart(data, group_col, group_title, group_sort=None, group_scale=None):
    '''Stacked bar: X = Healthy Feeling Group, color = group_col'''
    grouped = (
        data.groupby(["Healthy Feeling Group", group_col])
        .size().reset_index(name="count")
    )
    grouped["percentage"] = grouped.groupby(group_col)["count"].transform(
        lambda x: x / x.sum() * 100)
    grouped = grouped[grouped["Healthy Feeling Group"].isin(HEALTH_SORT)]
    scale = group_scale or alt.Scale(scheme="tableau10")
    return (
        alt.Chart(grouped).mark_bar().encode(
            x=alt.X("Healthy Feeling Group:N", title="Diet Health Perception",
                    sort=HEALTH_SORT, axis=alt.Axis(labelAngle=0, labelFontSize=12)),
            y=alt.Y("percentage:Q", title="% of students"),
            xOffset=alt.XOffset(f"{group_col}:N", sort=group_sort),
            color=alt.Color(f"{group_col}:N", title=group_title,
                            sort=group_sort, scale=scale),
            tooltip=[
                alt.Tooltip("Healthy Feeling Group:N", title="Health Perception"),
                alt.Tooltip(f"{group_col}:N", title=group_title),
                alt.Tooltip("percentage:Q", format=".1f", title="%")
            ]
        ).properties(height=320)
    )


def make_comfort_chart(data, group_col, group_title, group_sort=None):
    """Stacked bar: X = group_col, color = Reason"""
    df_f = data.dropna(subset=["Reason"])
    grouped = (
        df_f.groupby([group_col, "Reason"])
        .size().reset_index(name="count")
    )
    grouped["percentage"] = grouped.groupby(group_col)["count"].transform(
        lambda x: x / x.sum() * 100)
    x_enc = alt.X(f"{group_col}:N", title=group_title,
                  sort=group_sort, axis=alt.Axis(labelAngle=0, labelFontSize=12))
    return (
        alt.Chart(grouped).mark_bar().encode(
            x=x_enc,
            y=alt.Y("percentage:Q", title="% of students", stack="normalize",
                    axis=alt.Axis(format="%")),
            color=alt.Color("Reason:N", sort=REASON_ORDER,
                            title="Reason", scale=REASON_SCALE),
            order=alt.Order("Reason:N", sort="ascending"),
            tooltip=[
                alt.Tooltip(f"{group_col}:N", title=group_title),
                alt.Tooltip("Reason:N"),
                alt.Tooltip("percentage:Q", format=".1f", title="%")
            ]
        ).properties(height=320)
    )


def make_eatout_chart(data, group_col, group_title, group_sort=None, group_scale=None):
    '''Stacked bar: X = Eating Out Frequency, color = group_col'''
    grouped = (
        data.groupby(["Eating Out Frequency", group_col])
        .size().reset_index(name="count")
    )
    grouped["percentage"] = grouped.groupby(group_col)["count"].transform(
        lambda x: x / x.sum() * 100)
    scale = group_scale or alt.Scale(scheme="tableau10")
    return (
        alt.Chart(grouped).mark_bar().encode(
            x=alt.X("Eating Out Frequency:N", title="Eating Out Frequency",
                    axis=alt.Axis(labelAngle=0, labelFontSize=12)),
            y=alt.Y("percentage:Q", title="% of students"),
            xOffset=alt.XOffset(f"{group_col}:N", sort=group_sort),
            color=alt.Color(f"{group_col}:N", title=group_title,
                            sort=group_sort, scale=scale),
            tooltip=[
                alt.Tooltip("Eating Out Frequency:N"),
                alt.Tooltip(f"{group_col}:N", title=group_title),
                alt.Tooltip("percentage:Q", format=".1f", title="%")
            ]
        ).properties(height=320)
    )


def make_cooking_donut(data):
    '''Donut chart: Proportion of students in each Cook Frequency category'''
    cook_dist = data["Cook Frequency"].value_counts(normalize=True).reset_index()
    cook_dist.columns = ["Cook Frequency", "Proportion"]
    cook_dist["Proportion"] *= 100
    return (
        alt.Chart(cook_dist).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("Proportion:Q"),
            color=alt.Color("Cook Frequency:N", scale=COOK_SCALE),
            tooltip=["Cook Frequency:N", alt.Tooltip("Proportion:Q", format=".1f")]
        ).properties(height=300)
    )


def make_cooking_donut_by_group(data, group_col):
    '''Donut charts split by group_col (e.g., on/off campus).'''
    cook_dist = (
        data.groupby([group_col, "Cook Frequency"]).size().reset_index(name="count")
    )
    cook_dist["Proportion"] = cook_dist.groupby(group_col)["count"].transform(
        lambda x: x / x.sum() * 100
    )
    return (
        alt.Chart(cook_dist).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("Proportion:Q"),
            color=alt.Color("Cook Frequency:N", scale=COOK_SCALE),
            tooltip=[
                alt.Tooltip(f"{group_col}:N", title=group_col),
                alt.Tooltip("Cook Frequency:N"),
                alt.Tooltip("Proportion:Q", format=".1f")
            ]
        ).properties(height=300).facet(
            column=alt.Column(f"{group_col}:N", title=group_col)
        )
    )


def section(title, chart, caption, accent_color=None):
    """Display title, then chart, then caption — title always on top."""
    if accent_color:
        st.markdown(
            f"""
            <div style="
                border-left: 6px solid {accent_color};
                padding-left: 10px;
                margin-bottom: 4px;
            ">
                <h4 style="margin:0;">{title}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"#### {title}")
    st.altair_chart(chart, use_container_width=True)
    st.caption(caption)
    st.write("")


def conclusion_box(title, text):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #9aa8b5;
            border-left: 6px solid #476a87;
            border-radius: 10px;
            padding: 12px 14px;
            background: rgba(71, 106, 135, 0.08);
            margin-top: 8px;
            margin-bottom: 10px;
        ">
            <strong>{title}</strong><br>
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")


def get_captions_for_group(group_col):
    '''Return a dictionary of captions for each variable, based on the selected grouping column.'''
    if group_col == "Income Group":
        return {
            "Veggie": (
                "One might expect income to strongly influence vegetable consumption. "
                "However, the distribution across income groups is relatively balanced. "
                "Even students with little or no income report similar or higher "
                "vegetable consumption, suggesting that income alone may not strongly "
                "determine this aspect of students' diets."
            ),
            "Health": (
                "No clear trend emerges from diet health perception across income "
                "groups. Interestingly, higher-income students are slightly more "
                "represented among those who eat poorly, which challenges the "
                "assumption that more money leads to a healthier diet."
            ),
            "Comfort": (
                "Stress stands out as the dominant comfort food trigger for no-income "
                "students, more so than for other groups. This may reflect the "
                "additional psychological pressure of managing a very tight budget on "
                "top of academic demands."
            ),
            "EatOut": (
                "Students with no income are more likely to never eat out - a logical "
                "consequence of budget constraints. Rather than a dietary choice, this "
                "reflects a financial one: when money is tight, eating out is simply "
                "not an option."
            ),
            "Cooking": (
                "High income students slightly cook less often than lower income ones, but the gap is small and not strongly significant. "
            )
        }

    if group_col == "Living Situation":
        return {
            "Veggie": (
                "Both on-campus and off-campus students tend to report likely vegetable "
                "consumption, with very limited differences between the two groups."
            ),
            "Health": (
                "Diet health perception looks very similar across on-campus and "
                "off-campus students, suggesting no meaningful separation on this "
                "indicator."
            ),
            "Comfort": (
                "Stress appears slightly more frequent among off-campus students as a "
                "comfort food trigger, but the gap is small and not strongly "
                "significant."
            ),
            "EatOut": (
                "Eating-out frequency shows the clearest difference: off-campus "
                "students eat out substantially more often than on-campus students."
            ),
            "Cooking": (
                "Surprisingly, on-campus students report slightly more often that they "
                "do not have much time to cook. Still, across all students, the clear "
                "majority says they cook only when they have time, and not very often."
            )
        }

    if group_col == "Grade Level":
        return {
            "Veggie": (
                "Across Freshman, Sophomore, Junior and Senior groups, vegetable-eating "
                "patterns remain very similar, with no clearly meaningful gap."
            ),
            "Health": (
                "Perceived diet health is also broadly comparable across grade levels, "
                "without a strong or consistent trend."
            ),
            "Comfort": (
                "Comfort-food motives look close across grade levels. Any differences "
                "are small and not clearly significant."
            ),
            "EatOut": (
                "Eating-out frequency does not show a robust separation by grade level; "
                "observed differences appear limited."
            ),
            "Cooking": (
                "Cooking patterns also stay relatively close between grade levels."
            )
        }

    return {
        "Veggie": (
            "Vegetable consumption stays fairly distributed across groups. The "
            "constraint seems to shape differences only slightly, suggesting other "
            "factors also play an important role."
        ),
        "Health": (
            "Perceived diet health varies between groups, but without a single dominant "
            "pattern. This points to a mixed effect of the selected constraint."
        ),
        "Comfort": (
            "Emotional reasons remain central for comfort food in all groups, though "
            "the balance between stress, boredom and sadness changes depending on the "
            "constraint."
        ),
        "EatOut": (
            "Eating-out habits differ by group, indicating that the selected constraint "
            "can influence how often students rely on food outside home."
        ),
        "Cooking": (
            "Many students cook only whenever they can, indicating time constraints "
            "strongly limit home cooking."
        )
    }


def get_constraint_conclusion(group_col):
    '''Return a conclusion title and text based on the selected grouping column.'''
    if group_col == "Income Group":
        return (
            "Conclusion (Budget)",
            "Budget mainly affects behaviors with direct financial cost, especially "
            "eating out, while its effect is weaker on vegetable intake and perceived "
            "diet health."
        )

    if group_col == "Living Situation":
        return (
            "Conclusion (Time)",
            "Living situation and time constraints in general have limited impact on vegetable intake, health "
            "perception and comfort-food motives, but it strongly influences practical "
            "habits like eating out and cooking frequency."
        )

    if group_col == "Grade Level":
        return (
            "Conclusion (Academic Workload)",
            "No pattern appears clearly significant across grade levels. This suggests "
            "grade level may be a weak proxy for actual academic workload: students in "
            "the same year can still experience very different course loads, schedules "
            "and stress levels."
        )

    return (
        "Conclusion",
        "No strong conclusion is available for this grouping."
    )


def get_constraint_accent(group_col):
    if group_col == "Income Group":
        return "#d97706"
    if group_col == "Living Situation":
        return "#0f766e"
    if group_col == "Grade Level":
        return "#9d174d"
    return "#476a87"


def get_variable_comparative_conclusion(variable_key):
    '''Return a comparative conclusion title and text based on the selected variable.'''
    if variable_key == "Veggie":
        return (
            "Comparative Conclusion (Vegetable Eating)",
            "Vegetable eating is the least sensitive variable to constraints: Budget, "
            "Time and Academic Workload all show similar distributions, with no clear "
            "dominant driver. Overall, students seem to be very likely to eat vegetables often."
        )

    if variable_key == "Health":
        return (
            "Comparative Conclusion (Diet Health Perception)",
            "Perceived diet health changes little across constraints. None of the three "
            "constraints clearly stands out as a strong influence on this variable."
        )

    if variable_key == "Comfort":
        return (
            "Comparative Conclusion (Comfort Food Reasons)",
            "Comfort-food motives remain broadly stable across constraints. Time shows "
            "only a slight increase in stress off-campus as well as for student with no income, but the effect appears weak."
        )

    if variable_key == "EatOut":
        return (
            "Comparative Conclusion (Eating Out Frequency)",
            "Eating out is the most constraint-sensitive variable. Budget and Time show "
            "the clearest effects (less eating out with lower income, more eating out "
            "off-campus), while Academic Workload remains weakly differentiated."
        )

    if variable_key == "Cooking":
        return (
            "Comparative Conclusion (Cooking Frequency)",
            "Cooking frequency differs more clearly with Time constraints "
            " than with Budget or Academic Workload. Across all groups, most "
            "students still report cooking mainly when they have time."
        )

    return (
        "Comparative Conclusion",
        "No comparative conclusion is available for this variable."
    )


def render_all_charts(data, group_col, group_title, group_sort=None,
                      group_scale=None, show_cooking=False):
    '''Render all charts for a given grouping column, with appropriate titles and captions.'''
    captions = get_captions_for_group(group_col)

    section(
        f"🥦 Vegetable Eating Likelihood by {group_title}",
        make_veggie_chart(data, group_col, group_title, group_sort, group_scale),
        captions["Veggie"]
    )
    section(
        f"💚 Diet Health Perception by {group_title}",
        make_health_chart(data, group_col, group_title, group_sort, group_scale),
        captions["Health"]
    )
    section(
        f"🍫 Comfort Food Reasons by {group_title}",
        make_comfort_chart(data, group_col, group_title, group_sort),
        captions["Comfort"]
    )
    section(
        f"🍔 Eating Out Frequency by {group_title}",
        make_eatout_chart(data, group_col, group_title, group_sort, group_scale),
        captions["EatOut"]
    )
    if show_cooking:
        cooking_chart = make_cooking_donut_by_group(data, group_col)
        section(
            "🍳 Cooking Frequency among Students",
            cooking_chart,
            captions["Cooking"],
            accent_color=get_constraint_accent(group_col)
        )


# Title and subtitle
st.title("What Shapes Student Eating Habits?")
st.markdown(
    "Students' diets are influenced by many factors. "
    "Explore how **Budget**, **Time**, and **Workload** each affect eating habits."
)
st.divider()

#Two views : constraint and variable
tab1, tab2 = st.tabs([
    "🔍 Explore by Constraint — What does each constraint influence?",
    "📊 Explore by Variable — How do constraints compare on the same habit?"
])

# TAB 1 - By Constraint

with tab1:
    st.markdown("*Deep-dive into what each constraint influences on students' eating habits.*")
    col_left, col_right = st.columns([0.15, 0.85], gap="large")

    with col_left:
        st.image(plate, width=400)
        st.markdown("**Select a constraint:**")
        st.write("")
        if st.button("💰 Budget",   use_container_width=True, key="btn_budget"):
            st.session_state["choice_constraint"] = "Budget"
        if st.button("⏱ Time",     use_container_width=True, key="btn_time"):
            st.session_state["choice_constraint"] = "Time"
        if st.button("📚 Workload", use_container_width=True, key="btn_workload"):
            st.session_state["choice_constraint"] = "Workload"

    choice_c = st.session_state.get("choice_constraint", None)

    with col_right:
        if choice_c is None:
            st.info("👈 Click a constraint on the left to explore the data.")
        elif choice_c == "Budget":
            st.header("💰 Budget & Eating Habits")
            st.markdown("*Key indicator: Income Group*")
            render_all_charts(df, "Income Group", "Income Group",
                              group_scale=INCOME_SCALE, show_cooking=True)
            title, text = get_constraint_conclusion("Income Group")
            conclusion_box(title, text)
        elif choice_c == "Time":
            st.header("⏱ Time Constraints & Eating Habits")
            st.markdown("*Key indicator: Living Situation (on/off campus)*")
            render_all_charts(df, "Living Situation", "Living Situation",
                              group_scale=LIVING_SCALE, show_cooking=True)
            title, text = get_constraint_conclusion("Living Situation")
            conclusion_box(title, text)
        elif choice_c == "Workload":
            st.header("📚 Academic Workload & Eating Habits")
            st.markdown("*Key indicator: Grade Level*")
            render_all_charts(df, "Grade Level", "Grade Level",
                              group_sort=GRADE_ORDER, group_scale=GRADE_SCALE,
                              show_cooking=True)
            title, text = get_constraint_conclusion("Grade Level")
            conclusion_box(title, text)

# TAB 2 — By Variable

with tab2:
    st.markdown("*Compare how Budget, Time and Workload affect the same eating habit.*")
    col_left2, col_right2 = st.columns([0.15, 0.85], gap="large")

    with col_left2:
        st.image(plate, width=400)
        st.markdown("**Select a variable:**")
        st.write("")
        if st.button("🥦 Vegetable Eating",      use_container_width=True, key="btn_veg"):
            st.session_state["choice_variable"] = "Veggie"
        if st.button("💚 Diet Health Perception", use_container_width=True, key="btn_health"):
            st.session_state["choice_variable"] = "Health"
        if st.button("🍫 Comfort Food Reasons",   use_container_width=True, key="btn_comfort"):
            st.session_state["choice_variable"] = "Comfort"
        if st.button("🍔 Eating Out Frequency",   use_container_width=True, key="btn_eatout"):
            st.session_state["choice_variable"] = "EatOut"
        if st.button("🍳 Cooking Frequency",   use_container_width=True, key="btn_cooking"):
            st.session_state["choice_variable"] = "Cooking"

    choice_v = st.session_state.get("choice_variable", None)

    # chart-maker dispatch
    CHART_FN = {
        "Veggie":  lambda gc, gt, gs: make_veggie_chart(df, gc, gt, gs,
                       INCOME_SCALE if gc == "Income Group" else
                       LIVING_SCALE if gc == "Living Situation" else GRADE_SCALE),
        "Health":  lambda gc, gt, gs: make_health_chart(df, gc, gt, gs,
                       INCOME_SCALE if gc == "Income Group" else
                       LIVING_SCALE if gc == "Living Situation" else GRADE_SCALE),
        "Comfort": lambda gc, gt, gs: make_comfort_chart(df, gc, gt, gs),
        "EatOut":  lambda gc, gt, gs: make_eatout_chart(df, gc, gt, gs,
                       INCOME_SCALE if gc == "Income Group" else
                       LIVING_SCALE if gc == "Living Situation" else GRADE_SCALE),
        "Cooking": lambda gc, gt, gs: make_cooking_donut_by_group(df, gc),
    }

    TITLES = {
        "Veggie":  "🥦 Vegetable Eating Likelihood",
        "Health":  "💚 Diet Health Perception",
        "Comfort": "🍫 Comfort Food Reasons",
        "EatOut":  "🍔 Eating Out Frequency",
        "Cooking": "🍳 Cooking Frequency",
    }

    CONSTRAINTS = [
        ("💰 Budget",   "Income Group",   "Income Group",   None),
        ("⏱ Time",     "Living Situation","Living Situation",None),
        ("📚 Workload", "Grade Level",    "Grade Level",    GRADE_ORDER),
    ]

    with col_right2:
        if choice_v is None:
            st.info("👈 Click a variable on the left to compare across constraints.")
        else:
            st.subheader(f"{TITLES[choice_v]} — Budget vs Time vs Workload")
            st.markdown("*There is one chart per constraint to allow comparison between them.*")
            st.write("")
            fn = CHART_FN[choice_v]
            for label, gc, gt, gs in CONSTRAINTS:
                st.markdown(
                    f"<div style='border-left: 5px solid {get_constraint_accent(gc)}; padding-left: 8px; margin-bottom: 4px;'><strong>{label}</strong> — <em>{gt}</em></div>",
                    unsafe_allow_html=True
                )
                st.altair_chart(fn(gc, gt, gs), use_container_width=True)
                st.caption(get_captions_for_group(gc)[choice_v])
                st.write("")
            comp_title, comp_text = get_variable_comparative_conclusion(choice_v)
            conclusion_box(comp_title, comp_text)