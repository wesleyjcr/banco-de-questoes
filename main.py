#!/bin/env python3   
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *                 
from PyQt5.QtGui import *    
from PyQt5.QtWidgets import QMainWindow, QApplication              
from controller.principal import *     

if __name__ == "__main__":
    app = QApplication(sys.argv)      
    prin = Principal()
    prin.setAttribute(Qt.WA_DeleteOnClose)
    prin.showMaximized()
    app.exec_()
