from pyqt6 import QtWidgets, QtCore

class InputDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数値入力")
        self.setGeometry(100, 100, 200, 100)

        # レイアウト
        layout = QtWidgets.QVBoxLayout(self)

        # 数値入力用のQLineEdit
        self.number_input = QtWidgets.QLineEdit(self)
        layout.addWidget(self.number_input)

        # OKボタン
        self.ok_button = QtWidgets.QPushButton("OK", self)
        layout.addWidget(self.ok_button)

        # OKボタンを押すとダイアログを閉じる
        self.ok_button.clicked.connect(self.accept)

    def get_number(self):
        try:
            return int(self.number_input.text())
        except ValueError:
            return None


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # レイアウトを設定
        layout = QtWidgets.QVBoxLayout(self)

        # QLineEditを作成
        self.image_start = QtWidgets.QLineEdit(self)
        layout.addWidget(self.image_start, alignment=QtCore.Qt.AlignLeft)

        # ボタンを追加するレイアウト
        bottom_btn_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(bottom_btn_layout)

        # 数値入力用ダイアログを表示するボタン
        self.button = QtWidgets.QPushButton("数値入力ウィンドウを開く")
        bottom_btn_layout.addWidget(self.button)

        # シグナルとスロットを接続
        self.button.clicked.connect(self.open_input_dialog)

    # ボタンを押したときに呼ばれる関数
    def open_input_dialog(self):
        dialog = InputDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            number = dialog.get_number()
            if number is not None:
                self.image_start.setText(str(number))  # メインウィンドウのQLineEditに数値を反映
            else:
                print("無効な数値が入力されました")


# アプリケーションを実行
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
