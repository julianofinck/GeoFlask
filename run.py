from app import create_app
from app import Config
from app.init_db import bootstart
from dotenv import load_dotenv


load_dotenv()

app = create_app(Config)

if __name__ == '__main__':
    bootstart()
    app.run(host='0.0.0.0', port=5000)
    # Access debug through "localhost:5000"

# curl -X POST -F "shapefile=@tests/shp.zip" http://127.0.0.1:5000/upload
