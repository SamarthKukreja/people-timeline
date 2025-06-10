import json
import os
import pandas as pd
from io import StringIO

DATA_FILE = "timeline_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            # Read the content of the file
            content = f.read()
            # If the file is not empty, load the JSON data
            if content:
                return json.loads(content)
            else:
                # If the file is empty, return an empty list
                return []
    # If the file does not exist, return an empty list
    return []


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def export_data_as_csv(data):
    df = pd.DataFrame(data)
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()


def export_data_as_json(data):
    return json.dumps(data, indent=2)
