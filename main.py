from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, \
    QLineEdit, QPushButton, QComboBox, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QToolBar, QStatusBar, QGridLayout, QLabel, QMessageBox

from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3



class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                course TEXT,
                mobile TEXT
            )
            """)

        connection.commit()
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # calls Parent's __init__ i,e QMainWindow
        self.setWindowTitle("Student Management System")
        self.setMaximumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self) # self is used to connect to the main class
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self) # self is used to connect to the main class
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        edit_action = QAction(QIcon("icons/search.png"),"Search Student", self)
        edit_menu_item.addAction(edit_action)
        edit_action.triggered.connect(self.search)


        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Course", "Mobile_no"])
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table) # specifying the table as the central widget

        # Create Toolbar and add toolbar element
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(edit_action)

        # Create status bar and add status bar element
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self, row, column):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0) # this prevents it from giving the duplicate value
        for row_number, row_data in enumerate(result): # this access each row in the table
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data): # this will access  each item in particular rows
                self.table.setItem(row_number, column_number,  QTableWidgetItem(str(data)))
        connection.close()


    def insert(self):
        dialog = InsertDialog(self)
        dialog.exec()

    def search(self):
        dialog = SearchDialog(self)
        dialog.exec()

    def edit(self):
        dialog = EditDialog(self)
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog(self)
        dialog.exec()

    def about(self):
        dialog = AboutDialog(self)
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("About")
        content = """
        This is the app that is used to manage the student database.
        This is by using the Python and using the DB browser app.
        Feel free to modify the code and re-use the code in the way you want!!  
        Muchas gracias
        """

        self.setText(content)


class DeleteDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure to make the changes")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        layout.addWidget(confirmation, 0 ,0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)
        self.setLayout(layout)

        yes_button.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row index and student id
        index = self.main_window.table.currentRow()
        student_id = self.main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        self.main_window.load_data()
        self.accept()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record has been successfully deleted")
        confirmation_widget.exec()

class EditDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get the student name form the table
        index = self.main_window.table.currentRow()
        student_name = self.main_window.table.item(index, 1).text()

        # Get id from the selected row
        self.student_id = self.main_window.table.item(index, 0).text()

        # ADD STUDENT NAME WIDGET
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # ADD COMBO BOX WIDGET
        course_name = self.main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        course = ["JavaScript", "Python", "C++", "Java", "Assembly Language "]
        self.course_name.addItems(course)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # ADD MOBILE NUMBER
        mobile = self.main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add the button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        self.main_window.load_data()
        self.accept()


class InsertDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # ADD STUDENT NAME WIDGET
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # ADD COMBO BOX WIDGET
        self.course_name = QComboBox()
        course = ["JavaScript", "Python", "C++", "Java", "Assembly Language "]
        self.course_name.addItems(course)
        layout.addWidget(self.course_name)

        # ADD MOBILE NUMBER
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add the button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?,  ?,  ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        self.main_window.load_data()
        self.accept()

        if name == "" or mobile == "":
            QMessageBox.warning(self, "Error", "All fields are required")
            return

class SearchDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)


    def search(self):
        name = self.student_name.text()
        self.main_window.table.clearSelection()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)

        if not rows:
            QMessageBox.information(self, "No Result", "Student not found")
            return

        items = self.main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            self.main_window.table.item(item.row(), item.column()).setSelected(True)

        cursor.close()
        connection.close()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
