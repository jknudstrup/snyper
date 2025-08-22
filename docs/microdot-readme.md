# Microdot Library Reference

## Overview

Microdot is a minimal HTTP web framework for MicroPython and standard Python, designed for embedded systems and resource-constrained environments. It provides Flask-like APIs with async support and minimal memory footprint.

## Core Classes

### `Microdot` - Main Application Class

The primary application class for creating HTTP servers.

```python
from microdot import Microdot
app = Microdot()
```

#### Key Methods

**Route Registration:**
- `@app.route(url_pattern, methods=None)` - General route decorator
- `@app.get(url_pattern)` - GET request handler
- `@app.post(url_pattern)` - POST request handler  
- `@app.put(url_pattern)` - PUT request handler
- `@app.patch(url_pattern)` - PATCH request handler
- `@app.delete(url_pattern)` - DELETE request handler

**Request Lifecycle Hooks:**
- `@app.before_request(f)` - Run function before each request
- `@app.after_request(f)` - Run function after each request
- `@app.after_error_request(f)` - Run function after error responses
- `@app.errorhandler(status_code_or_exception_class)` - Handle specific errors

**Server Management:**
- `app.run(host='0.0.0.0', port=5000, debug=False, ssl=None)` - Start server (blocking)
- `await app.start_server(host='0.0.0.0', port=5000, debug=False, ssl=None)` - Start async server
- `app.shutdown()` - Request graceful server shutdown

**Sub-applications:**
- `app.mount(subapp, url_prefix='', local=False)` - Mount sub-application

**Error Handling:**
- `app.abort(status_code, reason=None)` - Abort request with HTTP error

### `Request` - HTTP Request Object

Represents an incoming HTTP request with all associated data.

#### Key Properties

**Request Info:**
- `request.method` - HTTP method (GET, POST, etc.)
- `request.url` - Full request URL
- `request.path` - URL path portion
- `request.query_string` - Query string portion
- `request.client_addr` - Client address tuple (host, port)
- `request.headers` - Request headers as `NoCaseDict`
- `request.cookies` - Parsed cookies as dictionary

**Request Body:**
- `request.body` - Raw body as bytes
- `request.stream` - Body as async stream
- `request.json` - Parsed JSON body (if Content-Type is application/json)
- `request.form` - Parsed form data as `MultiDict` (URL-encoded forms)
- `request.files` - Uploaded files dictionary (requires multipart decorator)

**URL Parameters:**
- `request.args` - Parsed query string parameters as `MultiDict`
- `request.url_args` - Dynamic URL path parameters

**Request Context:**
- `request.app` - Reference to Microdot application
- `request.g` - General purpose storage container
- `request.content_length` - Parsed Content-Length header
- `request.content_type` - Parsed Content-Type header

#### Configuration Class Variables

- `Request.max_content_length = 16 * 1024` - Maximum payload size (16KB)
- `Request.max_body_length = 16 * 1024` - Maximum body size stored in memory (16KB)
- `Request.max_readline = 2 * 1024` - Maximum line length (2KB)

#### Request Hooks
- `@request.after_request(f)` - Register request-specific after request handler

### `Response` - HTTP Response Object

Represents an HTTP response to send back to the client.

```python
from microdot import Response

# Simple response
return Response('Hello World')

# JSON response (auto-detected)
return Response({'status': 'ok'})

# Custom status and headers
return Response('Not Found', status_code=404, headers={'X-Custom': 'value'})
```

#### Constructor Parameters
- `body` - Response body (string, bytes, dict/list for JSON, file-like, or async generator)
- `status_code=200` - HTTP status code
- `headers=None` - Response headers dictionary
- `reason=None` - Custom reason phrase

#### Key Methods

**Cookie Management:**
- `response.set_cookie(cookie, value, path=None, domain=None, expires=None, max_age=None, secure=False, http_only=False, partitioned=False)`
- `response.delete_cookie(cookie, **kwargs)`

**Class Methods:**
- `Response.redirect(location, status_code=302)` - Create redirect response
- `Response.send_file(filename, status_code=200, content_type=None, stream=None, max_age=None, compressed=False, file_extension='')` - Send file contents

#### Configuration Class Variables
- `Response.default_content_type = 'text/plain'` - Default content type
- `Response.default_send_file_max_age = None` - Default cache control for files
- `Response.send_file_buffer_size = 1024` - File streaming buffer size
- `Response.types_map` - File extension to MIME type mapping

#### Built-in MIME Types
- `.css` → `text/css`
- `.gif` → `image/gif`
- `.html` → `text/html`
- `.jpg` → `image/jpeg`
- `.js` → `application/javascript`
- `.json` → `application/json`
- `.png` → `image/png`
- `.txt` → `text/plain`
- `.svg` → `image/svg+xml`

## Utility Classes

### `MultiDict` - Multiple Values Dictionary

Dictionary that can hold multiple values for the same key (used for query strings and form data).

```python
d = MultiDict()
d['sort'] = 'name'
d['sort'] = 'email'
print(d['sort'])  # 'name' (first value)
print(d.getlist('sort'))  # ['name', 'email'] (all values)
```

**Methods:**
- `get(key, default=None, type=None)` - Get first value with optional type conversion
- `getlist(key, type=None)` - Get all values as list with optional type conversion

### `NoCaseDict` - Case-Insensitive Dictionary

Dictionary with case-insensitive key access (used for HTTP headers).

```python
d = NoCaseDict()
d['Content-Type'] = 'text/html'
print(d['content-type'])  # 'text/html'
print(d['CONTENT-TYPE'])  # 'text/html'
```

### `URLPattern` - URL Route Pattern Matching

Handles dynamic URL pattern matching with type conversion.

**Supported URL Segments:**
- `<name>` or `<string:name>` - String segment (default)
- `<int:id>` - Integer segment with automatic conversion
- `<path:filepath>` - Path segment (includes slashes)
- `<re:pattern:name>` - Custom regex pattern

**Custom Types:**
```python
URLPattern.register_type('uuid', r'[a-f0-9-]{36}', lambda x: UUID(x))
```

### `HTTPException` - HTTP Error Exception

Exception class for HTTP errors that can be caught by error handlers.

```python
from microdot import HTTPException
raise HTTPException(404, "Resource not found")
```

### `AsyncBytesIO` - Async Bytes Stream Wrapper

Provides async interface for bytes streams.

## Utility Functions

### URL Encoding/Decoding
- `urlencode(s)` - URL encode string
- `urldecode(s)` - URL decode string

### Convenience Functions
- `abort(status_code, reason=None)` - Abort request (alias for `Microdot.abort`)
- `redirect(location, status_code=302)` - Create redirect response (alias for `Response.redirect`)
- `send_file(filename, ...)` - Send file response (alias for `Response.send_file`)

## Usage Examples

### Basic Application
```python
from microdot import Microdot

app = Microdot()

@app.route('/')
def index(request):
    return 'Hello, World!'

@app.route('/users/<int:id>')
def get_user(request, id):
    return {'user_id': id, 'name': f'User {id}'}

app.run(debug=True)
```

### Async Application
```python
import asyncio
from microdot import Microdot

app = Microdot()

@app.route('/')
async def index(request):
    await asyncio.sleep(0.1)  # Simulate async work
    return 'Hello, Async World!'

async def main():
    await app.start_server(debug=True)

asyncio.run(main())
```

### Request Handling
```python
@app.route('/api/data', methods=['POST'])
def handle_data(request):
    # Access JSON data
    data = request.json
    
    # Access form data
    name = request.form.get('name')
    
    # Access query parameters
    page = request.args.get('page', default=1, type=int)
    
    # Access headers
    auth = request.headers.get('Authorization')
    
    return {'received': data}
```

### Error Handling
```python
@app.errorhandler(404)
def not_found(request):
    return 'Page not found', 404

@app.errorhandler(RuntimeError)
def handle_runtime_error(request, exception):
    return f'Runtime error: {exception}', 500
```

### File Responses
```python
@app.route('/download/<filename>')
def download_file(request, filename):
    return Response.send_file(f'/files/{filename}')
```

## MicroPython Compatibility

Microdot is designed to work with MicroPython's limited stdlib:

- **No threading** - Uses async/await for concurrency
- **Memory efficient** - Minimal allocations and streaming responses
- **Limited imports** - Graceful fallbacks for missing modules
- **Socket handling** - Properly handles MicroPython socket limitations

## Configuration Tips

### Memory Limits
```python
# Adjust limits for your hardware
Request.max_content_length = 8 * 1024    # 8KB max payload
Request.max_body_length = 4 * 1024       # 4KB max body in memory
Request.max_readline = 1 * 1024          # 1KB max line length
```

### File Serving
```python
# Configure file serving
Response.send_file_buffer_size = 512     # Smaller buffer for low memory
Response.default_send_file_max_age = 3600  # 1 hour cache
```

This reference covers the core functionality of Microdot as implemented in the SNYPER project. The library provides a clean, Flask-inspired API that works well in MicroPython's constrained environment.