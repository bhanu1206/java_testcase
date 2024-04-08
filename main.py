from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)

# Set up JWT
app.config['JWT_SECRET_KEY'] = '315e5c9cff9b72eeacf7defb49f70942025e1e88afb8582a67867ba86670d7c3'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
jwt = JWTManager(app)

# Mock database of users
users = {
    'admin': 'admin@123'
}


# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if username and password are provided
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # Check if username exists and password is correct
    if username in users and users[username] == password:
        # Generate access token
        access_token = create_access_token(identity=username)
        # Customize the response JSON format
        response = {
            "userDetails": {
                "username": username,
                "authorities": [{"authority": "ROLE_ADMIN"}]
            },
            "token": access_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


# Protected route that requires authentication
@app.route('/protected', methods=['GET'])
# @jwt_required()
def protected():
    # Get the identity of the current user from the access token
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/test', methods=['GET'])
# @jwt_required()
def test():
    return "test"


if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from werkzeug.security import generate_password_hash, check_password_hash
#
# app = Flask(__name__)
#
# # Flask app configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost:3306/TestCases'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_SECRET_KEY'] = '315e5c9cff9b72eeacf7defb49f70942025e1e88afb8582a67867ba86670d7c3'
#
# # Initialize extensions
# db = SQLAlchemy(app)
# jwt = JWTManager(app)
#
#
# # User model
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#
#
# # Login route
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
#
#     # Check if username and password are provided
#     if not username or not password:
#         return jsonify({'message': 'Missing username or password'}), 400
#
#     # Query the database for the user
#     user = User.query.filter_by(username=username).first()
#
#     # Check if the user exists and password is correct
#     if user and check_password_hash(user.password, password):
#         # Generate access token
#         access_token = create_access_token(identity=username)
#         # Customize the response JSON format
#         response = {
#             "userDetails": {
#                 "username": username,
#                 "authorities": [{"authority": "ROLE_ADMIN"}]
#             },
#             "token": access_token
#         }
#         return jsonify(response), 200
#     else:
#         return jsonify({'message': 'Invalid username or password'}), 401
#
#
# # Protected route that requires authentication
# @app.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     # Get the identity of the current user from the access token
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
