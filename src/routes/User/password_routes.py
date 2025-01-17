from flask import Blueprint, request, jsonify, current_app
from models.User.user_model import Usuario, db
from flask_mail import Message
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_mail import Mail

password_bp = Blueprint('password_bp', __name__)

bcrypt = Bcrypt()
mail = Mail()


# Ruta para solicitar el restablecimiento de contraseña
@password_bp.route('/request-reset-password', methods=["POST"])
def request_reset_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "El campo 'email' es obligatorio"}), 400

    # Verificar si el usuario existe
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No existe un usuario con ese correo."}), 404

    try:
        # Generar token con validez de 5 minutos
        token = create_access_token(identity=email, expires_delta=timedelta(minutes=5))

        # Enlace para restablecer la contraseña
        reset_link = f"https://jubilant-waddle-jj4q4x5p6jpv2w6-5173.app.github.dev/reset-password/{token}"

        # Enviar correo
        msg = Message(
            'Restablece tu contraseña',
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[email]
        )
        msg.html = f"""
        <p>Hola,</p>
        <p>Para restablecer tu contraseña, haz clic en el siguiente enlace:</p>
        <a href="{reset_link}">Restablecer contraseña</a>
        <p>Este enlace expirará en 5 minutos.</p>
        """
        mail.send(msg)

        return jsonify({"message": "Se ha enviado un correo para recuperar tu contraseña"}), 200

    except Exception as e:
        print(f"Error al enviar el correo de recuperación: {e}")
        return jsonify({"error": "Error al enviar el correo de recuperación"}), 500


# Ruta para restablecer la contraseña usando el token
@password_bp.route('/reset-password', methods=["POST"])
@jwt_required()
def reset_password():
    user_data = request.get_json()
    email = get_jwt_identity()  #  Obtenemos el email del token

    if user_data['password'] == user_data['confirm_password']:
        # Buscar al usuario en la base de datos
        user = Usuario.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": "Usuario no encontrado."}), 404

        # Hashear la nueva contraseña
        hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        
        # Actualizar la contraseña en la base de datos
        user.password = hashed_password
        db.session.commit()

        return jsonify({"message": "Contraseña actualizada correctamente."}), 200

    return jsonify({"error": "Las contraseñas no coinciden."}), 400
  