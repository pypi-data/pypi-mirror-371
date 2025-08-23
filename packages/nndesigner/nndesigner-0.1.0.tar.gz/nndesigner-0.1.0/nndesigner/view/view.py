
from nndesigner.utils.base import *
from .node_panel import NodePanel
from .custom_widget import CollapsibleGroup


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("nndesigner 主界面")

        self.node_panel = NodePanel(self)
        self.setCentralWidget(self.node_panel)
        self.init_ui_bar()
        self.init_dock_widgets()

    def init_ui_bar(self):
        # 菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        new_action = QAction("新建", self)
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.on_new_tab)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def init_dock_widgets(self):
        self.left_dock = QDockWidget("node list", self)
        self.left_dock.setWidget(self._create_left_panel())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        self.right_dock = QDockWidget("右侧面板", self)
        self.right_dock.setWidget(QLabel("这里是右侧Dock内容"))
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

    def _create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)

        # 搜索框
        search_box = QLineEdit()
        search_box.setPlaceholderText("搜索节点/算子...")
        search_box.setClearButtonEnabled(True)
        search_box.setStyleSheet("QLineEdit { font-size: 15px; padding: 6px; }")
        layout.addWidget(search_box)

        # 节点分组
        node_groups = OmegaConf.load(DEFAULT_NODE_GROUP_CONFIG_PATH)
        self._group_widgets = []
        for group in node_groups:
            if group.get("type") == "torch":
                nodes = eval(group["nodes"])
            else:
                nodes = group["nodes"]
            group_widget = CollapsibleGroup(group.name, group.type, nodes)
            layout.addWidget(group_widget)
            self._group_widgets.append((group_widget, nodes))
            group_widget.list_widget.dragFinished.connect(self.on_node_drag_finished)

        layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(panel)

        # 搜索逻辑
        def do_search(text):
            text = text.strip().lower()
            for group_widget, nodes in self._group_widgets:
                if not text:
                    group_widget.setVisible(True)
                    group_widget.list_widget.clear()
                    for n in nodes:
                        QListWidgetItem(n, group_widget.list_widget)
                else:
                    filtered = [n for n in nodes if text in n.lower()]
                    group_widget.setVisible(bool(filtered))
                    group_widget.list_widget.clear()
                    for n in filtered:
                        QListWidgetItem(n, group_widget.list_widget)

        search_box.textChanged.connect(do_search)
        return scroll

    def on_node_drag_finished(self, node_type, node_name):
        # 这里可以做日志、提示、统计等
        print(f"节点拖拽完成: {node_type} {node_name}")

    def on_new_tab(self):
        self.node_panel.add_tab()



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    # 使用qdarktheme美化界面
    try:
        import qdarkstyle
        from qdarkstyle.dark.palette import DarkPalette
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6", palette = DarkPalette))
    except ImportError:
        pass  # 未安装qdarktheme时保持默认

    window = MainWindow()

    window.show()
    sys.exit(app.exec())
