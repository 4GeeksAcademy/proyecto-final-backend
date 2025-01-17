from flask import Blueprint, jsonify, request
from models import db,Usuario
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

user_bp = Blueprint('user_bp', __name__)
bcrypt = Bcrypt()

# Obtener todos los usuarios
@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    users = Usuario.query.all()
    users = [user.serialize() for user in users]
    return jsonify({"users":users}), 200

# Crear un nuevo usuario
@user_bp.route('/create', methods=['POST'])
def create_user():
    user_data = request.get_json()
    new_user = Usuario(**user_data)
    new_user.password = bcrypt.generate_password_hash(new_user.password).decode('utf-8')
    db.session.add(new_user)
    db.session.commit()
    access_token = create_access_token(identity=str(new_user.id))

    # Aquí devuelvo el token y la info del usuario
    return jsonify({
        "message": "Usuario creado",
        "access_token": access_token,
        "user": {
            "id": new_user.id,
            "nombre": new_user.nombre,
            "apellidos": new_user.apellidos,
            "nombre_usuario": new_user.nombre_usuario,
            "email": new_user.email
        }
    }), 201

@user_bp.route('/login', methods=['POST'])
def login():
    user_data = request.get_json()
    user = Usuario.query.filter_by(email=user_data["email"]).first()
    if user and bcrypt.check_password_hash(user.password, user_data["password"]):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "msg": "Login correcto",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "apellidos": user.apellidos,
                "nombre_usuario": user.nombre_usuario,
                "email": user.email
            }
        })
    else:
        return jsonify({"Error": "El email no está registrado o los datos son incorrectos"}), 401
    
# Ruta para obtener el perfil del usuario autenticado
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = Usuario.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": user.id,
        "nombre": user.nombre,
        "apellidos": user.apellidos,
        "nombre_usuario": user.nombre_usuario,
        "email": user.email
    }), 200
    


@user_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = Usuario.query.get(id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"user":user.serialize()}), 200


@user_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = Usuario.query.get(id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"}), 200