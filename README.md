# AISchool-auth

FastAPI Authentication API with JWT tokens, OAuth2 support, and email verification.

## Features

- JWT-based authentication with RS256 algorithm
- OAuth2 integration (Google, Facebook)
- Email verification system
- Password reset functionality
- Multi-language support (EN, RU, RO)
- Refresh token management
- JWKS endpoint for public key distribution

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd auth
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env` (if available)
   - Configure all required environment variables (see Configuration section)

4. **Run the application**
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the API**
   - API Documentation: http://localhost:8080/docs
   - Alternative docs: http://localhost:8080/redoc

## Configuration

Required environment variables:

- `HOST` - Server host (e.g., `0.0.0.0`)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ORIGINS` - Comma-separated list of CORS origins
- `CSP_HEADER` - Content Security Policy header
- `SECRET_KEY` - Secret key for JWT signing
- `VERIFICATION_SECRET` - Secret for verification codes
- `DATABASE_URL` - Database connection string
- `EMAIL_HOST_USER` - Email account username
- `EMAIL_HOST_PASSWORD` - Email account password
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `FACEBOOK_CLIENT_ID` - Facebook OAuth app ID

See `DEPLOYMENT.md` for detailed configuration instructions.

## Deployment

### Deploy to Render.com

This application is ready to deploy on Render.com. See the detailed deployment guide:

- **Quick Start**: See [RENDER_QUICK_START.md](RENDER_QUICK_START.md)
- **Detailed Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

### Key Points for Deployment

1. **Database**: The application supports both SQLite (local) and PostgreSQL (production)
2. **Environment Variables**: All configuration is done via environment variables
3. **RSA Keys**: Automatically generated on first run and stored in `keys/` directory
4. **Requirements**: Use `requirements.txt` for dependency installation

## Project Structure

```
auth/
├── core/              # Core settings and middleware
├── models/            # Database models
├── routers/           # API route handlers
├── schemas/           # Pydantic schemas
├── templates/         # Email templates
├── utils/             # Utility functions
├── keys/              # RSA keys storage (auto-generated)
├── main.py            # Application entry point
└── requirements.txt   # Python dependencies
```

## API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info
- `POST /auth/verify` - Verify email
- `POST /auth/restore` - Password reset
- `GET /.well-known/jwks.json` - JWKS endpoint
- `POST /refresh` - Refresh access token

See `/docs` endpoint for interactive API documentation.

## License

See [LICENSE](LICENSE) file for details.