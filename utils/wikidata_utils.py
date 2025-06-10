import requests
from utils.data_handler import load_data, save_data
import streamlit as st


def get_wikidata_id(wikipedia_title):
    search_url = "https://en.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": wikipedia_title,
        "format": "json",
    }

    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    search_results = search_data.get("query", {}).get("search", [])

    if not search_results:
        return None  # No matches found

    # Get the title of the top search result (assume confidence > 80%)
    best_match_title = search_results[0]["title"]

    # Now fetch the wikidata ID using the best match title
    detail_url = "https://en.wikipedia.org/w/api.php"
    detail_params = {
        "action": "query",
        "format": "json",
        "prop": "pageprops",
        "titles": best_match_title,
    }
    detail_response = requests.get(detail_url, params=detail_params)
    detail_data = detail_response.json()
    pages = detail_data["query"]["pages"]
    for page in pages.values():
        return page.get("pageprops", {}).get("wikibase_item")
    return None


def get_birth_death_from_wikidata(wikidata_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    response = requests.get(url)
    data = response.json()
    entity = data["entities"][wikidata_id]
    claims = entity["claims"]

    def extract_date(prop):
        if prop in claims:
            datavalue = claims[prop][0]["mainsnak"]["datavalue"]
            return datavalue["value"]["time"].strip("+").split("T")[0]
        return None

    birth_date = extract_date("P569")
    death_date = extract_date("P570")

    return birth_date, death_date or "Present"


def add_person(title):
    wikidata_id = get_wikidata_id(title)
    if not wikidata_id:
        st.error("❌ Wikidata ID not found. Please check the title.")
        return

    birth, death = get_birth_death_from_wikidata(wikidata_id)
    if not birth:
        st.error("❌ Birth date not found.")
        return

    person = {
        "name": title.replace("_", " "),
        "birth": birth,
        "death": death or "Present",
    }

    data = load_data()
    if any(p["name"].lower() == person["name"].lower() for p in data):
        st.warning("⚠️ Person already exists in timeline.")
        return

    data.append(person)
    save_data(data)
    st.success(f"✅ {person['name']} added to timeline.")
