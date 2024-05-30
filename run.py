from app import create_app
from app import Config
import app.init_db


app = create_app(Config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # Access debug through "localhost:5000"
