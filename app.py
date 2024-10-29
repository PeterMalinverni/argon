import pandas as pd
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the dataset
# Ensure 'clinical_trials.csv' is in the same directory
data = pd.read_csv('clinical_trials.csv')

def preprocess_data(df):
    """
    Preprocess the dataset by combining relevant text fields into a single searchable text field.
    """
    # Combine relevant text fields into 'search_text'
    df['search_text'] = df[['Study Title', 'Conditions', 'Interventions', 'Brief Summary']].fillna('').apply(lambda x: ' '.join(x), axis=1)
    df['search_text'] = df['search_text'].str.lower()
    return df

data = preprocess_data(data)

# Synonyms dictionary for disease terms and interventions
synonyms_dict = {
    'nsclc': [
        'nsclc',
        'non small cell lung cancer',
        'non small cell lung carcinoma',
        'carcinoma of the lungs, non small cell',
        'non-small cell lung cancer',
        'non-small cell lung carcinoma',
        'non–small-cell lung cancer'
    ],
    'immunotherapy': [
        'immunotherapy',
        'immunotherapeutic',
        'immune therapy',
        'immune-based therapy',
        'immuno-oncology'
    ],
    # Add more synonyms as needed
}

def get_synonyms(term):
    """
    Retrieve all synonyms for a given term from the synonyms dictionary.
    """
    term = term.lower()
    synonyms = set()
    for syn_list in synonyms_dict.values():
        if term in syn_list:
            synonyms.update(syn_list)
    if not synonyms:
        synonyms.add(term)
    return list(synonyms)

def search_trials(query):
    """
    Search for clinical trials that match the query terms with their synonyms.
    """
    # Split the query into individual terms
    terms = re.findall(r'\w+', query.lower())
    # Get synonyms for each term
    term_synonyms_list = []
    for term in terms:
        synonyms = get_synonyms(term)
        term_synonyms_list.append(synonyms)
    # Match trials that contain at least one synonym from each term
    def match_trial(text):
        text = text.lower()
        for synonyms in term_synonyms_list:
            if not any(syn in text for syn in synonyms):
                return False
            # Strive for near perfect recall by matching partial words
            # e.g., 'cancer' should match 'cancerous'
            for syn in synonyms:
                if syn in text:
                    return True
        return False
    matches = data[data['search_text'].apply(match_trial)]
    return matches

@app.route('/search', methods=['GET'])
def search():
    """
    API endpoint to search for clinical trials.
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    results = search_trials(query)
    # Select relevant columns to display
    results = results[['NCT Number', 'Study Title', 'Conditions', 'Interventions', 'Study Status', 'Study URL']]
    results_dict = results.to_dict(orient='records')
    return jsonify(results_dict)

if __name__ == '__main__':
    app.run(debug=True)
