from .functionsTab import functionsTab
from .runnerTab import runnerTab
from abstract_gui import startConsole
from abstract_gui.QT6 import ConsoleBase, QTabWidget
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class reactRunnerConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)

        # all content tabs share THIS console’s bus
        inner.addTab(runnerTab(),      "react Runner")
        inner.addTab(functionsTab(),   "Functions")

def startReactRunnerConsole():
    startConsole(reactRunnerConsole)
