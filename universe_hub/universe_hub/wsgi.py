import os
import sys
from django.core.wsgi import get_wsgi_application

# Agrega el directorio raíz al path de Python para que encuentre 'universe_hub'
# Esto asume que wsgi.py está dentro de la carpeta 'universe_hub'
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'universe_hub.settings')

application = get_wsgi_application()

# Vercel necesita que la variable se llame 'app' en algunos casos de enrutamiento
app = application
