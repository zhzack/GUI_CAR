from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# 默认角度
current_angle = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_angle', methods=['GET'])
def get_angle():
    global current_angle
    return jsonify({'angle': current_angle})

@app.route('/set_angle', methods=['POST'])
def set_angle():
    global current_angle
    data = request.get_json()
    angle = data.get('angle')
    if angle is not None and 0 <= angle <= 360:
        current_angle = angle
        return jsonify({'message': 'Angle updated successfully', 'angle': current_angle}), 200
    else:
        return jsonify({'error': 'Invalid angle. Please set an angle between 0 and 360.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
