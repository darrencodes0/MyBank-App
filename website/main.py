from flask import Flask
from routes import auth
from sessionkey import SESSION_KEY

#creates the app and blueprint for routes
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SESSION_KEY
    app.register_blueprint(auth, url_prefix='/')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)