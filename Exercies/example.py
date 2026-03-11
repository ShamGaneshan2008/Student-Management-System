from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout,  \
    QLineEdit, QPushButton, QComboBox

import sys

class SpeedCalculator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Age Calculator")
        grid = QGridLayout()

        # Create widgets
        distance_label = QLabel("Distance:")
        self.distance_input = QLineEdit()

        time_label = QLabel("Time (hours):")
        self.time_input = QLineEdit()

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['Metric (km)', 'Imperial (miles)'])

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)

        self.output_label = QLabel("")

        # Add widgets to grid
        grid.addWidget(distance_label, 0, 0)
        grid.addWidget(self.distance_input, 0 , 1)
        grid.addWidget(self.unit_combo, 0, 2)
        grid.addWidget(time_label, 1, 0 )
        grid.addWidget(self.time_input, 1, 1)
        grid.addWidget(calculate_button, 2, 1)
        grid.addWidget(self.output_label, 3, 0, 1, 2)

        self.setLayout(grid)

    def calculate(self):
        # Get distance and time from the input boxes
        distance = float(self.distance_input.text())
        time = float(self.time_input.text())

        # Calculate average speed
        speed = distance / time

        # Check what user chose in the combo
        if self.unit_combo.currentText() == "Metric (km)":
            speed = round(speed, 2) # 2 is the decimal point at the end
            unit = 'km/h'
        if self.unit_combo.currentText() == "Imperial (miles)":
            speed = round(speed * 0.621371, 2) # 2 is the decimal point at the end
            unit = 'mph'

        # Display the result
        self.output_label.setText(f"Average Speed: {speed} {unit}")


# This is the code to display the code
app = QApplication(sys.argv)
speed_cal = SpeedCalculator()
speed_cal.show()
sys.exit(app.exec())
