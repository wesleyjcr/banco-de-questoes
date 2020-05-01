#!/bin/env python                         
# -*- coding: utf-8 -*-             

import sys
from PyQt5.QtCore import *                 
from PyQt5.QtGui import *                  
from PyQt5.QtSql import *

def abrirBancoDeDados(self):
    #qApp.applicationDirPath()+
    # Estabelecer conexao com o banco de dados
    bancoDeDados = QSqlDatabase.addDatabase("QSQLITE", "storage.db")
    bancoDeDados.setDatabaseName("data/storage.db")
    bancoDeDados.setHostName("localhost")
    bancoDeDados.setUserName("usuario")
    bancoDeDados.setPassword("usuario")
    bancoDeDados.open()

    return bancoDeDados

def fecharBancoDeDados(self,bancoDeDados):
    bancoDeDados = bancoDeDados
    # Fechar conexao com o banco de dados 
    bancoDeDados.close()
