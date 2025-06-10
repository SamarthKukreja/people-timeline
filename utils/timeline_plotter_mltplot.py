import plotly.express as px
import pandas as pd
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt


def safe_parse_date(date_str):
    """Converts malformed date like '1440-00-00' to datetime object by replacing 00 with 1."""
    try:
        if not date_str or not isinstance(date_str, str):
            return None
        parts = date_str.strip().split("-")
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 and parts[1] != "00" else "01"
        day = int(parts[2]) if len(parts) > 1 and parts[2] != "00" else "01"

        dt = [str(year), str(month), str(day)]
        return "-".join(dt)
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
        if death_raw.strip().lower() == "present":
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

    def safe_parse(date_str):
        try:
            # st.write("Hello")
            # st.write(date_str)
            # st.write(datetime.strptime(date_str, "%Y-%m-%d"))
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None

    df["Start"] = df["Start"].apply(safe_parse)
    df["End"] = df["End"].apply(safe_parse)

    # 🧹 Drop rows with unparseable start or end dates
    df.dropna(subset=["Start", "End"], inplace=True)

    if df.empty:
        st.error("❌ All date values failed to parse.")
        return

    # ✅ Handle "Alive" people by replacing End with today's date
    df["PlottedEnd"] = df.apply(
        lambda row: row["End"] if row["Status"] == "Deceased" else datetime.today(),
        axis=1,
    )

    df["Duration"] = df["PlottedEnd"] - df["Start"]

    # 🎨 Plotting using matplotlib
    fig, ax = plt.subplots(figsize=(10, max(5, len(df) * 0.5)))
    for idx, row in df.iterrows():
        ax.barh(row["Name"], row["Duration"].days, left=row["Start"], color="#1f77b4")

    ax.set_xlabel("Time")
    ax.set_title("📜 Life Timeline of Famous People")
    ax.invert_yaxis()  # Reverse y-axis to match typical timeline order
    st.pyplot(fig)


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
