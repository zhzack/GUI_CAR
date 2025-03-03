import requests
import math
x = 10
y = 100
angle = 40
url = "http://localhost:5000/set_data"
par = {"angle": angle,
       "distance": math.sqrt(x**2 + y**2)}
r = requests.get(url, params=par)
print(r.text)  # 打印返回结果 文本
