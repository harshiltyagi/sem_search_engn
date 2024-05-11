from transformers import BertTokenizer, BertModel
#from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
import numpy as np

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


# Replace these with your Elasticsearch server details
es = Elasticsearch(['https://elastic:ML4SEc-8wHtqH2W067cC@localhost:9200'], verify_certs=False)

# Sample documents
documents = [
    "This is the first document",
    "This document is the second document",
    "And this is the third one",
    "Is this the first document?",
]

# Embedding function using BERT
def get_bert_embeddings(text):
    inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding=True)
    outputs = model(**inputs)
    embeddings = np.mean(outputs.last_hidden_state.detach().numpy(), axis=1)
    return embeddings


# Indexing documents in Elasticsearch
for idx, doc in enumerate(documents):
    doc_embedding = get_bert_embeddings(doc)
    doc_vector = doc_embedding.flatten().tolist()
    es.index(index='documents_index', id=idx, body={'text': doc, 'embedding': doc_vector})

# Query
query = "This is the second document"

# Get embedding for query
query_embedding = get_bert_embeddings(query).flatten()

# Search in Elasticsearch
search_body = {
    "query": {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_embedding.tolist()}
            }
        }
    }
}

search_results = es.search(index='documents_index', body=search_body)['hits']['hits']

# Retrieve top similar documents
top_similar_docs = sorted(search_results, key=lambda x: x['_score'], reverse=True)
for doc in top_similar_docs:
    print(f"Score: {doc['_score']:.4f} - Document: {doc['_source']['text']}")
