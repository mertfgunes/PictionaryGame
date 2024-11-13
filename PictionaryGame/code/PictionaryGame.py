from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QFileDialog,
                             QDockWidget, QPushButton, QVBoxLayout, QLabel,
                             QMessageBox, QComboBox, QStackedWidget, QHBoxLayout, QLineEdit)
from PyQt6.QtGui import QIcon, QPainter, QPen, QAction, QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QTimer
import sys
import csv
import random


class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QPixmap(1000, 700)
        self.image.fill(QColor("#FFFFFF"))
        self.setMinimumSize(1000, 700)
        # Add a subtle border to the canvas
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #CCCCCC;
                border-radius: 8px;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Smooth drawing
        painter.drawPixmap(0, 0, self.image)

    def clear(self):
        self.image.fill(QColor("#FFFFFF"))
        self.update()


class StartScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F2F5;
            }
            QLabel {
                color: #1A1A1A;
            }
        """)

        # Create a container for centered content
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        # Title with enhanced styling
        title = QLabel("Pictionary")
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #2C3E50;
            margin: 20px;
            font-family: 'Arial';
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitle = QLabel("Draw and Guess!")
        subtitle.setStyleSheet("""
            font-size: 24px;
            color: #7F8C8D;
            margin-bottom: 30px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Difficulty Selection with styled combo box
        difficulty_label = QLabel("Select Difficulty:")
        difficulty_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            margin-top: 20px;
        """)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Hard"])
        self.difficulty_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                padding: 8px;
                border: 2px solid #BDC3C7;
                border-radius: 6px;
                background-color: white;
                min-width: 200px;
                margin: 10px;
            }
            QComboBox:hover {
                border-color: #3498DB;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 20px;
            }
        """)

        # Start Button with enhanced styling
        self.start_button = QPushButton("Start Game")
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                padding: 15px 30px;
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 200px;
                margin-top: 30px;
            }
            QPushButton:hover {
                background-color: #27AE60;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)

        # Add widgets to container layout
        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)
        container_layout.addWidget(difficulty_label)
        container_layout.addWidget(self.difficulty_combo)
        container_layout.addWidget(self.start_button)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.setLayout(container_layout)

        # Add container to main layout with margins
        self.layout.addStretch(1)
        self.layout.addWidget(container)
        self.layout.addStretch(1)
        self.layout.setContentsMargins(50, 50, 50, 50)

        self.setLayout(self.layout)


class PictionaryGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F2F5;
            }
        """)

        # Create stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add screens
        self.start_screen = StartScreen()
        self.start_screen.start_button.clicked.connect(self.start_game)

        self.game_widget = QWidget()
        self.game_layout = QVBoxLayout(self.game_widget)
        self.game_widget.setStyleSheet("""
            QWidget {
                background-color: #F0F2F5;
            }
        """)

        # Create drawing canvas
        self.canvas = DrawingCanvas()
        self.game_layout.addWidget(self.canvas)

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.start_screen)
        self.stacked_widget.addWidget(self.game_widget)

        self.wordList = []
        self.currentWord = ""
        self.drawing = False
        self.brushSize = 3
        self.brushColor = QColor("#2C3E50")
        self.lastPoint = QPoint()
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1  # Start with player 1

        # Define score labels in the __init__ method to maintain references
        self.player1_label = QLabel(f"Player 1: {self.player1_score}")
        self.player2_label = QLabel(f"Player 2: {self.player2_score}")
        self.player1_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50;")
        self.player2_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50;")

        # Modern styled word display label
        self.word_label = QLabel()
        self.word_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px;
            }
        """)

        # Create menu bar and dock widget
        self.create_menus()
        self.create_dock_widget()

        self.timer_label = QLabel("Waiting for turn...")
        self.timer_label.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        font-weight: bold;
                        color: #2C3E50;
                        padding: 10px;
                        background-color: #ECF0F1;
                        border-radius: 8px;
                        margin: 10px;
                    }
                """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set window properties
        self.setWindowTitle("Pictionary Game")
        self.setWindowIcon(QIcon("./icons/paint-brush.png"))

    def create_dock_widget(self):
        self.dockInfo = QDockWidget()
        self.dockInfo.setStyleSheet("""
            QDockWidget {
                border: none;
                background-color: white;
            }
            QDockWidget::title {
                background-color: #2C3E50;
                color: white;
                padding: 8px;
                text-align: center;
            }
        """)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockInfo)

        playerInfo = QWidget()
        self.vbdock = QVBoxLayout()
        playerInfo.setLayout(self.vbdock)
        playerInfo.setMinimumWidth(250)
        playerInfo.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #2C3E50;
                font-size: 16px;
                padding: 5px;
            }
        """)

        # Enhanced player info layout
        turn_label = QLabel("Current Turn")
        turn_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")

        scores_label = QLabel("Scores")
        scores_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")

        self.vbdock.addWidget(turn_label)
        self.vbdock.addWidget(self.player1_label)
        self.vbdock.addWidget(self.player2_label)
        self.vbdock.addWidget(self.timer_label)

        self.dockInfo.setWidget(playerInfo)

    def create_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def handle_correct_guess(self):
        self.game_timer.stop()
        self.timer_label.setText("Turn completed!")

        # Update the score based on the current player
        if self.current_player == 1:
            self.player1_score += 1
            self.player1_label.setText(f"Player 1: {self.player1_score}")
        else:
            self.player2_score += 1
            self.player2_label.setText(f"Player 2: {self.player2_score}")

        # Print the current scores for debugging
        print(f"Player 1 score: {self.player1_score}, Player 2 score: {self.player2_score}")

        # Switch turns between players
        self.current_player = 2 if self.current_player == 1 else 1

        # Update word for drawing, display in the word label, and clear the canvas
        self.currentWord = self.getWord()
        self.word_label.setText(f"Draw this word: \n {self.currentWord}")
        self.canvas.clear()

        # Close the guessing window and open it again for the new turn
        self.guessing_window.close()
        self.show_guessing_window()

        self.canvas.clear()


    def create_menus(self):
        mainMenu = self.menuBar()
        mainMenu.setStyleSheet("""
            QMenuBar {
                background-color: #2C3E50;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 5px 10px;
                margin: 0px;
            }
            QMenuBar::item:selected {
                background-color: #34495E;
            }
            QMenu {
                background-color: white;
                border: 1px solid #BDC3C7;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
                color: #2C3E50;
            }
            QMenu::item:selected {
                background-color: #3498DB;
                color: white;
            }
        """)

        # File Menu
        fileMenu = mainMenu.addMenu("File")
        saveAct = QAction('Save Drawing', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.triggered.connect(self.save)

        clearAct = QAction('Clear Canvas', self)
        clearAct.setShortcut('Ctrl+C')
        clearAct.triggered.connect(self.clear)

        fileMenu.addAction(saveAct)
        fileMenu.addAction(clearAct)

        # Tool Menu with enhanced colors
        toolMenu = mainMenu.addMenu("Tools")

        # Brush Size Menu
        brushMenu = toolMenu.addMenu("Brush Size")
        sizes = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        for size in sizes:
            brushAct = QAction(f'Size {size}', self)
            brushAct.triggered.connect(lambda checked, s=size: self.setBrushSize(s))
            brushMenu.addAction(brushAct)

        # Color Menu with modern colors
        colorMenu = toolMenu.addMenu("Colors")
        colors = {
            'Midnight Blue': '#2C3E50',
            'Pomegranate': '#C0392B',
            'Emerald': '#27AE60',
            'Orange': '#D35400',
            'Purple': '#8E44AD',
            'Black': '#000000'
        }

        for color_name, color_code in colors.items():
            colorAct = QAction(color_name, self)
            colorAct.triggered.connect(lambda checked, c=color_code: self.setBrushColor(QColor(c)))
            colorMenu.addAction(colorAct)

    def create_dock_widget(self):
        self.dockInfo = QDockWidget()
        self.dockInfo.setStyleSheet("""
            QDockWidget {
                border: none;
                background-color: white;
            }
            QDockWidget::title {
                background-color: #2C3E50;
                color: white;
                padding: 8px;
                text-align: center;
            }
        """)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockInfo)

        playerInfo = QWidget()
        self.vbdock = QVBoxLayout()
        playerInfo.setLayout(self.vbdock)
        playerInfo.setMinimumWidth(250)
        playerInfo.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #2C3E50;
                font-size: 16px;
                padding: 5px;
            }
        """)

        # Enhanced player info layout
        turn_label = QLabel("Current Turn")
        turn_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #385d8c; margin-top 20px;")

        scores_label = QLabel("Scores")
        scores_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #385d8c; margin-top: 20px;")

        self.player1_label = QLabel(f"Player 1: {self.player1_score}")
        self.player2_label = QLabel(f"Player 2: {self.player2_score}")
        self.player1_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50;")
        self.player2_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50;")

        self.vbdock.addWidget(self.word_label)
        self.vbdock.addWidget(turn_label)
        self.vbdock.addSpacing(20)
        self.vbdock.addWidget(scores_label)
        self.vbdock.addWidget(self.player1_label)
        self.vbdock.addWidget(self.player2_label)
        self.vbdock.addStretch(1)

        self.dockInfo.setWidget(playerInfo)

    def mousePressEvent(self, event):
        if self.stacked_widget.currentIndex() == 1:
            if event.button() == Qt.MouseButton.LeftButton:
                canvas_pos = self.canvas.mapFrom(self, event.pos())
                if self.canvas.rect().contains(canvas_pos):
                    self.drawing = True
                    self.lastPoint = canvas_pos

    def mouseMoveEvent(self, event):
        if self.stacked_widget.currentIndex() == 1 and self.drawing:
            canvas_pos = self.canvas.mapFrom(self, event.pos())
            if self.canvas.rect().contains(canvas_pos):
                painter = QPainter(self.canvas.image)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                pen = QPen(self.brushColor, self.brushSize,
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                           Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.drawLine(self.lastPoint, canvas_pos)
                self.lastPoint = canvas_pos
                self.canvas.update()

    def mouseReleaseEvent(self, event):
        if self.stacked_widget.currentIndex() == 1:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drawing = False

    def setBrushColor(self, color):
        self.brushColor = color

    def setBrushSize(self, size):
        self.brushSize = size

    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Save Drawing", "",
            "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) "
        )
        if filePath:
            self.canvas.image.save(filePath)

    def clear(self):
        self.canvas.clear()

    def start_game(self):
        difficulty = self.start_screen.difficulty_combo.currentText().lower()
        self.getList(difficulty)
        self.currentWord = self.getWord()
        self.timer_label.setText("Starting new turn...")
        self.stacked_widget.setCurrentIndex(1)
        self.show_guessing_window()


    def show_guessing_window(self):
        self.guessing_window = GuessingWindow(self.currentWord)
        self.guessing_window.guess_correct.connect(self.handle_correct_guess)
        self.guessing_window.time_expired.connect(self.handle_time_expired)

        # Create timer for main window
        self.game_timer = QTimer()
        self.time_remaining = 60
        self.game_timer.timeout.connect(self.update_main_timer)
        self.game_timer.start(1000)

        QTimer.singleShot(100, self.guessing_window.show)

    def update_main_timer(self):
        self.time_remaining -= 1
        self.timer_label.setText(f"Time Remaining: {self.time_remaining}s")

        if self.time_remaining <= 10:
            self.timer_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    padding: 10px;
                    background-color: #E74C3C;
                    border-radius: 8px;
                    margin: 10px;
                }
            """)

        if self.time_remaining <= 0:
            self.game_timer.stop()

    def getList(self, mode):
        self.wordList.clear()  # Ensure word list is empty before populating
        file_path = mode + 'mode.txt'

        try:
            with open(file_path, 'r') as file:
                # Read the entire line and split by commas
                line = file.read()
                words = line.split(',')  # Split the string by commas
                for word in words:
                    word = word.strip()  # Remove any extra spaces or newlines
                    if word:  # Only add non-empty words
                        self.wordList.append(word)
        except FileNotFoundError:
            print(f"Error: {file_path} not found")

    def getWord(self):
        return random.choice(self.wordList)  # Select a random word from the list

    def handle_time_expired(self):
        self.game_timer.stop()
        self.timer_label.setText("Time's up!")
        # Switch turns between players
        self.current_player = 2 if self.current_player == 1 else 1

        # Update word for drawing, display in the word label, and clear the canvas
        self.currentWord = self.getWord()
        self.word_label.setText(f"Draw this word: \n {self.currentWord}")
        self.canvas.clear()

        # Close the guessing window and open it again for the new turn
        self.show_guessing_window()


class GuessingWindow(QWidget):
    guess_correct = pyqtSignal()
    time_expired = pyqtSignal()

    def __init__(self, correct_word):
        super().__init__()
        self.correct_word = correct_word
        self.setWindowTitle("Pictionary")
        self.setGeometry(600, 300, 400, 300)
        self.time_remaining = 60
        self.timer = None
        self.is_drawer_view = True  # Flag to track current view

        # Create stacked widget to manage different views
        self.stacked_layout = QStackedWidget()

        # Create drawer view
        self.drawer_widget = QWidget()
        drawer_layout = QVBoxLayout()

        # Word display for drawer
        word_title = QLabel("You will draw:")
        word_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 10px;
            }
        """)
        word_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.word_display = QLabel(self.correct_word)
        self.word_display.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #27AE60;
                padding: 20px;
                background-color: #F0F2F5;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        self.word_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Start Drawing!")
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                font-weight: bold;
                padding: 15px 30px;
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 8px;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        self.start_button.clicked.connect(self.start_game)

        drawer_layout.addWidget(word_title)
        drawer_layout.addWidget(self.word_display)
        drawer_layout.addWidget(self.start_button)
        self.drawer_widget.setLayout(drawer_layout)

        # Create guesser view
        self.guesser_widget = QWidget()
        guesser_layout = QVBoxLayout()

        self.timer_label = QLabel(f"Time Remaining: {self.time_remaining}s")
        self.timer_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2C3E50;
                padding: 10px;
                background-color: #ECF0F1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.guess_label = QLabel("Enter your guess:")
        self.guess_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #2C3E50;
                margin-top: 10px;
            }
        """)

        self.guess_input = QLineEdit()
        self.guess_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #BDC3C7;
            }
        """)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                padding: 10px 20px;
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        self.submit_button.clicked.connect(self.check_guess)

        guesser_layout.addWidget(self.timer_label)
        guesser_layout.addWidget(self.guess_label)
        guesser_layout.addWidget(self.guess_input)
        guesser_layout.addWidget(self.submit_button)
        self.guesser_widget.setLayout(guesser_layout)

        # Add both views to stacked widget
        self.stacked_layout.addWidget(self.drawer_widget)
        self.stacked_layout.addWidget(self.guesser_widget)

        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_layout)
        self.setLayout(main_layout)

        # Start with drawer view
        self.stacked_layout.setCurrentWidget(self.drawer_widget)

    def start_game(self):
        self.is_drawer_view = False
        self.stacked_layout.setCurrentWidget(self.guesser_widget)
        self.start_timer()

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self):
        self.time_remaining -= 1
        self.timer_label.setText(f"Time Remaining: {self.time_remaining}s")

        if self.time_remaining <= 10:
            self.timer_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                    padding: 10px;
                    background-color: #E74C3C;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
            """)

        if self.time_remaining <= 0:
            self.time_up()

    def check_guess(self):
        guess = self.guess_input.text().strip().lower()
        if guess == self.correct_word.lower():
            if self.timer:
                self.timer.stop()
            QMessageBox.information(self, "Correct!", "You guessed the word!")
            self.guess_correct.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Incorrect", "Try again!")
            self.guess_input.clear()
            self.guess_input.setFocus()

    def time_up(self):
        if self.timer:
            self.timer.stop()
        QMessageBox.information(self, "Time's Up", f"Time's up! The word was: {self.correct_word}")
        self.time_expired.emit()
        self.close()

    def closeEvent(self, event):
        if self.timer:
            self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PictionaryGame()
    window.show()
    app.exec()