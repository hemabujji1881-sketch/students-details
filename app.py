import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Student Details Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "student_dropout_behavior_dataset.csv"

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    # Convert common numeric fields safely, if present.
    numeric_cols = [
        "age", "quiz1_marks", "quiz2_marks", "quiz3_marks",
        "total_assignments", "assignments_submitted", "midterm_marks",
        "final_marks", "previous_gpa", "total_lectures",
        "lectures_attended", "total_lab_sessions", "labs_attended"
    ]
    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data

st.title("🎓 Student Details & Performance Dashboard")
st.caption("Interactive dashboard — use the sidebar filters to update every chart and KPI.")

if not DATA_PATH.exists():
    st.error("Dataset file not found. Put student_dropout_behavior_dataset.csv in the same folder as app.py.")
    st.stop()

df = load_data(DATA_PATH)

# Derived fields used by the dashboard.
if {"lectures_attended", "total_lectures"}.issubset(df.columns):
    df["lecture_attendance_pct"] = (
        df["lectures_attended"] / df["total_lectures"].replace(0, pd.NA) * 100
    ).fillna(0).clip(0, 100)
if {"labs_attended", "total_lab_sessions"}.issubset(df.columns):
    df["lab_attendance_pct"] = (
        df["labs_attended"] / df["total_lab_sessions"].replace(0, pd.NA) * 100
    ).fillna(0).clip(0, 100)
mark_cols = [c for c in ["quiz1_marks", "quiz2_marks", "quiz3_marks", "midterm_marks", "final_marks"] if c in df.columns]
if mark_cols:
    df["average_marks"] = df[mark_cols].mean(axis=1)

# ---------------- Sidebar: all filters apply to all charts ----------------
st.sidebar.header("🔎 Dashboard Filters")
filtered = df.copy()

if "name" in filtered.columns:
    names = sorted(filtered["name"].dropna().astype(str).unique().tolist())
    chosen_names = st.sidebar.multiselect("Student name", names, default=[])
    if chosen_names:
        filtered = filtered[filtered["name"].astype(str).isin(chosen_names)]

if "gender" in filtered.columns:
    genders = sorted(filtered["gender"].dropna().astype(str).unique().tolist())
    chosen_genders = st.sidebar.multiselect("Gender", genders, default=genders)
    if chosen_genders:
        filtered = filtered[filtered["gender"].astype(str).isin(chosen_genders)]
    else:
        filtered = filtered.iloc[0:0]

if "age" in filtered.columns and filtered["age"].notna().any():
    min_age = int(filtered["age"].min())
    max_age = int(filtered["age"].max())
    age_range = st.sidebar.slider("Age range", min_age, max_age, (min_age, max_age))
    filtered = filtered[filtered["age"].between(age_range[0], age_range[1])]

if "student_id" in filtered.columns:
    ids = sorted(pd.to_numeric(filtered["student_id"], errors="coerce").dropna().astype(int).unique().tolist())
    if ids:
        use_id_filter = st.sidebar.checkbox("Filter by student ID")
        if use_id_filter:
            selected_ids = st.sidebar.multiselect("Student ID", ids, default=[])
            if selected_ids:
                filtered = filtered[pd.to_numeric(filtered["student_id"], errors="coerce").isin(selected_ids)]
            else:
                filtered = filtered.iloc[0:0]

st.sidebar.divider()
if st.sidebar.button("Reset all filters", use_container_width=True):
    st.rerun()

# Summary metrics always reflect the filtered dataset.
if filtered.empty:
    st.warning("No students match the selected filters. Change or reset the sidebar filters.")
    st.stop()

n_students = len(filtered)
avg_age = filtered["age"].mean() if "age" in filtered.columns else None
avg_marks = filtered["average_marks"].mean() if "average_marks" in filtered.columns else None
avg_att = filtered["lecture_attendance_pct"].mean() if "lecture_attendance_pct" in filtered.columns else None

m1, m2, m3, m4 = st.columns(4)
m1.metric("Students", f"{n_students:,}")
m2.metric("Average age", f"{avg_age:.1f}" if pd.notna(avg_age) else "N/A")
m3.metric("Average marks", f"{avg_marks:.1f}" if pd.notna(avg_marks) else "N/A")
m4.metric("Lecture attendance", f"{avg_att:.1f}%" if pd.notna(avg_att) else "N/A")

st.divider()

# Charts all use `filtered`, so every sidebar selection updates all visuals.
left, right = st.columns(2)

with left:
    st.subheader("Students by gender")
    if "gender" in filtered.columns:
        gender_counts = filtered["gender"].fillna("Unknown").value_counts().rename_axis("Gender").reset_index(name="Students")
        fig = px.pie(gender_counts, names="Gender", values="Students", hole=0.45,
                     title="Gender distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Gender column is not available.")

with right:
    st.subheader("Age distribution")
    if "age" in filtered.columns:
        fig = px.histogram(filtered, x="age", nbins=12, color="gender" if "gender" in filtered.columns else None,
                           title="Student count by age", labels={"age": "Age"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Age column is not available.")

left, right = st.columns(2)
with left:
    st.subheader("Marks comparison")
    available_marks = [c for c in ["quiz1_marks", "quiz2_marks", "quiz3_marks", "midterm_marks", "final_marks"] if c in filtered.columns]
    if available_marks:
        marks_long = filtered.melt(
            id_vars=["name"] if "name" in filtered.columns else None,
            value_vars=available_marks, var_name="Assessment", value_name="Marks"
        ).dropna(subset=["Marks"])
        fig = px.box(marks_long, x="Assessment", y="Marks", points="outliers",
                     title="Marks spread by assessment")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No assessment marks columns were found.")

with right:
    st.subheader("Average marks by student")
    if {"name", "average_marks"}.issubset(filtered.columns):
        top = filtered.sort_values("average_marks", ascending=False)
        fig = px.bar(top, x="name", y="average_marks", color="average_marks",
                     title="Average marks for selected students",
                     labels={"name": "Student", "average_marks": "Average marks"})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Student name or marks columns are unavailable.")

left, right = st.columns(2)
with left:
    st.subheader("Lecture and lab attendance")
    attendance_cols = [c for c in ["lecture_attendance_pct", "lab_attendance_pct"] if c in filtered.columns]
    if attendance_cols and "name" in filtered.columns:
        att_long = filtered[["name"] + attendance_cols].melt(id_vars="name", var_name="Session type", value_name="Attendance (%)")
        att_long["Session type"] = att_long["Session type"].replace({
            "lecture_attendance_pct": "Lectures", "lab_attendance_pct": "Labs"
        })
        fig = px.bar(att_long, x="name", y="Attendance (%)", color="Session type",
                     barmode="group", title="Attendance percentage by student")
        fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Attendance columns are not available.")

with right:
    st.subheader("Previous GPA")
    if "previous_gpa" in filtered.columns:
        fig = px.histogram(filtered, x="previous_gpa", nbins=12,
                           title="Distribution of previous GPA")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Previous GPA column is not available.")

st.divider()
st.subheader("Filtered student records")
st.caption(f"Showing {len(filtered):,} of {len(df):,} records after applying the sidebar filters.")
st.dataframe(filtered, use_container_width=True, hide_index=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered records as CSV",
    data=csv,
    file_name="filtered_student_records.csv",
    mime="text/csv",
)

with st.expander("About this dataset and project"):
    st.write(
        "This dashboard uses the uploaded student_dropout_behavior_dataset.csv file. "
        "It includes student ID, name, age, gender, quiz and exam marks, GPA, assignments, "
        "and attendance fields. It does not include father name, mother name, phone number, "
        "home address, or branch. Those fields have not been fabricated."
    )
