#!/bin/bash

# Setup script for nginx reverse proxy

echo "Setting up nginx reverse proxy for TradingView Webhooks Bot..."

# Create logs directory
mkdir -p logs/nginx

# Set proper permissions
chmod 755 logs/nginx

# Check if nginx is installed (for local development)
if command -v nginx &> /dev/null; then
    echo "Nginx is installed locally."
    echo "To test the configuration: nginx -t"
    echo "To start nginx: sudo nginx"
    echo "To reload nginx: sudo nginx -s reload"
else
    echo "Nginx not found locally. Using Docker Compose with nginx container."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the application with nginx reverse proxy:"
echo "  docker-compose -f docker-compose.nginx.yml up -d"
echo ""
echo "To stop the application:"
echo "  docker-compose -f docker-compose.nginx.yml down"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.nginx.yml logs -f"
echo ""
echo "The application will be available at:"
echo "  http://localhost (port 80)"
echo ""
echo "Note: The Flask app is now only accessible through nginx on port 80."
echo "Direct access to port 5000 is blocked for security."