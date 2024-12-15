from flask import Flask
from apis import api
from mocking import create_mock_datas
from dotenv import load_dotenv
load_dotenv()

from secret import APP_PORT, FLASK_SECRET_KEY, ENV, API_URL, ROOT_PATH_PREFIX
def create_app():
    app = Flask(__name__, static_url_path=f'/{ROOT_PATH_PREFIX}/static')
    print("Running in ENV:", ENV)
    app.config['API_URL'] = API_URL
    api.init_app(app)
    create_mock_datas(app)
    app.secret_key = FLASK_SECRET_KEY
    return app

if __name__ == "__main__":
    app = create_app()
    create_mock_datas(app)
    app.run(port=APP_PORT, debug=True)