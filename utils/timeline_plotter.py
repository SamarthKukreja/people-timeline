import plotly.express as px
import pandas as pd
from datetime import datetime
import streamlit as st


def safe_parse_date(date_str):
    """Converts malformed date like '1440-00-00' to datetime object by replacing 00 with 1."""
    try:
        if not date_str or not isinstance(date_str, str):
            return None
        parts = date_str.strip().split("-")
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 and parts[1] != "00" else "01"
        day = int(parts[2]) if len(parts) > 1 and parts[2] != "00" else "01"

        dt = datetime(year, int(month), int(day))
        return dt
    except Exception as e:
        print(f"🚨 Failed to parse date: {date_str} → {e}")
        return None


def plot_timeline(data):
    records = []
    skipped = []

    for person in data:
        name = person.get("name", "Unknown")

        birth_raw = person.get("birth", "")
        birth = safe_parse_date(birth_raw)

        if not birth:
            skipped.append((name, "birth", birth_raw))
            continue

        death_raw = person.get("death", "")
        if isinstance(death_raw, str) and death_raw.strip().lower() == "present":
            death = datetime.today()  # used for plotting only
            is_alive = True
        else:
            death = safe_parse_date(death_raw)
            is_alive = False
            if not death:
                skipped.append((name, "death", death_raw))
                continue

        records.append(
            {
                "Name": name,
                "Start": birth,
                "End": death,
                "Status": "Alive" if is_alive else "Deceased",
            }
        )

    if not records:
        st.warning("⚠️ No valid data to plot.")
        return

    df = pd.DataFrame(records)

    # # 🔥 Enforce datetime64[ns] explicitly
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["End"] = pd.to_datetime(df["End"], errors="coerce")

    # 🧹 Drop rows with invalid dates
    df.dropna(subset=["Start", "End"], inplace=True)

    if df.empty:
        st.error("❌ All date values failed to parse.")
        return

    df["PlottedEnd"] = df.apply(
        lambda row: row["End"] if row["Status"] == "Deceased" else datetime.today(),
        axis=1,
    )

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="PlottedEnd",  # ✅ This column handles Alive vs Deceased correctly
        y="Name",
        color="Name",
        title="📜 Life Timeline of Famous People",
        hover_data=["Name", "Start", "PlottedEnd", "Status"],
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template="plotly_white", height=600)
    st.plotly_chart(fig, use_container_width=True)

    if skipped:
        st.info(f"ℹ️ Skipped {len(skipped)} entries due to invalid dates: {skipped}")


def filter_data_by_year(data, year_range):
    start_year, end_year = year_range
    filtered = []
    for person in data:
        try:
            year = int(person["birth"][:4])
            if start_year <= year <= end_year:
                filtered.append(person)
        except:
            continue
    return filtered
