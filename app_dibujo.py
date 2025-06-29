import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage, QPainter, QPen, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QColorDialog, QFileDialog, QVBoxLayout, QWidget, QPushButton, QLabel

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(Qt.black)
        self.pen_size = 3
        self.undo_stack = []
        self.redo_stack = []

    def resizeEvent(self, event):
        if self.image.size() != self.size():
            new_image = QImage(self.size(), QImage.Format_RGB32)
            new_image.fill(Qt.white)
            painter = QPainter(new_image)
            painter.drawImage(QPoint(), self.image)
            self.image = new_image
        super().resizeEvent(event)

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.undo_stack.append(self.image.copy())
            self.redo_stack.clear()

    def mouseMoveEvent(self, event):
        if self.drawing and event.buttons() & Qt.LeftButton:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.pen_color, self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas = QPainter(self)
        canvas.drawImage(self.rect(), self.image, self.image.rect())

    def clear_canvas(self):
        self.image.fill(Qt.white)
        self.update()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update()

    def save_image(self, file_path):
        self.image.save(file_path)

    def load_image(self, file_path):
        loaded_image = QImage(file_path)
        if not loaded_image.isNull():
            self.image = loaded_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.update()


class DibujoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('App de Dibujo')
        self.setGeometry(100, 100, 800, 600)
        
        self.canvas = Canvas()
        layout = QVBoxLayout()

        self.image_label = QLabel("Aquí se mostrará tu dibujo")
        layout.addWidget(self.canvas)

        self.upload_button = QPushButton('Cargar Dibujo')
        self.upload_button.clicked.connect(self.cargar_dibujo)
        layout.addWidget(self.upload_button)

        self.save_button = QPushButton('Guardar Dibujo')
        self.save_button.clicked.connect(self.guardar_dibujo)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.create_menu()

    def create_menu(self):
        clear_action = QAction("Limpiar", self)
        clear_action.triggered.connect(self.canvas.clear_canvas)

        undo_action = QAction("Deshacer", self)
        undo_action.triggered.connect(self.canvas.undo)

        redo_action = QAction("Rehacer", self)
        redo_action.triggered.connect(self.canvas.redo)

        pen_color_action = QAction("Color del Pincel", self)
        pen_color_action.triggered.connect(self.choose_pen_color)

        toolbar = self.addToolBar("Herramientas")
        toolbar.addAction(clear_action)
        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
        toolbar.addAction(pen_color_action)

    def choose_pen_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_pen_color(color)

    def cargar_dibujo(self):
        options = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Dibujo", "", "Archivos de Imagen (*.png *.jpg *.bmp)", options=options)
        if archivo:
            self.canvas.load_image(archivo)

    def guardar_dibujo(self):
        options = QFileDialog.Options()
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Dibujo", "", "Archivos de Imagen (*.png *.jpg *.bmp)", options=options)
        if archivo:
            self.canvas.save_image(archivo)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = DibujoApp()
    ventana.show()

    sys.exit(app.exec_())
