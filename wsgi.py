import sys
import os

# Garante que o diretório raiz do projeto está no PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
