from GBGenAI import app
from dotenv import load_dotenv
import os

load_dotenv()

HOSTNAME = os.getenv('HOSTNAME', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
DEBUG = bool(os.getenv('DEBUG', False))

if __name__ == '__main__':
    app.run(host=HOSTNAME, port=PORT, debug=DEBUG)