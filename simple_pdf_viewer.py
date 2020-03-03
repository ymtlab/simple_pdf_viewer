# -*- coding: utf-8 -*-
import subprocess
import sys
from mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pdftocairo_path = Path('poppler-0.68.0/bin/pdftocairo.exe')
        self.setAcceptDrops(True)
        self._numScheduledScalings = 0
        self.ui.graphicsView.wheelEvent = self.wheelEvent

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        event.accept()
        path = event.mimeData().urls()[0].toLocalFile()

        cmd = [str(self.pdftocairo_path), '-png', '-r', '200', path, '__tmp__']
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        proc = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            startupinfo=startupinfo
        )
        stdout, stderr = proc.communicate(timeout=1000)
        
        if stderr:
            return stdout, stderr

        image = QtGui.QImage('__tmp__-1.png', 'PNG')
        pixmap = QtGui.QPixmap.fromImage(image)
        scene = QtWidgets.QGraphicsScene(self)
        scene.addPixmap(pixmap)
        Path('__tmp__-1.png').unlink()

        self.ui.graphicsView.setScene(scene)
        self.ui.graphicsView.scale(1.0, 1.0)

    def execContextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('Clear', self.clear_item)
        self.menu.exec( self.focusWidget().mapToGlobal(point) )

    def wheelEvent(self, event):
        numDegrees = event.angleDelta().y() / 8
        numSteps = numDegrees / 15
        self._numScheduledScalings += numSteps
        if self._numScheduledScalings * numSteps < 0:
            self._numScheduledScalings = numSteps
        anim = QtCore.QTimeLine(350, self)
        anim.setUpdateInterval(20)
        anim.valueChanged.connect(self.scalingTime)
        anim.finished.connect(self.animFinished)
        anim.start()

    def scalingTime(self, x):
        factor = 1.0 + float(self._numScheduledScalings) / 300.0
        self.ui.graphicsView.scale(factor, factor)

    def animFinished(self):
        if self._numScheduledScalings > 0:
            self._numScheduledScalings -= 1
        else:
            self._numScheduledScalings += 1

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()
 
if __name__ == '__main__':
    main()
