from flask import Flask, render_template, jsonify, request
import random
app = Flask(__name__)

# 默认角度
current_angle = 0
current_distance = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/set_data', methods=['GET'])
def set_data():
    global current_angle
    global current_distance
    current_angle = request.args.get("angle")
    current_distance = request.args.get("distance")
    print(current_angle)
    print(current_distance)
    return ( f"current_angle:{current_angle},current_distance:{current_distance}")


@app.route('/get_angle', methods=['GET'])
def get_angle():
    global current_angle
    global current_distance
    # 生成一个0到360之间的随机角度
    current_angle = random.randint(0, 360)
    current_distance = random.randint(10, 100)  # 随机距离
    return jsonify({'angle': current_angle, 'distance': current_distance})


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
