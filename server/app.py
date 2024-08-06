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

@app.route('/messages', methods = ['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return make_response([message.to_dict() for message in messages], 200)
    elif request.method == 'POST':
        body = request.json.get('body')
        username = request.json.get('username')
        if not body or not username:
            return make_response(jsonify({'error': 'Missing required fields'}), 400)

        message = Message(body=body, username=username)
        db.session.add(message)
        db.session.commit()

        return make_response(message.to_dict(), 201)

@app.route('/messages/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()
    if request.method == 'GET':
        return make_response(message.to_dict(), 200)
    elif request.method == 'PATCH':
        body = request.json.get('body')
        if not body:
            return make_response(jsonify({'error': 'Missing required field'}), 400)

        message.body = body
        db.session.commit()

        return make_response(message.to_dict(), 200)
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        return make_response(jsonify({'message': 'Message deleted'}), 204)

if __name__ == '__main__':
    app.run(port=5555)
