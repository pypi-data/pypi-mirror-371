# functions_console.py
from .imports import QWidget,pyqtSignal
from abstract_gui.QT6 import add_logs_to
from .initFuncs import initFuncs
# --- Console ---------------------------------------------------------------
class functionsTab(QWidget):
    functionSelected = pyqtSignal(str)
    scanRequested = pyqtSignal(str)  # scope string ("all" | "reachable")

    def __init__(self, parent=None, use_flow=True):
        super().__init__(parent)
        self.func_map = {}
        self.init_path= '/var/www/html/clownworld/bolshevid'
        self.fn_filter_mode = "io"
        self.current_fn = None
        self._build_ui(use_flow)
functionsTab = initFuncs(functionsTab)
