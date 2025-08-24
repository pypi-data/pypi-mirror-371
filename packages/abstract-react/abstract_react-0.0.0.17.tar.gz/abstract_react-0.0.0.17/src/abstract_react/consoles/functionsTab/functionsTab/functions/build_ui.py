from ..imports import *
from abstract_gui.QT6 import attach_textedit_to_logs
# ---- UI ---------------------------------------------------------------
def _build_ui(self, use_flow: bool=True):
    root = QHBoxLayout(self)

    # left panel
    left = QVBoxLayout()
    # path + scope row
    row = QHBoxLayout()
    row.addWidget(QLabel("Project Path:"))
    self.path_in = QLineEdit(self.init_path)
    self.path_in.setPlaceholderText("Folder containing package.json / source")
    row.addWidget(self.path_in, 1)
    row.addWidget(QLabel("Scope:"))
    self.scope_combo = QComboBox(); self.scope_combo.addItems(["all", "reachable"])
    row.addWidget(self.scope_combo)
    left.addLayout(row)

    self.btn_scan = QPushButton("Scan Project Functions")
    left.addWidget(self.btn_scan)
    # Enter in the path box triggers scan too
    self.path_in.returnPressed.connect(lambda: self.scanRequested.emit(self.scope_combo.currentText()))

    self.search_fn = QLineEdit(); self.search_fn.setPlaceholderText("Filter functions…")
    left.addWidget(self.search_fn)

    self.rb_fn_source = QRadioButton("Function")
    self.rb_fn_io = QRadioButton("Import/Export"); self.rb_fn_io.setChecked(True)
    self.rb_fn_all = QRadioButton("All")
    self.fn_filter_group = QButtonGroup(self)
    for rb in (self.rb_fn_source, self.rb_fn_io, self.rb_fn_all):
        self.fn_filter_group.addButton(rb); left.addWidget(rb)

    # scroll area for function "chips"
    self.fn_scroll = QScrollArea(); self.fn_scroll.setWidgetResizable(True)
    self.fn_container = QWidget()
    if use_flow:
        self.fn_layout = flowLayout(self.fn_container, hspacing=8, vspacing=6)
        self.fn_container.setLayout(self.fn_layout)
    else:
        # fallback: vertical list aligned left
        box = QVBoxLayout(self.fn_container)
        box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.fn_layout = box
    self.fn_scroll.setWidget(self.fn_container)
    left.addWidget(self.fn_scroll)

    # right panel
    right = QVBoxLayout()
    right.addWidget(QLabel("Exported In"))
    self.exporters_list = QListWidget(); right.addWidget(self.exporters_list)
    right.addWidget(QLabel("Imported In"))
    self.importers_list = QListWidget(); right.addWidget(self.importers_list)
    right.addWidget(QLabel("Log"))
    self.log_view = QTextEdit(); self.log_view.setReadOnly(True); right.addWidget(self.log_view)
    try:
        attach_textedit_to_logs(self.log_view, tail_file=None)  # live logs, no tail to avoid dupes
    except Exception:
        pass
    root.addLayout(left, 1)
    root.addLayout(right, 2)

    # wire signals
    self.btn_scan.clicked.connect(lambda: self.scanRequested.emit(self.scope_combo.currentText()))
    self.scanRequested.connect(self._start_func_scan)
    self.search_fn.textChanged.connect(self._filter_fn_buttons)
    self.rb_fn_source.toggled.connect(lambda _: self._on_filter_mode_changed())
    self.rb_fn_io.toggled.connect(lambda _: self._on_filter_mode_changed())
    self.rb_fn_all.toggled.connect(lambda _: self._on_filter_mode_changed())
    # double-click to open in VS Code (optional)
    self.exporters_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))
    self.importers_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))
