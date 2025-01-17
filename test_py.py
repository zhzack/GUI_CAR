import sys
import math
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtSvg import QGraphicsSvgItem


class AirTagFinder(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initial setup
        self.target_x, self.target_y = random.randint(-100, 100), random.randint(-100, 100)
        self.current_x, self.current_y = 0, 0  # Initial position (0, 0)
        self.timer_active = False

        # UI setup
        self.setWindowTitle("Find My AirTag")
        self.setGeometry(100, 100, 400, 600)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Distance Label
        self.distance_label = QLabel(f"Distance: {self.calculate_distance():.1f} m", self)
        self.distance_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.distance_label)

        # Arrow SVG Widget (Graphics View and Scene)
        self.graphics_view = QGraphicsView(self)
        self.graphics_view.setFixedSize(300, 300)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)

        # Load arrow SVG
        self.arrow_item = QGraphicsSvgItem("img/arrow/jiantou_3d.svg")
        self.arrow_item.setTransformOriginPoint(self.arrow_item.boundingRect().center())  # Set rotation center
        self.graphics_scene.addItem(self.arrow_item)
        self.layout.addWidget(self.graphics_view)

        # Play Sound Button
        self.play_sound_button = QPushButton("Play Sound", self)
        self.play_sound_button.clicked.connect(self.play_sound)
        self.layout.addWidget(self.play_sound_button)

        # Simulate Movement Button
        self.simulate_movement_button = QPushButton("Simulate Movement", self)
        self.simulate_movement_button.clicked.connect(self.toggle_movement)
        self.layout.addWidget(self.simulate_movement_button)

        self.setCentralWidget(self.central_widget)

        # Timer for updating the interface
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)

    def play_sound(self):
        print("Playing sound on AirTag!")  # Replace with sound playing logic if needed

    def toggle_movement(self):
        if self.timer_active:
            # Stop the timer
            self.timer.stop()
            self.timer_active = False
            self.simulate_movement_button.setText("Simulate Movement")
        else:
            # Start the timer and generate a new random target
            self.target_x, self.target_y = random.randint(-100, 100), random.randint(-100, 100)
            self.timer.start(100)
            self.timer_active = True
            self.simulate_movement_button.setText("Stop Simulation")

    def calculate_distance(self):
        """Calculate the distance between current and target points."""
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        return math.sqrt(dx**2 + dy**2)

    def calculate_angle(self):
        """Calculate the angle (in degrees) to the target point."""
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        angle = math.degrees(math.atan2(-dy, dx))  # Negative dy to match screen coordinates
        return angle

    def update_ui(self):
        # Simulate movement toward the target
        step_size = 5  # Movement step
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        distance = self.calculate_distance()

        if distance < step_size:
            self.current_x, self.current_y = self.target_x, self.target_y
            self.timer.stop()
            self.timer_active = False
            self.simulate_movement_button.setText("Simulate Movement")
        else:
            angle = math.atan2(dy, dx)
            self.current_x += step_size * math.cos(angle)
            self.current_y += step_size * math.sin(angle)

        # Update UI
        self.distance_label.setText(f"Distance: {self.calculate_distance():.1f} m")
        self.update_arrow_widget()

    def update_arrow_widget(self):
        """Rotate the arrow SVG to point in the correct direction."""
        angle = self.calculate_angle()
        self.arrow_item.setRotation(angle)  # Rotate the arrow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    finder = AirTagFinder()
    finder.show()
    sys.exit(app.exec_())
