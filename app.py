from flask import Flask, request, jsonify, render_template
from datetime import datetime
import elasticsearch
from elasticsearch import Elasticsearch
import logging
import urllib3
from dotenv import load_dotenv
import os

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('imago_media_service')

ES_HOST = os.getenv("ES_HOST")
ES_PORT = os.getenv("ES_PORT")
ES_USER = os.getenv("ES_USER")
ES_PASSWORD = os.getenv("ES_PASSWORD")
ES_INDEX = os.getenv("ES_INDEX")

BASE_URL = "https://www.imago-images.de"

def create_es_client():
    """Create and return an Elasticsearch client."""
    try:
        client = Elasticsearch(
            [f"{ES_HOST}:{ES_PORT}"],
            basic_auth=(ES_USER, ES_PASSWORD),
            verify_certs=False
        )
        logger.info("Successfully connected to Elasticsearch")
        return client
    except elasticsearch.exceptions.AuthenticationException:
        logger.error("Authentication failed")
        raise
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
        raise

def process_media_item(item):
    """
    Process and normalize a media item from Elasticsearch.
    
    Args:
        item: Raw media item from Elasticsearch
        
    Returns:
        Normalized media item
    """
    media_id = str(item.get("bildnummer", ""))
    db = item.get("db", "st")
    
    media_id = media_id.zfill(10)
    
    thumbnail_url = f"{BASE_URL}/bild/{db}/{media_id}/s.jpg"

    date_str = item.get("datum", "")

    if date_str:
        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        formatted_date = date_obj.strftime("%Y-%m-%d")
    else:
        formatted_date = ""
    
    processed_item = {
        "id": media_id,
        "db": db,
        "title": item.get("suchtext", "Untitled"),
        "description": item.get("description", ""),
        "date": item.get("datum", ""),
        "thumbnail_url": thumbnail_url
    }
    
    return processed_item

def search_media(client, query=None, filters=None, size=20, page=1):
    """
    Search for media in Elasticsearch.
    
    Args:
        client: Elasticsearch client
        query: Search query string
        filters: Dict of field-value pairs for filtering
        size: Number of results per page
        page: Page number
        
    Returns:
        Dict containing search results and metadata
    """
    try:
        from_val = (page - 1) * size
        
        search_body = {
            "from": from_val,
            "size": size,
            "query": {
                "bool": {
                    "must": []
                }
            }
        }
        
        if query:
            search_body["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["suchtext"]
                }
            })

        if filters:
            for field, value in filters.items():
                search_body["query"]["bool"]["must"].append({
                    "match": {field: value}
                })

        if not query and not filters:
            search_body["query"] = {"match_all": {}}
        
        response = client.search(index=ES_INDEX, body=search_body)
        
        results = []
        for hit in response["hits"]["hits"]:
            result = process_media_item(hit["_source"])
            results.append(result)
        
        return {
            "total": response["hits"]["total"]["value"],
            "page": page,
            "size": size,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise

app = Flask(__name__)
es_client = None

@app.before_request
def ensure_es_client():
    global es_client
    if es_client is None:
        es_client = create_es_client()

@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint for searching media."""
    try:
        query = request.args.get('q', '')
        size = int(request.args.get('size', 20))
        page = int(request.args.get('page', 1))
        
        filters = {}
        for key, value in request.args.items():
            if key not in ['q', 'size', 'page']:
                filters[key] = value
        
        results = search_media(es_client, query, filters, size, page)
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"API search error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/search')
def search_page():
    """Render the search results page."""
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    
    try:
        results = search_media(es_client, query, {}, size, page)
        return render_template(
            'search.html', 
            query=query, 
            results=results,
            page=page,
            size=size,
            max=max,
            min=min
        )
    except Exception as e:
        logger.error(f"Search page error: {str(e)}")
        return render_template('error.html', error=str(e))

@app.template_filter('format_iso_date')
def format_iso_date(value, format="%Y-%m-%d"):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime(format)
    except Exception:
        return value

if __name__ == '__main__':
    app.run(debug=True)

