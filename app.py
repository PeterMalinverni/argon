from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)
df = pd.read_csv('clinical_trials.csv')


def search_clinical_trials(df: pd.DataFrame, query: str, max_steps: int = 0) -> list:
    """
    Searches the clinical trials DataFrame for entries matching the query and expands the search
    based on matching Conditions and Interventions up to a specified number of steps.

    Args:
        df (pd.DataFrame): DataFrame containing clinical trials data.
        query (str): Search query string.
        max_steps (int, optional): Number of steps to expand the search. Defaults to 0.

    Returns:
        list: List of dictionaries representing the search results.
    """

    df = df.astype(str)
    current_entries = df[df.apply(lambda row: query.lower() in ' '.join(row).lower(), axis=1)]

    if current_entries.empty:
        return []

    results_set = set(current_entries.index)
    visited_entries = set(current_entries.index)

    for step in range(max_steps):
        conditions = set()
        interventions = set()

        for idx, row in current_entries.iterrows():
            conditions.update(row['Conditions'].split('|'))
            interventions.update(row['Interventions'].split('|'))

        condition_matches = df[df['Conditions'].apply(
            lambda x: any(cond in x.split('|') for cond in conditions))]
        intervention_matches = df[df['Interventions'].apply(
            lambda x: any(interv in x.split('|') for interv in interventions))]

        new_entries = pd.concat([condition_matches, intervention_matches]).drop_duplicates()
        new_entries = new_entries[~new_entries.index.isin(visited_entries)]

        if new_entries.empty:
            break

        visited_entries.update(new_entries.index)
        results_set.update(new_entries.index)
        current_entries = new_entries

    results = df.iloc[list(results_set)]
    return results.to_dict(orient='records')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    """
    Handles the search requests.

    Returns:
        Response: JSON response containing the search results or an error message.
    """

    query = request.args.get('q', '')
    max_steps = int(request.args.get('steps', 0))
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    results = search_clinical_trials(df, query, max_steps=max_steps)
    for result in results:
        result['Interventions'] = ", ".join(result['Interventions'].split('|'))
        result['Conditions'] = ", ".join(result['Conditions'].split('|'))

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
