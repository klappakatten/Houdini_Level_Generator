import importlib
import level_node_graph, houdini_nodes
importlib.reload(level_node_graph)
importlib.reload(houdini_nodes)
from PySide2.QtWidgets import QPlainTextEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel,QLineEdit, QHBoxLayout
from PySide2.QtGui import QFont, QIntValidator
from level_node_graph import Node, NodeGraph, NodeType
from houdini_nodes import HoudiniNodes

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)

        self.houdini = HoudiniNodes()
        self.graph = NodeGraph()

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.textarea = QPlainTextEdit()
        self.button = QPushButton("Generate Level")
        self.h_layout = QHBoxLayout()
        self.width_input_label = QLabel("Module Dimensions (width / depth)")
        self.width_input = QLineEdit()
        self.height_input_label = QLabel("Stair Height")
        self.height_input = QLineEdit()

        self.init_ui()

        self.connect_signals()


    def button_click(self):
        self.graph.nodes = []

        self.add_nodes()

        self.graph.connect_nodes()
        self.graph.set_wall_dir()
        self.graph.set_doors()

        self.houdini.create_nodes(self.graph, self.get_width_input(), self.get_height_input())

    def get_width_input(self):
        return int(self.width_input.text())

    def get_height_input(self):
        return int(self.width_input.text())/2


    def add_nodes(self):
        text = self.textarea.toPlainText()
        text = text.splitlines()

        for y, line in enumerate(text):
            for x, char in enumerate(line):
                if char == " ":
                    continue
                node = Node(x, y)
                if char == "+":
                    node.level += 1
                    node.node_type = NodeType.STAIRS_UP
                elif char == "-":
                    node.level -= 1
                    node.node_type = NodeType.STAIRS_DOWN
                elif char == "D":
                    node.node_type = NodeType.DOOR

                self.graph.add_node(node)

    def init_ui(self):
        self.setWindowTitle("Level Map")
        font = QFont("Courier New", 12)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing,10)
        font.setWordSpacing(0)
        self.textarea.setFont(font)
        self.textarea.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.height_input_label.setBuddy(self.height_input)
        self.width_input_label.setBuddy(self.width_input)

        validator = QIntValidator()
        self.height_input.setPlaceholderText("Height")
        self.height_input.setText(str(1))
        self.height_input.setValidator(validator)
        self.width_input.setPlaceholderText("Width")
        self.width_input.setText(str(5))
        self.width_input.setValidator(validator)


        default_level_map = [
            "**********    *** *++***",
            "*               - +    *",
            "******      -   - +    ",
            "************++++*+*    ",
            "      D    -    -",
            "  *   *     ",
            "  *  **+*    ",
            "  ---*  *    "
        ]

        level_string = "\n".join(default_level_map)

        self.h_layout.addWidget(self.width_input_label)
        self.h_layout.addWidget(self.width_input)
        #self.h_layout.addWidget(self.height_input_label)
        #self.h_layout.addWidget(self.height_input)
        self.layout.addLayout(self.h_layout)
        self.textarea.setPlainText(level_string)
        self.layout.addWidget(self.textarea)
        self.layout.addWidget(self.button)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def connect_signals(self):
        self.button.clicked.connect(self.button_click)


#app = QApplication(sys.argv)
#window = MainWindow()

#window.show()
#app.exec()

