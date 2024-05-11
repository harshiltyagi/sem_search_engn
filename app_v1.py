import os
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

# Replace these with your Elasticsearch server details
ELASTICSEARCH_URL = 'https://elastic:ML4SEc-8wHtqH2W067cC@localhost:9200'
es = Elasticsearch([ELASTICSEARCH_URL], verify_certs=False)

# Path to the folder containing Citeseer documents
documents_folder = r'C:\Users\harsh\Downloads\citeseer2.tar\2'

# Name of the Elasticsearch index
index_name = 'citeseer_papers_index'

# Check if the index already exists
if not es.indices.exists(index=index_name):
    # Index documents into Elasticsearch
    for root, dirs, files in os.walk(documents_folder):
        for file_name in files:
            if file_name.endswith('.txt'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    document_text = file.read()
                    # Index document into Elasticsearch
                    es.index(index=index_name, body={'text': document_text})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = perform_search(query)
    return render_template('results.html', query=query, results=results)

def perform_search(query):
    search_body = {
        "query": {
            "match": {
                "text": query
            }
        },
        "highlight": {
            "fields": {
                "text": {}
            }
        }
    }
    search_results = es.search(index=index_name, body=search_body)['hits']['hits']
    formatted_results = []
    for hit in search_results:
        title = hit['_source'].get('title', '')  # Replace 'title' with the actual field name for title
        highlight = hit.get('highlight', {}).get('text', [])
        formatted_results.append({'title': title, 'highlighted_snippet': '...'.join(highlight)})
    return formatted_results

if __name__ == '__main__':
    app.run(debug=True)
