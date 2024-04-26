from flask import Flask

def create_app():
    app = Flask(__name__)  # creating an instance of Flask app , __name__ refers to the current module or package name
    app.config['SECRET_KEY'] = 'WCWT5 Wilmington DE'
    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app

