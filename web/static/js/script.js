let currentAngle = 0;
let currentDistance = 0;
const arcLen = 25;
const ctx = document.getElementById('myArcChart').getContext('2d');


// 创建 Doughnut 图表，外环绘制圆环，内部绘制动态圆弧
const myArcChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Arc', 'Remaining'],
        datasets: [{
            label: 'Progress',
            data: [0, 360], // 初始为 0 的角度
            backgroundColor: ['#76C7C0', '#e51a54'], // 圆弧颜色和剩余颜色
            borderWidth: 10,
            borderRadius: 25, // 设置圆弧的圆角大小

        }]
    },
    options: {
        responsive: true,
        cutout: '70%', // 设置圆环的内圆比例
        rotation: 0, // 圆环起始点旋转至顶部
        circumference: 360, // 设置圆环完整度
        plugins: {
            legend: {
                display: false, // 隐藏图例
            },
            tooltip: {
                enabled: false, // 隐藏工具提示
            }
        }
    }
});

// 更新车辆的位置标注
function updateCarPosition(angle) {
    angle -= arcLen / 2
    let position = '';

    if (angle >= 0 && angle < 90) {
        position = '右前方';
    } else if (angle >= 90 && angle < 180) {
        position = '右后方';
    } else if (angle >= 180 && angle < 270) {
        position = '左后方';
    } else {
        position = '左前方';
    }

    // 更新页面上的方向文字
    document.getElementById('carLocation').textContent = position;
}

// 获取当前角度
function getAngle() {
    fetch('/get_angle')
        .then(response => response.json())
        .then(data => {
            currentAngle = data.angle;
            updateChart();
        });
}

// 更新圆环图的角度
function updateChart() {
    myArcChart.data.datasets[0].data = [arcLen, 360 - arcLen];
    myArcChart.options.rotation = currentAngle - arcLen / 2
    myArcChart.update();
}

// 设置新的角度
function setAngle(angle) {
    fetch('/set_angle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ angle })
    })
        .then(response => response.json())
        .then(data => {
            if (data.angle !== undefined) {
                currentAngle = data.angle;
                updateChart();
            } else {
                alert('Error: ' + data.error);
            }
        });
}

// 初始化加载时获取当前角度
getAngle();

// 向后台请求当前角度，并更新图表
function updateAngleFromServer() {
    fetch('/get_angle')
        .then(response => response.json())  // 解析 JSON 响应
        .then(data => {
            currentAngle = data.angle;  // 获取后台返回的角度
            currentDistance = data.distance;// 获取后台返回的距离
            console.log("距离",currentDistance)
            console.log("角度",currentAngle)
            document.getElementById('centerLabel').textContent = `距离: ${currentDistance}米  `;
            myArcChart.data.datasets[0].data = [arcLen, 360 - arcLen];  // 更新数据
            myArcChart.options.rotation = currentAngle - arcLen;  // 根据角度更新旋转角度
            // 更新方向标注
            updateCarPosition(currentAngle);
            myArcChart.update();  // 更新图表

        })
        .catch(error => console.error('Error fetching angle:', error));  // 错误处理
}

// 每5秒自动请求后台获取角度并更新图表
setInterval(updateAngleFromServer, 200);

// 页面加载时，第一次请求角度
document.addEventListener('DOMContentLoaded', function () {
    updateAngleFromServer();
});
