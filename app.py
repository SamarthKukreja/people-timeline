import streamlit as st

st.set_page_config(page_title="Famous People Timeline", layout="wide")

from utils.wikidata_utils import add_person
from utils.data_handler import (
    load_data,
    export_data_as_csv,
    export_data_as_json,
    clear_data_file,
)
from utils.timeline_plotter import plot_timeline, filter_data_by_year
import datetime

st.title("📜 Timeline after year 1678")
st.markdown("Enter a **Wikipedia title** to add them to the timeline.")

with st.form("add_person_form"):
    person_title = st.text_input(
        "Enter Wikipedia Title:", help="Example: Albert_Einstein"
    )
    submitted = st.form_submit_button("Add to Timeline")
    if submitted and person_title:
        add_person(person_title.strip().replace(" ", "_"))

st.divider()
st.subheader("📆 Filter Timeline")

data = load_data()
print(data)
if data and data != "empty":
    # min_year = min(int(p["birth"][:4]) for p in data)
    min_year = 1678
    # max_year = max(
    #     int(p["death"][:4]) if p["death"] != "Present" else datetime.datetime.now().year
    #     for p in data
    # )
    max_year = 2025
    year_range = st.slider(
        "Select birth year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )
    filtered_data = filter_data_by_year(data, year_range)
    plot_timeline(filtered_data)
else:
    st.info("Add a person to begin building your timeline.")

st.divider()
st.subheader("📤 Export Timeline Data")

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "📥 Export as CSV",
        export_data_as_csv(data),
        file_name="timeline_data.csv",
        mime="text/csv",
    )

with col2:
    st.download_button(
        "📥 Export as JSON",
        export_data_as_json(data),
        file_name="timeline_data.json",
        mime="application/json",
    )


st.divider()  # Visual separator
st.subheader("🗑️ Manage Timeline Data")

# Button to clear all timeline data
if st.button("🚨 Clear All Timeline Data", key="clear_data_button"):
    clear_data_file()  # Call the function to empty the JSON file
    st.success("Timeline data cleared!")  # Provide user feedback
    st.experimental_rerun()  # Rerun the app to reflect the empty timeline
