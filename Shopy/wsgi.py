import os
from django.core.wsgi import get_wsgi_application
from waitress import serve

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shopy.settings')  # Replace 'Shopy' with your project name

# Get the WSGI application for your project
application = get_wsgi_application()

# Run the application with Waitress
if __name__ == "__main__":
    serve(application, host='0.0.0.0', port=8000)
