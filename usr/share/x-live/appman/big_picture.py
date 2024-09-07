from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import requests
import os
from io import BytesIO
import sys

arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/appman/')

os.chdir(arbeitsverzeichnis)

class ImageWindow(QWidget):
    def __init__(self, image_url, title, parent=None):
        super().__init__(parent)

        # Setze den Titel des Fensters
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("./appman.png"))

        # Bild von der URL herunterladen und in ein QPixmap umwandeln
        pixmap = self.download_image(image_url)

        # Erstelle ein QLabel für das Bild
        self.label = QLabel(self)
        max_width = 1280
        max_height = 650
        scaled_pixmap = pixmap.scaled(max_width, max_height, aspectRatioMode=1)  # 1 =
        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignCenter)

        # Layout für das Widget
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.resize(scaled_pixmap.size())

    def download_image(self, url):
        """Download the image from the URL and return a QPixmap."""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Ensure we notice bad responses
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.read())
            return pixmap
        except requests.RequestException as e:
            print(f"Fehler beim Herunterladen des Bildes: {e}")
            return QPixmap()  # Rückgabe eines leeren Pixmaps im Fehlerfall

if __name__ == "__main__":
    # Überprüfe, ob die Argumente beim Start des Programms übergeben wurden
    if len(sys.argv) != 3:
        print("Verwendung: python image_window.py <Bild-URL> <Fenstertitel>")
        sys.exit(1)

    # Argumente einlesen
    image_url = sys.argv[1]
    title = sys.argv[2]

    app = QApplication(sys.argv)

    # Erstelle das ImageWindow mit den angegebenen Werten
    window = ImageWindow(image_url, title)
    
    # Setze die Größe des Fensters (optional)
    #window.resize(800, 600)
    
    # Zeige das Fenster an
    window.show()
    
    # Starte die Anwendung
    sys.exit(app.exec_())
