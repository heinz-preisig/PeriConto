import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QMenu
from PyQt5.QtWidgets import QApplication, QMenuBar, QGridLayout, QAction, qApp, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt


class Ontovis(QWidget):

    def __init__(self):
        super().__init__()

        # layout = QGridLayout()
        # self.setLayout(layout)

        # # create menu
        # menubar = QMenuBar()
        # layout.addWidget(menubar, 0, 0)
        # actionFile = menubar.addMenu("File")
        # actionFile.addAction("New")
        # actionFile.addAction("Open")
        # actionFile.addAction("Save")
        # actionFile.addSeparator()
        # actionFile.addAction("Quit")
        # menubar.addMenu("Edit")
        # menubar.addMenu("View")
        # menubar.addMenu("Help")

        self.initUI()

    def initUI(self):

        # vbox = QVBoxLayout(self)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.menubar = QMenuBar()
        self.layout.addWidget(self.menubar, 0, 0)
        #menubar = layout.addWidget(QMenuBar(self))

        self.fileMenu = QMenu('File')
        self.menubar.addMenu(self.fileMenu)

        #TODO: implement a user option to select a ontology_nx.html file to visualize
        self.fileMenu.addAction('Open', lambda: self.loadPage())

        #TODO: implement save action, e.g. take a snapshot and save as png 
        self.fileMenu.addAction('Save', lambda: print('save'))

        self.helpmenu = QMenu('Help')
        self.menubar.addMenu(self.helpmenu)

        self.layout.setMenuBar(self.menubar)


        self.webEngineView = QWebEngineView()
        #self.loadPage()

        # button_open_action = QAction("Open",self)
        # button_open_action.triggered.connect(self.loadPage)
        #button_action2.setCheckable(True)

        # quit_action = QAction('Quit', self)
        # quit_action.triggered.connect(self.quitActionClicked)


        self.layout.addWidget(self.webEngineView)

        self.setLayout(self.layout)
        
        self.setGeometry(300, 300, 600, 1200)
        self.setWindowTitle('OntoVis')
        #self.showMaximized()

    def loadPage(self):
  
        with open('../nx.html', 'r') as f:

            html = f.read()
            self.webEngineView.setHtml(html)

    
    # def quitActionClicked(self):
    #     qApp.quit()

# def main():

#     app = QApplication(sys.argv)
#     ex = Ontovis()
#     sys.exit(app.exec_())


if __name__ == '__main__':
    # main()
    app = QApplication(sys.argv)
    ex = Ontovis()
    ex.show()
    sys.exit(app.exec_())