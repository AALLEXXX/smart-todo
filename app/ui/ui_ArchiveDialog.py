# Form implementation generated from reading ui file 'app/ui/ArchiveDialog.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore
from PyQt6 import QtWidgets


class Ui_ArchiveDialog(object):
    def setupUi(self, ArchiveDialog):
        ArchiveDialog.setObjectName("ArchiveDialog")
        self.verticalLayout = QtWidgets.QVBoxLayout(ArchiveDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.archiveList = QtWidgets.QListWidget(parent=ArchiveDialog)
        self.archiveList.setObjectName("archiveList")
        self.verticalLayout.addWidget(self.archiveList)
        self.closeButton = QtWidgets.QPushButton(parent=ArchiveDialog)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout.addWidget(self.closeButton)

        self.retranslateUi(ArchiveDialog)
        QtCore.QMetaObject.connectSlotsByName(ArchiveDialog)

    def retranslateUi(self, ArchiveDialog):
        _translate = QtCore.QCoreApplication.translate
        ArchiveDialog.setWindowTitle(_translate("ArchiveDialog", "Archived Tasks"))
        self.closeButton.setText(_translate("ArchiveDialog", "Close"))
