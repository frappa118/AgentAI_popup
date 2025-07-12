import time
import random
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer


#set-up frasi
frasi = [
    "Napoli è una bella citta finche non la invadi",
    "Milano è bella ma finche ci vai",
    "Roma è bella ma finche non ci vivi",
    "Oggi è una bella giornata per imparare qualcosa di nuovo!",
    "ESATTO la scienza è un opinione"
    ]
# randomizza una frase
frase = random.choice(frasi)
# random size
size = random.randint(100, 1000)

class PopUp(QDialog):
    def __init__(self):
        super().__init__()
        # impostazione della del titolo della finestra
        self.setWindowTitle("Il saggio dice...")
        # dimensioni finestra
        self.setFixedSize(size, size) #(lunghezza, altezza)
        self.setStyleSheet('''
                QDialog {
                    background-color: #f0f8ff;
                }
                QLabel {
                    font-size: 14px;
                    color: #100;
                    padding: 20px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    font-size: 12px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                ''')
        layout = QVBoxLayout()
        # Testo casuale
        self.label = QLabel(frase)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        # Bottone
        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

        self.setLayout(layout)
        # Centra la finestra
        self.posizione_casuale()

    def posizione_casuale(self):
        screen = QApplication.desktop().screenGeometry()
        max_x = screen.width() - self.width()
        max_y = screen.height() - self.height()
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)
        self.move(x, y)



    """def center(self):
        frame = self.frameGeometry()
        screen = QApplication.desktop().screenGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())
    """
def mostra_popup():
    """Pop-up usando PyQt5"""
    app = QApplication(sys.argv)
    popup = PopUp()
    popup.exec_()  # Mostra il pop-up e attende la chiusura
    #sys.exit(app.exec_())  # Termina l'applicazione quando il pop-up è chiuso

for i in range(3):
    mostra_popup()
