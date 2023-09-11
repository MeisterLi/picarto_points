from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, websocket_path='/socket.io', cors_allowed_origins="*")
key = ""
data = {}

app.config['PREFERRED_URL_SCHEME'] = 'https'  # Use 'http' for non-SSL

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/new_data', methods=['POST'])
def new_data():
    print("Updating!")
    password = request.json.get('password')
    if password != key:
        print("Password does not match!")
        return jsonify(success=False, message="Invalid password")

    try:
        data_list = request.json.get('data', [])
        print(f"list is {str(data_list)}")

        for item in data_list:
            name = item.get('name')
            points = int(item.get('points'))

            data[name] = points
            print(f"adding {name} with {points}")

        # Broadcast the updated data to all connected clients
        socketio.emit('update', data)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/update', methods=['POST'])
def update():
    print("Updating!")
    socketio.emit('update', data)
    return jsonify(success=True)

@app.route('/clear', methods=['POST'])
def clear():
    password = request.form.get('password')

    if password != key:
        return jsonify(success=False, message="Invalid password")

    data.clear()  # Clear the data dictionary

    # Broadcast the cleared data to all connected clients
    socketio.emit('update', data, broadcast=True)

    return jsonify(success=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5432)
