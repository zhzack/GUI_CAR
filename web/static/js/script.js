let currentAngle = 0;
const ctx = document.getElementById('myArcChart').getContext('2d');

// 创建 Doughnut 图表，外环绘制圆环，内部绘制动态圆弧
const myArcChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Arc', 'Remaining'],
        datasets: [{
            label: 'Progress',
            data: [0, 360], // 初始为 0 的角度
            backgroundColor: ['#76C7C0', '#E0E0E0'], // 圆弧颜色和剩余颜色
            borderWidth: 0,
            borderRadius: 35, // 设置圆弧的圆角大小
        }]
    },
    options: {
        responsive: true,
        cutout: '70%', // 设置圆环的内圆比例
        rotation: 0, // 圆环起始点旋转至顶部
        circumference: 360, // 设置圆环完整度
        plugins: {
            legend: {
                display: true, // 隐藏图例
            },
            tooltip: {
                enabled: true, // 隐藏工具提示
            }
        }
    }
});

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
    myArcChart.data.datasets[0].data = [40, 330];
    myArcChart.options.rotation=currentAngle-20
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
