from .functionsTab import functionsTab
from .runnerTab import runnerTab
from abstract_gui import startConsole
from abstract_gui.QT6 import ConsoleBase, QTabWidget, QMainWindow
from abstract_paths import ContentFinderConsole
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


class reactFinderConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract Tools")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        # If you want these consoles independent, give each its OWN bus.
        # If you want them to share state globally, make ONE bus and pass it to all.
        self.reachRunner   = reactRunnerConsole()                # independent
        self.contentFinder = ContentFinderConsole()              # own bus for content-group only

        self.tabs.addTab(self.reachRunner,   "React Runner")
        self.tabs.addTab(self.contentFinder, "Content Finder")
        


def startReactFinderConsole():
    startConsole(reactFinderConsole)
