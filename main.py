import hou
import importlib
import level_node
importlib.reload(level_node)
from PySide2.QtWidgets import QPlainTextEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel,QLineEdit, QHBoxLayout
from PySide2.QtGui import QFont, QIntValidator
from level_node import Node, NodeGraph, NodeType


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)

        self.graph = NodeGraph()

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.textarea = QPlainTextEdit()
        self.button = QPushButton("Generate Level")
        self.h_layout = QHBoxLayout()
        self.width_input_label = QLabel("Floor Width")
        self.width_input = QLineEdit()
        self.height_input_label = QLabel("Floor Height")
        self.height_input = QLineEdit()

        self.init_ui()

        self.connect_signals()


    def button_click(self):
        self.graph.nodes = []

        self.add_nodes()

        self.graph.connect_nodes()
        self.graph.set_wall_dir()
        self.add_points()

        #print(self.graph)

    def add_nodes(self):
        text = self.textarea.toPlainText()
        text = text.splitlines()
        for i, line in enumerate(text):
            for j, char in enumerate(line):
                if char == " ":
                    continue
                node = Node(i, j)
                if char == "+":
                    node.level += 1
                    node.node_type = NodeType.STAIRS_UP
                elif char == "-":
                    node.level -= 1
                    node.node_type = NodeType.STAIRS_DOWN
                elif char == "D":
                    node.node_type = NodeType.DOOR

                self.graph.add_node(node)

    def add_points(self):
        nodes = self.graph.nodes

        height_multiplier = int(self.height_input.text())
        width_multiplier = int(self.width_input.text())

        wrangle_string = ""

        obj = hou.node("obj/")
        geo = obj.createNode("geo")
        add_node = geo.createNode("add")
        copy_node = geo.createNode("copytopoints::2.0")
        grid_node = geo.createNode("grid")
        attrib_node = geo.createNode("attribcreate::2.0")
        wrangle_node = geo.createNode("attribwrangle")
        transform_node = geo.createNode("xform")
        null_node = geo.createNode("null","POINTS_OUT")

        #Set Params

        #Set attributes
        attrib_node.setParms({
            "numattr":5,
            "name1":"type",
            "default1v1":1,
            "value1v1":1,
            "type1":1,
            "name2": "type_name",
            "string2": "DEFAULT",
            "type2": 3,
            "name3":"wall_dir",
            "size3":4,
            "type3": 1,
            "name4":"module_width",
            "class4":0,
            "value4v1":width_multiplier,
            "name5":"module_height",
            "class5": 0,
            "value5v1": height_multiplier

        })

        add_node.parm("points").set(len(nodes))

        for i, node in enumerate(self.graph.nodes):
            add_node.setParms({
                f"pt{i}x":node.x * width_multiplier,
                f"pt{i}y":node.level * height_multiplier,
                f"pt{i}z":node.y * width_multiplier,
            })
            wrangle_string += f"setpointattrib(0,'type',{i},{node.node_type.value});setpointattrib(0,'type_name',{i},'{node.node_type.name}');setpointattrib(0,'wall_dir',{i},{{{node.wall_dir[0]},{node.wall_dir[1]},{node.wall_dir[2]},{node.wall_dir[3]}}});\n"

        grid_node.setParms({
            "sizex":width_multiplier,
            "sizey":width_multiplier,
            "rows":3,
            "cols":3
        })

        wrangle_node.setParms(
            {
                "class":0,
                "snippet":wrangle_string
            }
        )

        transform_node.parm("sz").set(-1)


        #Set inputs
        attrib_node.setInput(0,add_node)
        wrangle_node.setInput(0,attrib_node)
        transform_node.setInput(0,wrangle_node)
        null_node.setInput(0,transform_node)

        copy_node.setInput(0,grid_node)
        copy_node.setInput(1, null_node)

        null_node.setDisplayFlag(True)
        null_node.setRenderFlag(True)

        geo.layoutChildren()


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


        level_map = [
            "**********  ",
            "*           ",
            "*           ",
            "*******     ",
            "      +     ",
            "  *   *     ",
            "  *  **+    ",
            "  ---* *    "
        ]

        level_string = "\n".join(level_map)

        self.h_layout.addWidget(self.width_input_label)
        self.h_layout.addWidget(self.width_input)
        self.h_layout.addWidget(self.height_input_label)
        self.h_layout.addWidget(self.height_input)
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

