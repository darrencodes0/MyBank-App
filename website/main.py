from flask import Flask
from website.routes import auth
from website.sessionkey import SESSION_KEY

#creates app and blueprint for routes
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SESSION_KEY
    app.register_blueprint(auth, url_prefix='/')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)