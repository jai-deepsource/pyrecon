'''This file contains the QDialogs used in the gitTool.'''
from PySide.QtCore import *
from PySide.QtGui import *
import subprocess, os

class NewBranchDialog(QDialog): #===
    '''Dialog for creating a new branch.'''
    def __init__(self, repository):
        QDialog.__init__(self)
        self.setWindowTitle('Create New Branch')
        self.repository = repository
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
        self.exec_()
    def loadObjects(self):
        self.textLabel1 = QLabel('This will create a new branch named:')
        self.branchName = QLineEdit('<enter new branch name>')
        self.textLabel2 = QLabel('from the current state of the repository:\n'+self.repository.head.commit.hexsha)
        self.acceptBut = QPushButton('Make new branch')
        self.cancelBut = QPushButton('Cancel')
    def loadFunctions(self):
        self.acceptBut.clicked.connect( self.userAccept )
        self.cancelBut.clicked.connect( self.userReject )
    def loadLayout(self):
        info = QVBoxLayout()
        info.addWidget(self.textLabel1)
        info.addWidget(self.branchName)
        info.addWidget(self.textLabel2)
        buttons = QHBoxLayout()
        buttons.addWidget(self.cancelBut)
        buttons.addWidget(self.acceptBut)
        container = QVBoxLayout()
        container.addLayout(info)
        container.addLayout(buttons)
        self.setLayout(container)
    def userAccept(self):
        self.done(1)
    def userReject(self):
        self.done(0)

class DirtyHandler(QDialog):
    '''Class for handling a dirty repository. Display modified/untracked files and allow user to handle them via stash or clean.'''
    def __init__(self, repository):
        QDialog.__init__(self)
        self.repository = repository
        os.chdir(self.repository.working_dir) # Switch directory to repository's directory
        self.setWindowTitle('Modified Repository Handler')
        self.diff = self.repository.head.commit.diff(None)# Diff rel to working dir
        self.untracked = self.repository.untracked_files
        self.modified = [diff.a_blob.name for diff in self.diff]
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
        self.checkStatus()
        self.exec_()
    def loadObjects(self):
        self.info = QTextEdit() # Where "dirty" issues are displayed to user
        self.stashButton = QPushButton('Stash the current state')
        self.stashButton.setToolTip('This will save the current state into the stash, which can be retrieved at a later time.')
        self.cleanButton = QPushButton('Discard the current state')
        self.cleanButton.setToolTip('This will revert the current state into the most recent commit. Data can NOT be retrieved.')
        self.cancelButton = QPushButton('Cancel')
    def loadFunctions(self):
        self.stashButton.clicked.connect( self.stash )
        self.cleanButton.clicked.connect( self.clean )
    def loadLayout(self):
        container = QVBoxLayout()
        container.addWidget(self.info)
        container.addWidget(self.stashButton)
        if len(self.untracked) > 0:
            container.addWidget(self.cleanButton)
        self.setLayout(container)
    def stash(self): #===
        '''Stash the current state, including untracked files'''
        cmdList = ['git', 'stash', 'save', '-u']
        rets = subprocess.check_output( cmdList )
        self.done(1)
    def clean(self):
        '''Remove modified/untracked files'''
        cmdList = ['git', 'clean', '-fn']
        rets = subprocess.check_output( cmdList )
        confirm = QMessageBox()
        confirm.setText('The following changes will be made, are you sure?')
        print rets #===
        confirm.setInformativeText(str(rets))
        confirm.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = confirm.exec_()
        if ret == QMessageBox.Ok:
            rets = subprocess.check_output( ['git','clean','-f'] )
            print rets
        else:
            print 'Changes were not made.'
            return
        self.done(1)
    def checkStatus(self):
        if (len(self.modified) > 0 and
            len(self.untracked) == 0):
            text = 'Files in the repository have been modified:\n'
            text = text+'\n'.join(['\t'+str(mod) for mod in self.modified])
            self.info.setText(text)
        elif (len(self.untracked) > 0):
            text=''
            if len(self.modified) > 0:
                text = 'Files have been modified:\n.'
                text = text+'\n'.join(['\t'+str(mod) for mod in self.modified])
            text = text+'\nUntracked files present:\n'
            text = text+'\n'.join(['\t'+str(uFile) for uFile in self.untracked])
            self.info.setText(text)

class InvalidRepoHandler(QDialog):
    def __init__(self, path):
        QDialog.__init__(self)
        self.path = path
        os.chdir(self.path)
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
        self.exec_()
    def loadObjects(self):
        self.info1 = QTextEdit()
        self.info1.setText(str(self.path)+' is an invalid Git repository. Would you like to initialize it as a git repository?')
        self.yes = QPushButton('Yes, initialize repository')
        self.no = QPushButton('No, quit the gitTool')
    def loadFunctions(self):
        self.yes.clicked.connect( self.clickYes )
        self.no.clicked.connect( self.clickNo )
    def loadLayout(self):
        container = QVBoxLayout()
        container.addWidget(self.info1)
        buttons = QHBoxLayout()
        buttons.addWidget(self.yes)
        buttons.addWidget(self.no)
        container.addLayout(buttons)
        self.setLayout(container)
    def clickYes(self):
        rets = subprocess.check_output(['git','init'])
        print rets
        #=== need to setup remote repository
        self.done(1)
    def clickNo(self):
        self.done(0)