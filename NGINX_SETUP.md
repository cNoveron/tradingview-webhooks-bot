# Nginx Reverse Proxy Setup

This document explains how to set up nginx as a reverse proxy for the TradingView Webhooks Bot to avoid exposing the Flask application directly on port 80.

## Overview

The setup includes:
- nginx reverse proxy listening on port 80
- Flask application running on port 5000 (internal only)
- Security headers and proper proxy configuration
- Docker Compose setup for easy deployment

## Files Created

1. `nginx.conf` - nginx configuration file
2. `docker-compose.nginx.yml` - Docker Compose with nginx
3. `setup-nginx.sh` - Setup script
4. Updated `src/main.py` - Added proxy support

## Quick Start

1. Run the setup script:
   ```bash
   ./setup-nginx.sh
   ```

2. Start the application with nginx:
   ```bash
   docker-compose -f docker-compose.nginx.yml up -d
   ```

3. Access your application at `http://localhost`

## Configuration Details

### Nginx Configuration (`nginx.conf`)

- **Port**: Listens on port 80
- **Proxy**: Forwards requests to `app:5000` (Docker service)
- **Security Headers**: X-Frame-Options, XSS Protection, etc.
- **Logging**: Separate access and error logs
- **Health Check**: `/health` endpoint for monitoring

### Docker Compose (`docker-compose.nginx.yml`)

- **App Service**: Flask application with restricted port binding
- **Nginx Service**: nginx container with volume mounts
- **Networks**: Internal bridge network for service communication
- **Volumes**: Persistent nginx logs

### Flask Application Updates

The Flask app has been updated to:
- Trust proxy headers using `ProxyFix` middleware
- Handle forwarded headers properly
- Work correctly behind a reverse proxy

## Security Benefits

1. **Port Isolation**: Flask app not directly exposed
2. **Security Headers**: Additional protection headers
3. **Access Control**: Hidden files denied access
4. **Logging**: Separate nginx logs for monitoring

## Monitoring

### View Logs
```bash
# All services
docker-compose -f docker-compose.nginx.yml logs -f

# Nginx only
docker-compose -f docker-compose.nginx.yml logs -f nginx

# App only
docker-compose -f docker-compose.nginx.yml logs -f app
```

### Health Check
```bash
curl http://localhost/health
```

## Troubleshooting

### Common Issues

1. **Port 80 already in use**:
   ```bash
   sudo lsof -i :80
   # Stop the conflicting service
   ```

2. **Permission denied for nginx logs**:
   ```bash
   sudo chown -R $USER:$USER logs/nginx
   ```

3. **App not accessible**:
   ```bash
   # Check if containers are running
   docker-compose -f docker-compose.nginx.yml ps

   # Check nginx configuration
   docker-compose -f docker-compose.nginx.yml exec nginx nginx -t
   ```

### Manual nginx Setup (Local)

If you prefer to run nginx locally instead of in Docker:

1. Install nginx:
   ```bash
   # macOS
   brew install nginx

   # Ubuntu/Debian
   sudo apt-get install nginx
   ```

2. Copy the configuration:
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/tradingview-webhooks
   sudo ln -s /etc/nginx/sites-available/tradingview-webhooks /etc/nginx/sites-enabled/
   ```

3. Test and restart:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Production Considerations

1. **HTTPS**: Add SSL certificate configuration
2. **Rate Limiting**: Configure rate limiting in nginx
3. **Load Balancing**: Add multiple app instances
4. **Monitoring**: Set up proper monitoring and alerting
5. **Backup**: Regular backup of configuration and logs

## Customization

### Change Port
Edit `docker-compose.nginx.yml`:
```yaml
nginx:
  ports:
    - "8080:80"  # Change 80 to your desired port
```

### Add Domain
Edit `nginx.conf`:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

### SSL Configuration
Add SSL configuration to `nginx.conf`:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... rest of configuration
}
```