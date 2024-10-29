import pandas as pd
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the dataset
data = pd.read_csv('clinical_trials.csv')

def preprocess_data(df):
    df['search_text'] = df[['Study Title', 'Conditions', 'Interventions', 'Brief Summary']].fillna('').apply(lambda x: ' '.join(x), axis=1)
    df['search_text'] = df['search_text'].str.lower()
    return df

data = preprocess_data(data)

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
}

def get_synonyms(term):
    term = term.lower()
    synonyms = set()
    for syn_list in synonyms_dict.values():
        if term in syn_list:
            synonyms.update(syn_list)
    if not synonyms:
        synonyms.add(term)
    return list(synonyms)

def search_trials(query):
    terms = re.findall(r'\w+', query.lower())
    term_synonyms_list = []
    for term in terms:
        synonyms = get_synonyms(term)
        term_synonyms_list.append(synonyms)
    def match_trial(text):
        text = text.lower()
        for synonyms in term_synonyms_list:
            if not any(syn in text for syn in synonyms):
                return False
        return True
    matches = data[data['search_text'].apply(match_trial)]
    return matches

@ app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    results = search_trials(query)
    results = results[['NCT Number', 'Study Title', 'Conditions', 'Interventions', 'Study Status', 'Study URL']]

    # Replace NaN with None
    results = results.where(pd.notnull(results), None)

    results_dict = results.to_dict(orient='records')
    return jsonify(results_dict)


if __name__ == '__main__':
    app.run(debug=True)
