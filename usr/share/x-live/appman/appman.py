import os
import json
import requests
import subprocess
import re
import time
from PyQt5.QtCore import QProcess
from app_info import get_package_info
from screenshot_search import fetch_image_urls
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QListWidget, QWidget, QHBoxLayout, QLabel, QTextEdit, QPushButton, QDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage,QTextCursor, QIcon
# Pfad zum gewünschten Arbeitsverzeichnis # Das Arbeitsverzeichnis festlegen
arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/appman/')

os.chdir(arbeitsverzeichnis)

class PackageManager(QMainWindow):
    def __init__(self):
        super().__init__()
        os.system("sh ./pkg_sort.sh")

        self.setWindowTitle("X-Live-AppMan")
        self.setWindowIcon(QIcon("./appman.png"))
        self.setGeometry(100, 100, 600, 600)
        self.setFixedWidth(800)
        self.process = None

        # Layout und zentrale Widget-Initialisierung
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Übersetzungstabelle laden oder erstellen
        self.translations = check_and_update_translations(self.get_available_categories(), 'translations.json')

        # Kombobox für Kategorien
        self.category_combo = QComboBox(self)
        self.load_categories()
        self.category_combo.currentIndexChanged.connect(self.load_packages)
        self.layout.addWidget(self.category_combo)
        self.category_combo.hide()

        # Kombobox für populäre Kategorien
        self.popular_categories = [
            "games", "video", "sound", "graphics", "web", "text",
            "education", "doc", "admin", "all"
        ]

        self.popular_category_combo = QComboBox(self)
        self.load_popular_categories()
        self.popular_category_combo.currentIndexChanged.connect(self.load_packages_from_popular)
        self.layout.addWidget(self.popular_category_combo)

        self.pack_info_layout = QVBoxLayout()
        self.pack_title = QLabel()
        self.pack_info = QTextEdit()
        self.pack_info.setStyleSheet("border: none")
        self.pack_install = QPushButton("installieren")
        self.pack_install.setStyleSheet(""" QPushButton {background: green;color: white;} QPushButton:disabled {background: gray;color: light_gray;}""")
        self.pack_uninstall = QPushButton("deinstallieren")
        self.pack_uninstall.setStyleSheet(""" QPushButton {background: red;color: white;} QPushButton:disabled {background: gray;color: light_gray;}""")
        self.pack_uninstall.hide()
        self.pack_uninstall.clicked.connect(self.uninstall_start)
        self.pack_install.clicked.connect(self.install_start)
        self.img_layout=QHBoxLayout()
        self.img_layout.addStretch(0)
        self.pack_img = QPushButton()
        self.pack_img.clicked.connect(self.new_window)
        self.img_layout.addWidget(self.pack_img)
        self.img_layout.addStretch(0)
        self.install_layout = QHBoxLayout()
        self.install_layout.addStretch(5)
        self.install_layout.addWidget(self.pack_install)
        self.install_layout.addWidget(self.pack_uninstall)
        
        self.pack_info_layout.addStretch(1)
        self.pack_info_layout.addWidget(self.pack_title)
        self.pack_info_layout.addLayout(self.img_layout)
        self.pack_info_layout.addWidget(self.pack_info)
        self.pack_info_layout.addStretch(2)
        self.pack_info_layout.addLayout(self.install_layout)
        self.pack_info_layout.addStretch(0)

        self.output_area = QTextEdit()
        self.mainlayout = QHBoxLayout()
        self.mainlayout.addLayout(self.layout)
        #self.mainlayout.addStretch(0)
        self.mainlayout.addLayout(self.pack_info_layout)
        self.mainlayout.addWidget(self.output_area)
        self.output_area.hide()

        # ListWidget für Paketliste
        self.package_list = QListWidget(self)
        self.package_list.currentItemChanged.connect(self.on_listwidget_item_changed)
        self.package_list.setFixedWidth(230)
        self.package_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.package_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layout.addWidget(self.package_list)

        self.central_widget.setLayout(self.mainlayout)
        # Initiale Paketliste laden
        self.load_packages_from_popular()
        self.background_color()
        self.package_list.setCurrentRow(0)

    def on_listwidget_item_changed(self, current, previous):
        # Hole den aktuell ausgewählten Text
        if current:
            selected_text = current.text()
            # Aktualisiere das Label mit dem ausgewählten Text
            app_info = get_package_info(selected_text)
            img_url = fetch_image_urls(selected_text)
            self.current = current
            self.previous = previous
            self.pack_title.setText(f"{selected_text}")
            self.pack_title.setStyleSheet("font-size: 32px;")
            
            self.pack_info.setText(f" Maintainer: {app_info['Maintainer']}\n Homepage: {app_info['Homepage']}\n Installierte Größe: {app_info['Installed-Size']} KB\n Beschreibung: {app_info['Short Description']}\n\n {app_info['Long Description']}")#\nAbhängigkeiten: {app_info['Depends']} \n")
            
            if not img_url:
                img_url = ["https://screenshots.debian.net/images/dummy/no-screenshots-upload-one.svg"]
            pixmap = QPixmap()
            pixmap.loadFromData(self.download_image(img_url[0]))
            max_width = 500
            max_height = 240
            scaled_pixmap = pixmap.scaled(max_width, max_height, aspectRatioMode=1)  # 1 = Qt.AspectRatioMode.KeepAspectRatio
            self.pack_img.setIcon(QIcon(pixmap))
            self.pack_img.setIconSize(scaled_pixmap.size())
            self.nw_img_url = img_url[0]
            self.nw_title = selected_text
            if app_info['Status'] == "yes":
                self.pack_install.hide()
                self.pack_uninstall.show()
            else:
                self.pack_install.show()
                self.pack_uninstall.hide()
            
            
            
            
            
    def new_window(self):
        subprocess.Popen(["python3", "./big_picture.py", self.nw_img_url, self.nw_title])


    def get_available_categories(self):
        # Verfügbare Kategorien aus dem /tmp/x-live/sections/ Verzeichnis abrufen
        category_files = os.listdir('/tmp/x-live/sections/')
        available_categories = [os.path.splitext(f)[0] for f in category_files if f.endswith('.list')]
        return available_categories

    def load_categories(self):
        # Kategorien aus der Übersetzungstabelle laden
        translated_categories = [self.translations.get(cat, cat) for cat in self.get_available_categories()]
        self.category_combo.addItems(translated_categories)

    def load_popular_categories(self):
        # Populäre Kategorien in die ComboBox laden
        translated_categories = [self.translations.get(cat, cat) for cat in self.popular_categories]
        self.popular_category_combo.addItems(translated_categories)

    def load_packages(self):
        # Pakete für die ausgewählte Kategorie laden
        selected_category = self.category_combo.currentText()
        self.package_list.clear()

        # Kategorie in der Originalsprache finden
        original_category = next(key for key, value in self.translations.items() if value == selected_category)

        # Pfad zur gewählten Kategorie .list Datei
        category_file = f'/tmp/x-live/sections/{original_category}.list'

        # Pakete aus der .list Datei laden
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                packages = f.read().splitlines()
            self.package_list.addItems(packages)

    def load_packages_from_popular(self):
        # Pakete für die ausgewählte populäre Kategorie laden
        popular_category = self.popular_category_combo.currentText()
        self.package_list.clear()

        # Kategorie in der Originalsprache finden
        original_category = next(key for key, value in self.translations.items() if value == popular_category)

        # Pfad zur gewählten Kategorie .list Datei
        category_file = f'/tmp/x-live/sections/{original_category}.list'

        # Pakete aus der .list Datei laden
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                packages = f.read().splitlines()
            self.package_list.addItems(packages)

    def download_image(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Fehler beim Herunterladen des Bildes. Status-Code: {response.status_code}")

    # Farbprofil abrufen und anwenden

    def get_current_theme(self):
        try:
            # Versuche, das Theme mit xfconf-query abzurufen
            result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'], capture_output=True, text=True)
            theme_name = result.stdout.strip()
            if theme_name:
                return theme_name
        except FileNotFoundError:
            print("xfconf-query nicht gefunden. Versuche gsettings.")
        except Exception as e:
            print(f"Error getting theme with xfconf-query: {e}")

        try:
            # Fallback auf gsettings, falls xfconf-query nicht vorhanden ist
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
            theme_name = result.stdout.strip().strip("'")
            if theme_name:
                return theme_name
        except Exception as e:
            print(f"Error getting theme with gsettings: {e}")

        return None

    def extract_color_from_css(self,css_file_path, color_name):
        try:
            with open(css_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                #print(content)
                # Muster zum Finden der Farbe
                pattern = r'{}[\s:]+([#\w]+)'.format(re.escape(color_name))
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
                return None
        except IOError as e:
            print(f"Error reading file: {e}")
            return None
            
            
    def background_color(self):
        theme_name = self.get_current_theme()
        if theme_name:
            print(f"Current theme: {theme_name}")

            # Pfad zur GTK-CSS-Datei des aktuellen Themes
            css_file_path = f'/usr/share/themes/{theme_name}/gtk-3.0/gtk.css'
            if os.path.exists(css_file_path):
                bcolor = self.extract_color_from_css(css_file_path, ' background-color')
                color = self.extract_color_from_css(css_file_path, ' color')
                self.central_widget.setStyleSheet(f"background: {bcolor};color: {color}")
            else:
                print(f"CSS file not found: {css_file_path}")
        else:
            print("Unable to determine the current theme.")
            
            
    def install_start(self):
        self.popular_category_combo.hide()
        self.package_list.hide()
        self.output_area.show()
        self.pack_uninstall.setEnabled(False)
        self.pack_install.setEnabled(False)
        self.install_package(self.nw_title)

            
    def uninstall_start(self):
        self.popular_category_combo.hide()
        self.package_list.hide()
        self.output_area.show()
        self.pack_uninstall.setEnabled(False)
        self.pack_install.setEnabled(False)
        self.uninstall_package(self.nw_title)
        
    def un_install_finished(self):
        
        self.popular_category_combo.show()
        self.package_list.show()
        self.output_area.hide()
        self.process = None  
        self.pack_uninstall.setEnabled(True)
        self.pack_install.setEnabled(True)
        self.on_listwidget_item_changed(self.current, self.previous)

    def install_package(self,deb_package):
        if not self.process:
            self.output_area.show()
            self.adjustSize()
            self.output_area.append("Starting package update and installation...\n")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished)
            
            # Prepare the command
            command = f'apt update && apt install -y {deb_package}'
            self.process.start('pkexec', ['sh', '-c', command])
            
    def uninstall_package(self,deb_package):
        if not self.process:
            self.output_area.show()
            self.adjustSize()
            self.output_area.append("Starting package update and installation...\n")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished_remove)
            
            # Prepare the command
            command = f'apt update && apt remove -y {deb_package}'
            self.process.start('pkexec', ['sh', '-c', command])

    def read_output(self):
        if self.process:
            output = self.process.readAll().data().decode()
            output = output.replace('\r\n', '\n').replace('\r', '\n')
            self.output_area.moveCursor(QTextCursor.End)
            self.output_area.insertPlainText(output)
            self.output_area.moveCursor(QTextCursor.End)

    def process_finished(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.output_area.append("\nInstallation completed successfully.")
            QMessageBox.information(self, "Success", "Package installed successfully!")
        else:
            self.output_area.append("\nInstallation failed.")
            QMessageBox.critical(self, "Error", "Failed to install package.")
            
        self.un_install_finished()
        
            
    def process_finished_remove(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.output_area.append("\nUninstallation completed successfully.")
            QMessageBox.information(self, "Success", "Package uninstalled successfully!")
        else:
            self.output_area.append("\nUninstallation failed.")
            QMessageBox.critical(self, "Error", "Failed to uninstall package.")
        
        self.un_install_finished()
                        
            
            
            
            


def check_and_update_translations(categories, translation_file):
    # Übersetzungstabelle prüfen und aktualisieren
    if os.path.exists(translation_file):
        with open(translation_file, 'r') as f:
            translations = json.load(f)
    else:
        translations = {}

    updated = False

    for category in categories:
        if category not in translations:
            translations[category] = category
            updated = True

    if updated:
        with open(translation_file, 'w') as f:
            json.dump(translations, f, indent=4)

    return translations


if __name__ == '__main__':
    app = QApplication([])

    manager = PackageManager()
    manager.show()

    app.exec_()
