import tkinter as tk
import math
import sys

class VectorDisplay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("矢量方向显示器")
        self.config(bg="#f0f0f0")

        self.canvas_size = 400
        self.center = self.canvas_size // 2
        self.max_radius = 180

        # 创建画布
        self.canvas = tk.Canvas(self, width=self.canvas_size, height=self.canvas_size, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10, padx=20)

        # 绘制参考系
        self._draw_reference()

        # 初始化箭头
        self.arrow = None

        # 信息显示区域
        info_frame = tk.Frame(self, bg="#f0f0f0")
        info_frame.pack(pady=5)

        self.coord_label = tk.Label(info_frame, text="坐标: (0.00, 0.00)", font=("微软雅黑", 12), bg="#e0e0e0", width=20)
        self.coord_label.pack(side=tk.LEFT, padx=5)

        self.distance_label = tk.Label(info_frame, text="距离: 0.00", font=("微软雅黑", 12), bg="#e0e0e0", width=15)
        self.distance_label.pack(side=tk.LEFT, padx=5)

        # 启动线程，等待接收坐标输入
        self.after(100, self.listen_for_coordinates)

    def _draw_reference(self):
        """绘制参考坐标系"""
        self.canvas.create_oval(self.center-3, self.center-3, self.center+3, self.center+3, fill="red")
        self.canvas.create_line(self.center, 20, self.center, self.canvas_size-20, fill="#e0e0e0", dash=(4, 4))
        self.canvas.create_line(20, self.center, self.canvas_size-20, self.center, fill="#e0e0e0", dash=(4, 4))

    def set_coordinate(self, x, y):
        """设置目标坐标并更新显示"""
        if self.arrow:
            self.canvas.delete(self.arrow)

        distance = math.hypot(x, y)
        if distance > self.max_radius and distance != 0:
            scale = self.max_radius / distance
            dx, dy = x*scale, y*scale
        else:
            dx, dy = x, y

        end_x = self.center + dx
        end_y = self.center - dy  # 反转Y轴方向

        self.arrow = self.canvas.create_line(self.center, self.center, end_x, end_y, arrow=tk.LAST, fill="#2196F3", width=3, arrowshape=(12, 15, 6))

        self.coord_label.config(text=f"坐标: ({x:.2f}, {y:.2f})")
        self.distance_label.config(text=f"距离: {distance:.2f}")

    def listen_for_coordinates(self):
        """从标准输入接收坐标"""
        if sys.stdin:
            coords = sys.stdin.readline().strip()
            if coords:
                x, y = map(int, coords.split())
                self.set_coordinate(x, y)

if __name__ == "__main__":
    app = VectorDisplay()
    app.mainloop()
