# IMAGO Media Service

This is a Python-based solution for the IMAGO Coding Challenge C3, which retrieves media content from Elasticsearch and presents it to users through a web interface and API.

## Features

- **Elasticsearch Integration**: Connects to the provided Elasticsearch server to fetch media data
- **Data Normalization**: Handles and normalizes unstructured data
- **Search Functionality**: Supports keyword-based search and filtering
- **Responsive UI**: Simple web interface to browse and search media
- **API Endpoints**: RESTful API for integration with other services
- **Testing**: Unit tests for key components

## Project Structure

```
imago-media-service/
├── README.md
├── app.py                # Main application file
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── search.html       # Search results page
│   └── error.html        # Error page
└── .env.exemple
```

## Installation and Setup

1. Clone the repository:

```
git clone imago_test
cd imago_test
```

2. Create a virtual environment and install dependencies:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. copy the .env.exemple and set .env:

```
cp .env.exemple .env
```

3. Run the application:

```
python app.py
```

4. Access the application in your browser at `http://localhost:5000`

## API Usage

The service provides a RESTful API for searching media:

### Search Endpoint

```
GET /api/search
```

Parameters:

- `q`: Search query (optional)
- `page`: Page number (default: 1)
- `size`: Results per page (default: 20)
- Additional parameters will be treated as filters

Example:

```
GET /api/search?q=football&page=2&size=10&db=sport
```

Response format:

```json
{
  "total": 100,
  "page": 2,
  "size": 10,
  "results": [
    {
      "date": "2007-03-30T00:00:00.000Z",
      "db": "sport",
      "id": "0002758691",
      "thumbnail_url": "https://www.imago-images.de/bild/sport/0002758691/s.jpg",
      "title": "AFL Logo - (Icon38616869) American Football Herren AFL 2007, Arena Football League, Arenafootball, Hallenfootball, Halle, Indoor Einzelbild Kansas City American Football Herren AFL 2007, Arena Football League, Arenafootball, Hallenfootball, Halle, Indoor Einzelbild Kansas City EDITORIAL USE ONLY"
    },
    ...
  ]
}
```

## Identified Issues and Solutions

### 1. Data Inconsistency

**Problem**: The Elasticsearch data might have inconsistent or missing fields, which can cause issues when displaying or searching for media.

**Solution**: Our data normalization process handles missing fields by providing sensible defaults, ensuring a consistent structure for front-end display and API responses.

### 2. Security Concerns

**Problem**: The connection to Elasticsearch uses basic authentication over HTTPS but ignores certificate validation, which could be vulnerable to man-in-the-middle attacks.

**Solution**: For a production environment, we would:

- Use proper SSL certificates and enable certificate validation
- Implement API key-based authentication instead of basic auth
- Restrict access to Elasticsearch through a security layer or proxy

### 3. Performance Bottlenecks

**Problem**: As the number of media items grows, search performance might degrade, especially for complex queries.

**Solution**:

- Implement caching for frequently accessed queries
- Use Elasticsearch's aggregations and filters more efficiently
- Optimize indexing and mapping in Elasticsearch
- Add connection pooling for the Elasticsearch client

## Scalability Considerations

To make this solution scalable for large volumes of data:

1. **Horizontal Scaling**: Deploy multiple instances of the application behind a load balancer
2. **Caching Layer**: Add Redis or Memcached to cache frequent queries
3. **Pagination Optimization**: Use search_after parameter instead of from/size for deep pagination
4. **Asynchronous Processing**: Use Celery for background tasks like data processing or export
5. **Connection Pooling**: Optimize Elasticsearch connections using connection pools

## Maintainability Considerations

To keep the solution maintainable as more providers and media items come online:

1. **Modular Architecture**: Separate concerns (data access, business logic, presentation)
2. **Configuration Management**: Externalize configuration for easy updates
3. **Documentation**: Maintain comprehensive API and code documentation
4. **Monitoring**: Implement proper logging and monitoring (covered in the solution)
5. **Testing**: Maintain comprehensive test coverage (unit tests, integration tests)

## Monitoring and Logging

The solution includes basic logging for key operations, such as:

- Elasticsearch connection status
- Search operations
- Error handling

For production, we would enhance this with:

- Integration with a monitoring service (e.g., Prometheus, Grafana)
- Structured logging for better analysis
- Error tracking (e.g., Sentry)
- Performance metrics collection

## Future Enhancements

1. Advanced search features (faceted search, auto-complete)
2. User authentication and personalization
3. Media collection/favorites functionality
4. Advanced filtering options
5. Better error handling and user feedback
6. Responsive design improvements

## Requirements

See `requirements.txt` for the full list of dependencies.

## Testing

It was taking to much time that I dont have in the moment
