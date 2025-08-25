# ChartBot Pro Refined
# Educational tool only. Not financial advice.

import sys, os, re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PIL import Image
import pytesseract

APP_TITLE = "ChartBot Pro"
VERSION = "2.2.0"

def bundle_base():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

def configure_tesseract():
    base = bundle_base()
    # Preferred: bundled inside EXE (PyInstaller)
    texe = os.path.join(base, "tess", "tesseract.exe")
    tdata = os.path.join(base, "tess", "tessdata")
    if os.path.exists(texe) and os.path.exists(tdata):
        pytesseract.pytesseract.tesseract_cmd = texe
        os.environ["TESSDATA_PREFIX"] = os.path.join(base, "tess")
        return texe

    # Fallback: repo local files (running from source)
    here = os.path.dirname(os.path.abspath(__file__))
    texe = os.path.join(here, "tess", "tesseract.exe")
    tdata = os.path.join(here, "tess", "tessdata")
    if os.path.exists(texe) and os.path.exists(tdata):
        pytesseract.pytesseract.tesseract_cmd = texe
        os.environ["TESSDATA_PREFIX"] = os.path.join(here, "tess")
        return texe

    # System installs (if any)
    for p in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            os.environ["TESSDATA_PREFIX"] = os.path.dirname(p)
            return p

    return None

def parse_levels(text: str):
    nums = []
    for m in re.findall(r"\b\d{1,6}(?:\.\d{1,4})?\b", text.replace(',', ''))[:12]:
        try: 
            f = float(m)
            if f > 0: nums.append(f)
        except: 
            pass
    nums.sort()
    if not nums: return None
    if len(nums) >= 3:
        mid = nums[len(nums)//2]
        return mid, mid*1.02, mid*0.99
    if len(nums) == 2:
        e = sum(nums)/2
        return e, max(nums)*1.01, min(nums)*0.99
    e = nums[0]
    return e, e*1.02, e*0.99

def bias_from_text(text: str):
    U = text.upper()
    longish = any(w in U for w in ["BUY","LONG","BULL","SUPPORT"])
    shortish = any(w in U for w in ["SELL","SHORT","BEAR","RESISTANCE"])
    if longish and not shortish: return "📈 Long bias"
    if shortish and not longish: return "📉 Short bias"
    return "⚖️ Neutral"

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(980, 640)
        self.setWindowIcon(QIcon("icon.ico"))
        self.tesseract_path = configure_tesseract()

        central = QWidget(); self.setCentralWidget(central)
        v = QVBoxLayout(central)

        top = QHBoxLayout()
        self.btn_open = QPushButton("Open Chart Image")
        self.btn_open.clicked.connect(self.open_img)
        self.btn_analyze = QPushButton("Analyze")
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self.analyze)
        top.addWidget(self.btn_open); top.addWidget(self.btn_analyze); top.addStretch(1)
        v.addLayout(top)

        self.preview = QLabel("No image loaded")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("QLabel{background:#111;color:#bbb;padding:10px;}")
        v.addWidget(self.preview, 3)

        self.out = QTextEdit(); self.out.setReadOnly(True)
        v.addWidget(self.out, 2)

        self.image_path = None
        self.statusBar().showMessage(f"Tesseract: {self.tesseract_path or 'not found'}  |  v{VERSION}")

    def open_img(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open Chart", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not p: return
        self.image_path = p
        pix = QPixmap(p)
        if pix.isNull():
            self.preview.setText("Failed to load image.")
        else:
            self.preview.setPixmap(pix.scaledToWidth(900, Qt.SmoothTransformation))
        self.btn_analyze.setEnabled(True)
        self.out.setPlainText(f"Loaded: {os.path.basename(p)}")

    def analyze(self):
        if not self.image_path:
            QMessageBox.warning(self, "No image", "Please open a chart image first.")
            return
        text = ""
        if self.tesseract_path and os.path.exists(self.tesseract_path):
            text = pytesseract.image_to_string(Image.open(self.image_path), lang="eng")
        bias = bias_from_text(text)
        levels = parse_levels(text)
        lines = [
            f"File: {os.path.basename(self.image_path)}",
            f"Tesseract: {self.tesseract_path or 'not found'}",
            f"Bias: {bias}",
            ""
        ]
        if levels:
            e,tp,sl = levels
            lines += [f"Suggested Entry: {e:.4f}", f"Take Profit:     {tp:.4f}", f"Stop Loss:       {sl:.4f}"]
        else:
            lines += ["Could not infer numeric levels from OCR."]
        lines += ["", "OCR Preview:", (text[:1200] or "(empty)")]
        self.out.setPlainText("\n".join(lines))

def main():
    app = QApplication(sys.argv)
    w = Main(); w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
