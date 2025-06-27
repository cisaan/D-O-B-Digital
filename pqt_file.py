import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QWidget, QComboBox, QFileDialog


class DailyOccurrenceForm(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Set window title and apply rounded corners
        self.setWindowTitle('Daily Occurrence Form - Version 0.3')
        self.setStyleSheet("border-radius: 10px;")  # Rounded corners
        self.setGeometry(300, 100, 600, 500)  # Set the window size and position

        # Use Windows 11 System Font - Segoe UI
        self.setFont(QFont("Segoe UI", 10))

        # Create a grid layout
        layout = QGridLayout()

        # Add form labels and inputs
        layout.addWidget(QLabel('Ref Number:'), 0, 0)
        self.ref_number = QLineEdit(self)
        layout.addWidget(self.ref_number, 0, 1)

        layout.addWidget(QLabel('Date (DD/MM/YYYY):'), 1, 0)
        self.date_entry = QLineEdit(self)
        layout.addWidget(self.date_entry, 1, 1)

        layout.addWidget(QLabel('Time (HH:MM:SS):'), 2, 0)
        self.time_entry = QLineEdit(self)
        layout.addWidget(self.time_entry, 2, 1)

        layout.addWidget(QLabel('Reported By:'), 3, 0)
        self.reported_by_entry = QLineEdit(self)
        layout.addWidget(self.reported_by_entry, 3, 1)

        # Move Category section here, after Reported By
        layout.addWidget(QLabel('Category:'), 4, 0)
        self.category_dropdown = QComboBox(self)
        self.category_dropdown.addItems(['Arrest', 'Theft', 'Antisocial Behaviour', 'Other'])
        layout.addWidget(self.category_dropdown, 4, 1)

        # Continue with the rest of the fields
        layout.addWidget(QLabel('Details of Incident:'), 5, 0)
        self.details_of_incident = QTextEdit(self)
        layout.addWidget(self.details_of_incident, 5, 1)

        layout.addWidget(QLabel('Action Taken:'), 6, 0)
        self.action_taken = QTextEdit(self)
        layout.addWidget(self.action_taken, 6, 1)

        layout.addWidget(QLabel('Crime Reference Number:'), 7, 0)
        self.crime_ref_number = QLineEdit(self)
        layout.addWidget(self.crime_ref_number, 7, 1)

        layout.addWidget(QLabel('CCTV Footage Link:'), 8, 0)
        self.cctv_link = QLineEdit(self)
        layout.addWidget(self.cctv_link, 8, 1)

        layout.addWidget(QLabel('Officer Reporting Full Name:'), 9, 0)
        self.officer_name = QLineEdit(self)
        layout.addWidget(self.officer_name, 9, 1)

        # Add buttons for selecting images and submitting
        self.select_images_button = QPushButton('Select Images', self)
        self.select_images_button.clicked.connect(self.select_images)
        self.select_images_button.setStyleSheet(self.button_style())
        layout.addWidget(self.select_images_button, 10, 0)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit_form)
        self.submit_button.setStyleSheet(self.button_style())
        layout.addWidget(self.submit_button, 10, 1)

        # Set layout
        self.setLayout(layout)


        # Set the background color to light grey
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))  # Windows 11 grey background
        self.setPalette(palette)

    def select_images(self):
        # File dialog to select images
        file_dialog = QFileDialog.getOpenFileNames(self, 'Select Images', '', 'Image Files (*.png *.jpg *.jpeg)')
        if file_dialog[0]:
            print(f'Selected images: {file_dialog[0]}')

    def submit_form(self):
        # Here, you'd handle the form submission logic
        print('Form submitted!')

    def button_style(self):
        """ Return button style for rounded, flat design """
        return """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """


# Running the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = DailyOccurrenceForm()
    form.show()
    sys.exit(app.exec_())
