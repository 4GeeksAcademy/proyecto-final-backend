import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models.User.user_model import db, Usuario
from models import Ingrediente, Receta, RecetaFavorita, receta_ingredientes
from routes import user_bp, recipe_bp, ingredient_bp, favorite_bp, ai_bp, password_bp
from flask_jwt_extended import JWTManager
from datetime import timedelta

from openai import OpenAI
import openai

from flask_mail import Mail



#  Configuración de la Aplicación Flask
app = Flask(__name__)
app.url_map.strict_slashes = False

#  Configuración de Flask-Mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"), 
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
)
mail = Mail(app)


#  Configuración de la Base de Datos
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#  Configuración de JWT
jwt_key = os.getenv("JWT_KEY")
app.config["SECRET_KEY"] = jwt_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
jwt = JWTManager(app)

#  Registrar Blueprints
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(recipe_bp, url_prefix='/recipe')
app.register_blueprint(ingredient_bp, url_prefix='/ingredient')
app.register_blueprint(favorite_bp, url_prefix='/recipe_favorite')
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(password_bp, url_prefix='/password')

#  Inicializar Extensiones
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
setup_admin(app)

#  Manejador de errores
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

#  Generar sitemap con todos los endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#  Punto de entrada principal
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)

