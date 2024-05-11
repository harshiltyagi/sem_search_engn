from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Elasticsearch setup
ELASTICSEARCH_URL = 'https://elastic:ML4SEc-8wHtqH2W067cC@localhost:9200'
es = Elasticsearch([ELASTICSEARCH_URL], verify_certs=False)
index_name = 'citeseer_papers_index_v2'  # Replace with your index name


# Function to retrieve suggestions
def get_suggestions(query_text):
    es_query = {
        "suggest": {
            "text": query_text,
            "simple_phrase": {
                "phrase": {
                    "field": "content",
                    "size": 5,
                    "gram_size": 1,
                    "direct_generator": [
                        {
                            "field": "content",
                            "suggest_mode": "always",
                            "min_word_length": 1
                        }
                    ]
                }
            }
        }
    }

    # Execute the Elasticsearch query for suggestions
    response = es.search(index=index_name, body=es_query)

    # Process the response and extract suggestions
    suggestions = [suggestion['_source']['content'] for suggestion in
                   response['suggest']['simple_phrase'][0]['options']]
    return suggestions


# Routes
@app.route('/')
def index():
    # Get suggestions for the dropdown
    query_text = "your_query_here"  # Replace with an actual query text
    suggestions = get_suggestions(query_text)

    return render_template('index.html', suggestions=suggestions)


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    # Your search logic here...
    pass


if __name__ == '__main__':
    app.run(debug=True)
