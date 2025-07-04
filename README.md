# Ollama API Middleware

A FastAPI-based middleware service that adds Bearer token authentication to Ollama, since Ollama itself doesn't support authentication. This service provides a secure way to access Ollama's API with proper authentication and user management.

## Features

- 🔐 **Bearer Token Authentication**: Secure access to Ollama API with standard Bearer tokens
- 👥 **User Management**: Admin interface for managing users and Bearer tokens
- 🎨 **Modern UI**: Beautiful web interface built with TailwindCSS and DaisyUI
- 📊 **Dashboard**: Real-time statistics and monitoring
- 🔄 **Proxy Service**: Seamlessly forwards requests to Ollama API
- 💾 **SQLite Database**: Lightweight data storage for users and Bearer tokens
- 🚀 **FastAPI**: High-performance async web framework

## Quick Start

### Prerequisites

- Python 3.8+
- **Recommended: Python 3.10 or 3.11** (see Troubleshooting below)
- Ollama running locally (default: http://localhost:11434)

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/alive2tinker/apify_ollama.git](https://github.com/alive2tinker/apify_ollama.git)
   cd ollama-api-middleware
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Production mode (clean output, no debug info)
   python run.py
   
   # Development mode (verbose output, auto-reload)
   DEBUG=true python run.py
   ```

4. **Access the application**
   - Web UI: http://localhost:8000 (or next available port)
   - API Documentation: http://localhost:8000/docs
   - Default admin credentials: `admin` / `admin123`

## Usage

### Web Interface

1. **Login**: Use the default admin credentials or create a new user
2. **Create Bearer Tokens**: Navigate to the Bearer Tokens page and create new tokens
3. **Manage Users**: Add or remove users from the Users page
4. **Monitor Usage**: View statistics and recent activity on the dashboard

### API Usage

All API endpoints require a Bearer token in the `Authorization` header:

```bash
# List models
curl -H "Authorization: Bearer your-bearer-token" http://localhost:8000/api/tags

# Generate text
curl -X POST -H "Authorization: Bearer your-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama2", "prompt": "Hello, world!"}' \
  http://localhost:8000/api/generate

# Chat with model
curl -X POST -H "Authorization: Bearer your-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama2", "messages": [{"role": "user", "content": "Hello!"}]}' \
  http://localhost:8000/api/chat
```

### Postman Setup

1. **Create a new request**
2. **Go to the Authorization tab**
3. **Select "Bearer Token" from the Type dropdown**
4. **Enter your Bearer token in the Token field**
5. **Make your API requests** - the token will be automatically included in the Authorization header

### Python Client Example

```python
import requests

BEARER_TOKEN = "your-bearer-token"
BASE_URL = "http://localhost:8000"

headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# List models
response = requests.get(f"{BASE_URL}/api/tags", headers=headers)
models = response.json()

# Generate text
data = {
    "model": "llama2",
    "prompt": "Explain quantum computing in simple terms"
}
response = requests.post(f"{BASE_URL}/api/generate", headers=headers, json=data)
result = response.json()
```

## API Endpoints

### Ollama Proxy Endpoints (require Bearer token)

- `GET /api/tags` - List available models
- `POST /api/generate` - Generate text
- `POST /api/chat` - Chat with model
- `POST /api/pull` - Pull a model
- `POST /api/push` - Push a model
- `POST /api/create` - Create a model
- `DELETE /api/delete` - Delete a model
- `POST /api/show` - Show model information

### Admin Endpoints (require JWT token)

- `POST /admin/token` - Login and get JWT token
- `POST /admin/users` - Create new user
- `GET /admin/api-keys` - List Bearer tokens
- `POST /admin/api-keys` - Create new Bearer token
- `PUT /admin/api-keys/{id}` - Update Bearer token status
- `DELETE /admin/api-keys/{id}` - Delete Bearer token

### Web Interface

- `GET /` - Dashboard
- `GET /login` - Login page
- `GET /api-keys` - Bearer tokens management
- `GET /users` - Users management

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Debug Mode (development vs production)
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/ollama_middleware.db

# JWT Settings
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
```

### Debug Mode

The application supports a `DEBUG` environment variable to control logging and output:

- **`DEBUG=false`** (default): Clean production output, suppressed warnings
- **`DEBUG=true`**: Verbose development output, auto-reload, debug logs

**Usage:**
```bash
# Production mode
python run.py

# Development mode
DEBUG=true python run.py
```

**What changes in debug mode:**
- Shows detailed startup messages
- Enables auto-reload on file changes
- Shows bcrypt warnings and verbose logs
- Displays default admin credentials
- Uses debug log level

### Database

The application uses SQLite by default. The database file is created automatically at `data/ollama_middleware.db`.

## Security Considerations

1. **Change Default Credentials**: Update the default admin password after first login
2. **Secure Secret Key**: Use a strong secret key in production
3. **HTTPS**: Use HTTPS in production environments
4. **Bearer Token Rotation**: Regularly rotate Bearer tokens
5. **Rate Limiting**: Consider implementing rate limiting for production use

## Development

### Project Structure

```
ollama-api-middleware/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── crud.py              # Database operations
│   ├── ollama_proxy.py      # Ollama proxy service
│   ├── api_routes.py        # API endpoints
│   ├── admin_routes.py      # Admin endpoints
│   ├── web_routes.py        # Web interface routes
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── api_keys.html
│       └── users.html
├── data/                    # Database files
├── requirements.txt
└── README.md
```

### Running in Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Python Version Compatibility (pydantic-core build error)

If you see an error like this when installing dependencies:

```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
ERROR: Failed building wheel for pydantic-core
ERROR: Failed to build installable wheels for some pyproject.toml based projects (pydantic-core)
```

This is because **Python 3.13 is not yet fully supported** by Pydantic and FastAPI dependencies. To fix this:

1. **Use Python 3.10 or 3.11** (recommended):
   - Create a new virtual environment:
     ```bash
     python3.11 -m venv .venv
     source .venv/bin/activate
     # or for Python 3.10
     python3.10 -m venv .venv
     source .venv/bin/activate
     ```
   - Reinstall dependencies:
     ```bash
     pip install --upgrade pip
     pip install -r requirements.txt
     ```
2. If you must use Python 3.13, you will need to wait for upstream support from Pydantic and FastAPI, or try using their development versions (not recommended for production).

### Common Issues

1. **Ollama Connection Error**: Ensure Ollama is running on http://localhost:11434
2. **Database Error**: Check file permissions for the data directory
3. **Import Error**: Ensure all dependencies are installed
4. **Port Already in Use**: The application will automatically find the next available port
5. **Bearer Token Not Working**: Ensure you're using the correct format: `Authorization: Bearer your-token`

### Logs

Check the console output for error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository. 
