from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# GET /messages - returns all messages ordered by created_at
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_serialized = [message.to_dict() for message in messages]
    return make_response(jsonify(messages_serialized), 200)

# POST /messages - creates a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()  # Get JSON data from the request
    body = data.get('body')
    username = data.get('username')

    if not body or not username:
        return make_response(jsonify({'error': 'Missing body or username'}), 400)

    new_message = Message(body=body, username=username)
    db.session.add(new_message)
    db.session.commit()

    return make_response(jsonify(new_message.to_dict()), 201)


# PATCH /messages/<int:id> - updates the body of a specific message
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # Get the message from the database using the new SQLAlchemy method
    message = db.session.get(Message, id)

    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    # Get the JSON data from the request
    data = request.get_json()
    body = data.get('body')

    if body:
        message.body = body
        db.session.commit()

    return make_response(jsonify(message.to_dict()), 200)

# DELETE /messages/<int:id> - deletes a specific message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)

    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    db.session.delete(message)
    db.session.commit()

    return make_response(jsonify({'message': 'Message successfully deleted'}), 200)

if __name__ == '__main__':
    app.run(port=5555)
