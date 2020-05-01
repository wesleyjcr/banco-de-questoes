#!/bin/env python3
# -*- coding: utf-8 -*-

## [Ficha]##################################################
#	                                                       #
#  Nome: Modulo View				                       #
#  Escrito por: Wesley Júnior de Castro Ribeiro            #
#						                                   #
#  [Descricao]##############################################
#					                                       #
#  Este script contem as classes que se comunicam com      #
#  a interface grafica.                                    #
#					                                       #
############################################################

import sys
import os
import datetime
import shutil
import zipfile
import webbrowser
import _thread
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMainWindow, QDataWidgetMapper, QFileDialog, QMessageBox

from model.model import *
from view.principal import *

class Principal(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Principal, self).__init__(parent)
        self.setupUi(self)

        self.editID.setVisible(False)
        self.bancoDeDados = abrirBancoDeDados(self)
        self.modelPrincipal = QSqlTableModel(self, self.bancoDeDados)
        self.buttonUpdate.setVisible(False)
        self.abrirTabela('')

        self.mapeador = QDataWidgetMapper()
        self.mapeador.setModel(self.modelPrincipal)
        self.mapeador.addMapping(self.editID,0)
        self.mapeador.addMapping(self.editTitulo, 1)
        self.mapeador.addMapping(self.editPergunta, 2)
        self.mapeador.addMapping(self.editResposta, 3)
        self.mapeador.addMapping(self.editCategoria, 4)

        self.mapeador.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        #self.tableQuestoes.connect(self.tableQuestoes.selectionModel(), SIGNAL("currentRowChanged(QModelIndex,QModelIndex)"), self.mapeador, SLOT("setCurrentModelIndex(QModelIndex)"))
        self.tableQuestoes.selectionModel().currentChanged.connect(self.on_row_changed)

    @pyqtSlot()
    def on_row_changed(self):
        index = self.tableQuestoes.currentIndex()
        self.mapeador.setCurrentModelIndex(index)
        
        

    @pyqtSlot()
    def on_actionBackup_triggered(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dirFile = QFileDialog.getExistingDirectory(self, 'Exportar para...', 'backup/',options=options)

        if (sys.platform =='win32'):
            meuzip = zipfile.ZipFile(dirFile+'\\backup_'+now+'.bak', 'w',zipfile.ZIP_DEFLATED)
            meuzip.write('data\\storage.db')
            for root, dirs, files in os.walk('files'):
                for f in files:
                    meuzip.write(os.path.join(root, f))
            meuzip.close()
            QMessageBox.information(self,u'Backup realizado com sucesso!',u'Backup realizado com sucesso!')
        else:
            meuzip = zipfile.ZipFile(dirFile+'/backup_'+now+'.bak', 'w',zipfile.ZIP_DEFLATED)
            meuzip.write('data/storage.db')
            for root, dirs, files in os.walk('files'):
                for f in files:
                    meuzip.write(os.path.join(root, f))
            meuzip.close()
            QMessageBox.information(self,u'Backup realizado com sucesso!',u'Backup realizado com sucesso!')

    @pyqtSlot()
    def on_actionRestaurar_triggered(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dirFile = QFileDialog.getOpenFileName(self, 'Importar backup...', 'backup/', 'Backup (*.bak);; All(*)',options=options)

        print(dirFile)

        try:
            
            with zipfile.ZipFile(dirFile[0]) as zf:
                zf.extractall('.')
            QMessageBox.information(self,'Restauração do Backup', 'O backup foi restaurado com sucesso!')
            self.abrirTabela('')
        except:
            QMessageBox.warning(self, 'Restauração do Backup', 'Ocorreram erros durante a restauração do backup, verifique o arquivo!')

    @pyqtSlot()
    def on_actionDoacoes_triggered(self):
        webbrowser.open('https://pagseguro.uol.com.br/checkout/v2/donation.html?currency=BRL&receiverEmail=wesleyjcr@gmail.com', new=0, autoraise=True)

    @pyqtSlot()
    def on_actionNovaQuestao_triggered(self):
        self.limparCampos()

    @pyqtSlot()
    def on_actionDeletar_Questao_triggered(self):
        if self.editID.text() =='':
            QMessageBox.warning(self, "Exclusão de questão", "Você precisa selecionar um registro para efetuar a exclusão!",QMessageBox.Ok)
        else:
            msg = QMessageBox.warning(self, "Exclusão de questão", "Tem certeza que deseja excluir essa questão?",QMessageBox.Yes|QMessageBox.No)
            if msg==QMessageBox.Yes:
                con = QSqlQuery(self.bancoDeDados)
                con.prepare("DELETE FROM QUESTAO WHERE ID = ?")
                con.addBindValue(self.editID.text())
                con.exec_()
                if (con.lastError().type() != QSqlError.NoError):
                    QMessageBox.critical(self,u'Erro na deleção',u'<b>Erro na deleção dos dados!</b>\n\nDetalhes técnicos:\n'+con.lastError().text())

                else:
                    self.abrirTabela('')
                    self.limparCampos()

    def abrirTabela(self,filtro):
        consulta = "SELECT ID AS CÓDIGO, TITULO AS TÍTULO, PERGUNTA AS PERGUNTA, RESPOSTA AS RESPOSTA, CATEGORIA AS CATEGORIA FROM QUESTAO WHERE upper(TITULO||CATEGORIA) LIKE '%"+filtro.upper()+"%' ORDER BY ID"     
        self.modelPrincipal.setQuery(QSqlQuery(consulta, self.bancoDeDados))
        self.modelPrincipal.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.tableQuestoes.setModel(self.modelPrincipal)
        self.tableQuestoes.resizeColumnsToContents()
        self.tableQuestoes.setColumnHidden(0,True)
        self.tableQuestoes.setColumnHidden(2,True)
        self.tableQuestoes.setColumnHidden(3,True)
        self.tableQuestoes.setColumnHidden(4,True)

    def limparCampos(self):
        self.editTitulo.clear()
        self.editID.clear()
        self.editPergunta.clear()
        self.editResposta.clear()
        self.editCategoria.clear()

    @pyqtSlot()
    def on_buttonSalvar_clicked(self):
        if self.editPergunta.toPlainText() =='':
            QMessageBox.warning(self,u'Atenção',u'É necessário cadastrar uma pergunta!')
        else:
            if self.editID.text()=='':
                con = QSqlQuery(self.bancoDeDados)
                con.prepare("INSERT INTO QUESTAO (TITULO,PERGUNTA, RESPOSTA, CATEGORIA) VALUES (?,?,?,?)")
                con.addBindValue(self.editTitulo.text())
                con.addBindValue(self.editPergunta.toHtml())
                con.addBindValue(self.editResposta.toHtml())
                con.addBindValue(self.editCategoria.text())
                con.exec_()

                if (con.lastError().type() != QSqlError.NoError):
                    QMessageBox.critical(self,u'Erro na inserção',u'<b>Erro na inserção dos dados!</b>\n\nDetalhes técnicos:\n'+con.lastError().text())


                else:
                    self.abrirTabela('')
                    self.limparCampos()
            else:
                con = QSqlQuery(self.bancoDeDados)
                con.prepare("UPDATE QUESTAO SET TITULO=?, PERGUNTA=?, RESPOSTA=?, CATEGORIA=? WHERE ID = ?")
                con.addBindValue(self.editTitulo.text())
                con.addBindValue(self.editPergunta.toHtml())
                con.addBindValue(self.editResposta.toHtml())
                con.addBindValue(self.editCategoria.text())
                con.addBindValue(self.editID.text())
                con.exec_()
                if (con.lastError().type() != QSqlError.NoError):
                    QMessageBox.critical(self,u'Erro na atualização',u'<b>Erro na atualização dos dados!</b>\n\nDetalhes técnicos:\n'+query.lastError().text())
                else:
                    self.abrirTabela('')
                    self.limparCampos()


    @pyqtSlot()
    def on_buttonCancelar_clicked(self):
        self.limparCampos()

    @pyqtSlot(str)
    def on_editPesquisar_textEdited(self, condicao):
        self.abrirTabela(condicao)

    @pyqtSlot()
    def on_buttonBold_clicked(self):
        if self.editPergunta.fontWeight() == QtGui.QFont.Bold:
            self.editPergunta.setFontWeight(QtGui.QFont.Normal)
            self.editPergunta.setFocus()
        else:
            self.editPergunta.setFontWeight(QtGui.QFont.Bold)
            self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonListBulleted_clicked(self):
        cursor = self.editPergunta.textCursor()
        # Insert bulleted list
        cursor.insertList(QtGui.QTextListFormat.ListDisc)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonListNumbered_clicked(self):
        cursor = self.editPergunta.textCursor()
        # Insert list with numbers
        cursor.insertList(QtGui.QTextListFormat.ListDecimal)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonItalic_clicked(self):
        state = self.editPergunta.fontItalic()
        self.editPergunta.setFontItalic(not state)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonUnderline_clicked(self):
        state = self.editPergunta.fontUnderline()
        self.editPergunta.setFontUnderline(not state)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonAlignLeft_clicked(self):
        self.editPergunta.setAlignment(Qt.AlignLeft)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonAlignRight_clicked(self):
        self.editPergunta.setAlignment(Qt.AlignRight)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonAlignCenter_clicked(self):
        self.editPergunta.setAlignment(Qt.AlignCenter)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonAlignJustify_clicked(self):
        self.editPergunta.setAlignment(Qt.AlignJustify)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonImage_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, 'Inserir imagem',".","Imagens (*.png *.xpm *.jpg *.bmp *.gif *.jpeg);; Tudo(*)",options=options)

        if filename !='':
            if (sys.platform =='win32'):
                filename = shutil.copy2(filename, 'files\\' +datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.'+filename.split('.')[1])
            else:
                filename = shutil.copy2(filename, 'files/' +datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.'+filename.split('.')[1])
            image = QImage(filename)
            if image.isNull():
                popup = QMessageBox(QMessageBox.Critical,
                                          "Erro ao carregar a imagem",
                                          "Não foi possível carregar esse arquivo!",
                                          QMessageBox.Ok,
                                          self)
                popup.show()
                self.editPergunta.setFocus()
            else:
                cursor = self.editPergunta.textCursor()
                cursor.insertImage(image.scaled(720,350,Qt.KeepAspectRatio), filename)
                self.editPergunta.setFocus()


    @pyqtSlot("QFont")
    def on_fontBox_currentFontChanged(self, text):
        self.editPergunta.setCurrentFont(text)
        self.editPergunta.setFocus()

    @pyqtSlot(str)
    def on_fontSize_activated(self, fontsize):
        self.editPergunta.setFontPointSize(int(fontsize))
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonHighlight_clicked(self):
        color = QtGui.QColorDialog.getColor()
        print(color)
        self.editPergunta.setTextBackgroundColor(color)
        self.editPergunta.setFocus()

    @pyqtSlot()
    def on_buttonFontColor_clicked(self):
        color = QtGui.QColorDialog.getColor()
        self.editPergunta.setTextColor(color)
        self.editPergunta.setFocus()

    #AQUI COMEÇA A PROGRAMAÇÃO DA FORMATAÇÃO DAS RESPOSTAS

    @pyqtSlot()
    def on_buttonBoldR_clicked(self):
        if self.editResposta.fontWeight() == QtGui.QFont.Bold:
            self.editResposta.setFontWeight(QtGui.QFont.Normal)
            self.editResposta.setFocus()
        else:
            self.editResposta.setFontWeight(QtGui.QFont.Bold)
            self.editResposta.setFocus()

    @pyqtSlot()
    def on_buttonListBulletedR_clicked(self):
        cursor = self.editResposta.textCursor()
        # Insert bulleted list
        cursor.insertList(QtGui.QTextListFormat.ListDisc)
        self.editResposta.setFocus()

    @pyqtSlot()
    def on_buttonListNumberedR_clicked(self):
        cursor = self.editResposta.textCursor()
        # Insert list with numbers
        cursor.insertList(QtGui.QTextListFormat.ListDecimal)
        self.editResposta.setFocus()

    @pyqtSlot()
    def on_buttonItalicR_clicked(self):
        state = self.editResposta.fontItalic()
        self.editResposta.setFontItalic(not state)
        self.editResposta.setFocus()

    @pyqtSlot()
    def on_buttonUnderlineR_clicked(self):
        state = self.editResposta.fontUnderline()
        self.editResposta.setFontUnderline(not state)
        self.editResposta.setFocus()

    @pyqtSlot()
    def on_buttonImageR_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, 'Inserir imagem',".","Imagens (*.png *.xpm *.jpg *.bmp *.gif *.jpeg);; Tudo(*)",options=options)

        if filename !='':
            if (sys.platform =='win32'):
                filename = shutil.copy2(filename, 'files\\' +datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.'+filename.split('.')[1])
            else:
                filename = shutil.copy2(filename, 'files/' +datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.'+filename.split('.')[1])
            # Create image object
            image = QtGui.QImage(filename)
            # Error if unloadable
            if image.isNull():
                popup = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                                          "Erro ao carregar o arquivo",
                                          "Não foi possível carregar esse arquivo!",
                                          QtGui.QMessageBox.Ok,
                                          self)
                popup.show()
                self.editResposta.setFocus()
            else:
                cursor = self.editResposta.textCursor()
                cursor.insertImage(image,filename)
                self.editResposta.setFocus()
