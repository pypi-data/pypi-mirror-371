# main.py - 启动入口
import sys
from PySide6.QtWidgets import QApplication
from nndesigner.view.view import MainWindow

def main():
	app = QApplication(sys.argv)
	# 使用qdarktheme美化界面
	try:
		import qdarkstyle
		from qdarkstyle.dark.palette import DarkPalette
		app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6", palette=DarkPalette))
	except ImportError:
		pass
	window = MainWindow()
	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
