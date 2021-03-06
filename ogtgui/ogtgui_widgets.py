# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""

import collections
import os

from Qt import QtGui, QtCore, Qt, pyqtSignal


from  . import xwidgets
from .img import Ico
from ogt import utils


class OGTSourceViewWidget( QtGui.QWidget ):
    """The SourceViewWidget info which in row 0 """

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        self.tabWidget = QtGui.QTabWidget()
        self.mainLayout.addWidget(self.tabWidget)

        # spread view
        self.tableWidget = QtGui.QTableWidget()
        self.tabWidget.addTab(self.tableWidget, "Grid View")


        self.txtBox = QtGui.QTextEdit()
        self.txtBox.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.txtBox.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.txtBox.setStyleSheet("font-family: monospace")
        self.tabWidget.addTab(self.txtBox, "Raw Text")



    def load_document(self, doco):

        #print doco
        self.txtBox.setText(doco.source)

        self.tableWidget.setRowCount(len(doco.lines))

        for ridx, row in enumerate(doco.lines):

            if self.tableWidget.columnCount() < len(row):
                self.tableWidget.setColumnCount(len(row))

            for cidx, cell in enumerate(row):
                item = QtGui.QTableWidgetItem()
                item.setText( cell )
                self.tableWidget.setItem(ridx, cidx, item)




class OGTScheduleWidget( QtGui.QWidget ):
    """The SourceViewWidget info which in row 0 """

    def __init__( self, parent=None):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)


        # spread view
        self.tableWidget = QtGui.QTableWidget()
        self.mainLayout.addWidget(self.tableWidget)




    def load_document(self, doco):




        samples = doco.group("SAMP")
        sched_group = doco.group("LBST")

        if samples == None or sched_group == None:
            return

        sched = {}
        locs = {}
        for row in sched_group.data:
            #print row
            tst = row.get('LBST_TEST')
            if not tst in sched:
                sched[tst] = dict(test=tst, samp_refs={})
                #tests.append(tst)
            loc = row.get('LOCA_ID') # + "~~" + row.get("SAMP_REF")
            if not loc in locs:
                locs[loc] = collections.OrderedDict()

            samp_ref = row.get("SAMP_REF")
            if not samp_ref in locs[loc]:
                locs[loc][samp_ref] = {}

            locs[loc][samp_ref][tst] = dict(loca_id=loc,
                                            samp_ref=samp_ref,
                                            params = row.get('LBST_METH') )

        #print sched
        tests = sorted(sched.keys())
        self.tableWidget.setColumnCount(len(tests) + 2)

        hitem = xwidgets.XTableWidgetItem()
        hitem.set("LOCA_ID", bold=True)

        self.tableWidget.setHorizontalHeaderItem(0, hitem)

        hitem = xwidgets.XTableWidgetItem()
        hitem.set("SAMP_REF", bold=True)
        f = hitem.font()
        f.setBold(True)
        hitem.setFont(f)
        self.tableWidget.setHorizontalHeaderItem(1, hitem)

        for cidx, ki in enumerate(tests):
            tst = sched[ki]
            hitem = xwidgets.XTableWidgetItem()
            hitem.set(ki, bold=True)
            self.tableWidget.setHorizontalHeaderItem(cidx + 2, hitem)

        #print locs
        for loca in sorted(locs.keys()):

            for samp_ref in locs[loca].keys():

                row_idx = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(row_idx  + 1)

                bg = "#dddddd"

                #print loca, locs[loca]
                item = xwidgets.XTableWidgetItem()
                item.set(loca, bold=True, bg=bg)
                self.tableWidget.setItem(row_idx, 0, item)

                item = xwidgets.XTableWidgetItem()
                item.set(samp_ref, bold=True, bg=bg, align=Qt.AlignCenter)
                self.tableWidget.setItem(row_idx, 1, item)

                #print locs[loca][samp_ref]
                for cidx, tst_ki in enumerate(tests):

                    item = xwidgets.XTableWidgetItem()

                    if tst_ki in locs[loca][samp_ref]:

                        tst = locs[loca][samp_ref][tst_ki]


                        item.set(tst['params'], bg="yellow", check=Qt.Checked)


                    else:
                        item.setCheckState(Qt.Unchecked)

                    self.tableWidget.setItem(row_idx, cidx + 2, item)

        # resize columns, with max_width
        col_width = 200

        self.tableWidget.resizeColumnsToContents()
        for cidx in range(0, self.tableWidget.columnCount()):
            if self.tableWidget.columnWidth(cidx) > col_width:
                self.tableWidget.setColumnWidth(cidx, col_width)


class C_EG:
    """Columns for examples"""
    file_name = 0
    file_path = 1

class ExamplesWidget( QtGui.QWidget ):

    sigLoadFile = pyqtSignal(object)

    def __init__( self, parent):
        QtGui.QWidget.__init__( self, parent )

        self.debug = False

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.tabBar = QtGui.QTabBar()
        self.mainLayout.addWidget(self.tabBar, 0)
        self.tabBar.currentChanged.connect(self.on_tab_changed)

        #=============================
        ## Set up tree
        self.tree = QtGui.QTreeWidget()
        self.mainLayout.addWidget(self.tree, 30)

        self.tree.setRootIsDecorated(False)
        self.tree.header().setStretchLastSection(True)
        self.tree.header().hide()

        hi = self.tree.headerItem()
        hi.setText(C_EG.file_path, "full path")
        hi.setText(C_EG.file_name, "Example")

        self.tree.setColumnHidden(C_EG.file_path, True)

        self.tree.itemDoubleClicked.connect(self.on_tree_double_clicked)



    def load(self):

        ## nuke any tabs existing
        self.tabBar.blockSignals(True)
        for i in range(0, self.tabBar.count()):
            self.tabBar.removeTab(i)

        dirs, err = utils.get_example_dirs()
        if err:
            # todo warn
            return


        for d in dirs:
            nidx = self.tabBar.addTab(Ico.icon(Ico.Folder), d)
            self.tabBar.setTabData(nidx, d)
        self.tabBar.blockSignals(False)

        self.on_tab_changed(0)

    def list_files(self, sub_dir):

        files_list, err = utils.list_examples( sub_dir )
        if err:
            pass #TODO
        self.tree.clear()

        for file_name in files_list:
            item = QtGui.QTreeWidgetItem()
            item.setText(C_EG.file_path, file_name)
            item.setText(C_EG.file_name, os.path.basename(file_name))
            item.setIcon(C_EG.file_name, Ico.icon(Ico.Ags4))
            f = item.font(C_EG.file_name)
            f.setBold(True)
            item.setFont(C_EG.file_name, f)
            self.tree.addTopLevelItem(item)



    def on_tree_double_clicked(self, item, col):

        file_path = str(item.text(C_EG.file_path))
        self.sigLoadFile.emit(file_path)


    def on_tab_changed(self, idx):

        sub_dir = str(self.tabBar.tabData(idx).toString())
        self.list_files(sub_dir)
