from .imports import QTabWidget,QMainWindow,apiConsole,reactRunnerConsole,ContentFinderConsole,clipitTab,windowManagerConsole
from .logTab import logTab
class abstractIde(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract Tools")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # If you want these consoles independent, give each its OWN bus.
        # If you want them to share state globally, make ONE bus and pass it to all.
        self.logConsole    = logTab()              # own bus for content-group only
        self.contentFinder = ContentFinderConsole()              # own bus for content-group only
        self.reactRunner   = reactRunnerConsole()                # independent
        self.apiConsole    = apiConsole()                   # independent
        self.clipit        = clipitTab()
        self.windowMgr     = windowManagerConsole()
        
        self.tabs.addTab(self.reactRunner,   "Reach Runner")
        self.tabs.addTab(self.contentFinder, "Content Finder")
        self.tabs.addTab(self.apiConsole,      "api console")
        self.tabs.addTab(self.clipit,           "clipit")
        self.tabs.addTab(self.windowMgr,      "window mgr")
        self.tabs.addTab(self.logConsole,      "Logs")
