# -*- coding: utf-8 -*-
"""
@author: Peter Morgan <pete@daffodil.uk.com>
"""
from Qt import QtGui, QtCore, Qt, pyqtSignal

from .img  import Ico


import ogt.ags4

import app_globals as G

from . import xobjects

class AGS_TYPE:
    abbrev = "ABBR"
    abbrev_item = "ABBR_ITEM"
    group = "GROUP"
    heading = "HEAD"
    note = "NOTE"


class AGS_COLORS:
    group = "#286225"
    abbrev = "#496FA3"


SHOW_NONE = "#__NONE__#"

def type_ico(ags_type):

    v = ags_type.upper()


    if v in ["DT"]: # Date time
        return Ico.TypeDate

    if v.endswith("DP"): # n decimal places
        return  Ico.TypeDecimal

    if v == "ID": # UID
        return  Ico.TypeID

    if v in ["PA", "PU", "PT"]: # Picklists
        return  Ico.TypePicklist

    if v.endswith("SCI"):  # n + Scientific
        return  Ico.TypeSci

    if v == "YN": # Boolean yes/no
        return  Ico.TypeCheckBox

    if v in ["X"]: # text
        return  Ico.TypeText

    return Ico.TypeUnknown

def type_icon(ags_type):
    return type_ico(ags_type)
##===================================================================
## Main
##===================================================================
class AgsObject(QtCore.QObject):

    sigLoaded = pyqtSignal()

    def __init__( self, parent=None):
        super(QtCore.QObject, self).__init__(parent)

        self.modelNotes = NotesModel()
        self.modelUnits = UnitsModel(self)


        self.modelClasses = ClassesModel(self)
        self.modelGroups = GroupsModel(self)
        self.modelHeadings = HeadingsModel(self)

        #self.modelAbbrevClasses = ClassesModel(self)
        #self.modelAbbrevs = AbbrevsModel(self)

        self.modelAbbrItems = AbbrevItemsModel(self)

        self.modelGroups.sigClasses.connect(self.modelClasses.load_classes)

        #self.connect(self.modelAbbrevs, QtCore.SIGNAL("classes"), self.modelAbbrevClasses.load_classes)


    def load(self):

        all, err = ogt.ags4.all()
        print err
        print "all=", all.keys()

        self.modelAbbrItems.load_data(all['abbrs'])

        groups, err = ogt.ags4.groups()
        #print groups.keys()





        self.modelGroups.load_data(groups)

        self.modelNotes.init_words()



        self.sigLoaded.emit()



    def get_group(self, code):
        return self.modelGroups.get_group(code)

    def deadget_abbrev(self, head_code):
        return self.modelAbbrevItems.get_abbrev(head_code)

    def has_abbrev(self, head_code):
        """Check `head_code` exists


        :param head_code:

        """
        return self.modelAbbrevItems.has_abbrev(head_code)
#
    def get_words(self):
        return self.modelNotes.get_words()

    def get_notes(self, group_code):
        return self.modelNotes.get_notes(group_code)

    def get_heading(self, head_code):
        return self.modelHeadings.get_heading(head_code)

    def get_picklist(self, abbrev):

        #print self.modelAbbrevItems.get_picklist(abbrev)
        return self.modelAbbrevItems.get_picklist(abbrev)
        """
        if not abbrev in self._abbrevs:
            return None
        vals = self._abbrevs[abbrev]['vals']
        dic = {}
        for v in vals:
            dic[v['val_code']] = v
        return [ dic[k] for k in sorted( dic.keys() ) ]

        return None
        """
class NotesModel():

    def __init__(self):
        self.d = {}
        self.words = {}

    def append_notes(self, group_code, recs):

        self.d[group_code] = recs


    def add_words(self, rows):

        for rec in rows:
            if rec['code'] in self.words:
                pass #print "panic", rec, self.words[rec['code']]
            else:
                self.words[rec['code']] = rec


    def init_words(self):

        self.words = {}
        print "TODO words", self
        #self.add_words( G.Ags.modelAbbrevs.get_words() )
        self.add_words( G.Ags.modelGroups.get_words() )
        self.add_words( G.Ags.modelHeadings.get_words() )
        #print self.words

    def get_words(self):
        return self.words

    def get_notes(self, group_code):
        return self.d.get(group_code)

##===================================================================
## Groupss
##===================================================================
class CG:
    code = 0
    description = 1
    cls = 2
    search = 3
    x_id = 4



class GroupsModel(xobjects.XStandardItemModel):

    sigClasses = pyqtSignal(list)

    def __init__( self, parent=None):
        xobjects.XStandardItemModel.__init__( self, parent)


        self.set_header(CG.code, "Group")
        self.set_header(CG.description, "Description")
        self.set_header(CG.cls, "Class")
        #self.set_header(CG.x_id, "xid")
        self.set_header(CG.search, "Search")


    def load_data(self, groups):

        classes = []


        for group_code in groups.keys():
            rec = groups[group_code]
            items = self.make_blank_row()

            items[CG.code].set(rec['group_code'], bold=True, ico=Ico.AgsGroup, font="monospace")
            items[CG.description].set(rec['group_description'])
            items[CG.search].set( rec['group_code'] + rec['group_description'] )
            items[CG.cls].set(rec['class'])
            self.appendRow(items)

            if not rec['class'] in classes:
                classes.append(rec['class'])

            G.Ags.modelHeadings.append_headings(rec)
            G.Ags.modelNotes.append_notes(group_code, rec['notes'])


        self.sigClasses.emit(classes)

    def get_group(self, code):
        items = self.findItems(code, Qt.MatchExactly, CG.code)
        #print "GET+", code
        ridx = items[0].index().row()
        return dict(	group_code=self.item(ridx, CG.code).s(),
                        group_description=self.item(ridx, CG.description).s(),
                        cls=self.item(ridx, CG.cls).s())

    def get_words(self):

        lst = []
        for ridx in range(0, self.rowCount()):
            lst.append( dict(type=AGS_TYPE.group, description=self.item(ridx, CG.description).s(),
                            code=self.item(ridx, CG.code).s()))
        return lst

##===================================================================
## Abbrecs
##===================================================================
class deadAbbrevsModel(xobjects.XStandardItemModel):



    def __init__( self, parent=None):
        super(xobjects.XStandardItemModel, self).__init__(parent)

        #header_labels = ['Code', "Description", "Group", "abbrev_id"]
        self.set_header(CG.code, "Code")
        self.set_header(CG.description, "Description")
        self.set_header(CG.cls, "Group")
        self.set_header(CG.search, "Search")
        self.set_header(CG.x_id, "ID")

    def load_data(self, data):

        for head_code in data.keys():

            #self.removeRows(0, self.rowCount())
            #classes = []
            for rec in data[head_code]['abbreviations']:
                print rec
                #rec = data['abbrevs'][ki]
                code = rec['abbr_code']
                items = self.get_abbrev_row(code)
                if items == None:
                    items = self.make_blank_row()
                    items[CG.code].set(code, bold=True, ico=Ico.AgsAbbrev)
                    self.appendRow(items)
                items[CG.description].set(rec['abbr_desc'])
                items[CG.search].set(code + rec['abbr_desc'])
                #items[CG.cls].set(rec['grp'])
                #items[CG.x_id].set(rec['abbrev_id'])


                #if not rec['grp'] in classes:
                #    classes.append(rec['grp'])

                #G.Ags.modelAbbrevItems.append_abbrev_items(ki, rec['items'])

            #self.emit(QtCore.SIGNAL("classes"), classes)

    def get_abbrev_row(self, code):
        items = self.findItems(code, Qt.MatchExactly, CG.code)
        if len(items) == 0:
            return None
        #ridx = items[0].index().row()
        return self.get_items_from_item(items[0])

    def get_abbrev(self, code):
        items = self.findItems(code, Qt.MatchExactly, CG.code)
        if len(items) == 0:
            return None
        #print "GET+", code, items
        ridx = items[0].index().row()
        return dict(	abbrev_code=self.item(ridx, CG.code).s(),
                        description=self.item(ridx, CG.description).s(),
                        cls=self.item(ridx, CG.cls).s())


    def get_words(self):

        lst = []
        for ridx in range(0, self.rowCount()):
            lst.append( dict(type=AGS_TYPE.abbrev, description=self.item(ridx, CG.description).s(),
                            code=self.item(ridx, CG.code).s()))
        return lst

##===================================================================
## headings
##===================================================================
class CH:
    """Columns NO's for the ;class:`~ogtgui.ags_models.HeadingsModel`"""
    head_code = 0
    status = 1
    unit = 2
    data_type = 3

    description = 4
    example = 5
    sort = 6
    group_code = 7
    group_descr = 8
    class_ = 9


class HeadingsModel(xobjects.XStandardItemModel):
    def __init__( self, parent=None):
        super(xobjects.XStandardItemModel, self).__init__(parent)

        self.set_header(CH.head_code, "Heading")
        self.set_header(CH.description, "Description")
        self.set_header(CH.data_type, "Type")
        self.set_header(CH.unit, "Unit")
        self.set_header(CH.status, "Stat")
        #hi.setTextAlignment(C.unit, QtCore.Qt.AlignHCenter)

        self.set_header(CH.example, "Example")
        self.set_header(CH.sort, "Srt")
        self.set_header(CH.group_code, "Group")
        self.set_header(CH.group_descr, "Group Description")
        self.set_header(CH.class_, "Class")

    def append_headings(self, grp):


        for rec in grp['headings']:

            ico = type_ico(rec['suggested_type'])

            items = self.make_blank_row()
            items[CH.head_code].set(rec['head_code'], ico=ico, bold=True, font="monospace")

            items[CH.data_type].set(rec['suggested_type'])
            items[CH.unit].set( rec['suggested_unit'])
            items[CH.description].set( rec['head_description'])
            items[CH.sort].set(rec['sort_order'])
            items[CH.example].set(rec['example'])

            items[CH.group_code].set(grp['group_code'])
            items[CH.group_descr].set(grp['group_description'])
            items[CH.class_].set(grp['class'])

            self.appendRow(items)


    def get_words(self):

        lst = []
        for ridx in range(0, self.rowCount()):
            lst.append( dict(type=AGS_TYPE.heading, description=self.item(ridx, CH.description).s(),
                            code=self.item(ridx, CH.head_code).s()))
        return lst

    def get_heading(self, code):
        items = self.findItems(code, Qt.MatchExactly, CH.head_code)
        if len(items) == 0:
            return None
        #print "GET+", code, items
        ridx = items[0].index().row()
        return dict(	head_code=self.item(ridx, CH.head_code).s(),
                        head_description=self.item(ridx, CH.description).s(),
                        group_code=self.item(ridx, CH.group_code).s(),
                        #group_code=self.item(ridx, CH.group_code).s(),
                        data_type=self.item(ridx, CH.data_type).s())

##===================================================================
## Abbrev Values
##===================================================================

class CA:
    """Columns no's for the :class:`~ogtgui.ags4_models.AbbrevItemsModel` """
    code = 0
    description = 1
    head_code = 2



class AbbrevItemsModel(xobjects.XStandardItemModel):
    def __init__( self, parent=None):
        super(xobjects.XStandardItemModel, self).__init__(parent)

        self.set_header(CA.code, "Code")
        self.set_header(CA.description, "Description")
        self.set_header(CA.head_code, "head_code")


    def load_data(self, data):
        print self, data.keys()
        for head_code, recs in data.iteritems():
            print head_code, recs
            self.append_abbrv_items(head_code, data[head_code]['abbrs'])

    def append_abbrv_items(self, head_code, recs):


        for rec in recs:
            #items = self.get_item_row(rec['item_id'])
            #if items == None:
            #print rec
            items = self.make_blank_row()
            #items[CI.item_id].set(rec['item_id'])

            items[CA.code].set(rec['code'], ico=Ico.AgsAbbrevItem, bold=True, font="monospace")
            items[CA.description].set(rec['description'])
            items[CA.head_code].set(head_code)
            self.appendRow(items)

    def has_abbrev(self, head_code):
            return len(  self.findItems(head_code, Qt.MatchExactly, CA.head_code) ) > 0

    def deadget_item_row(self, item_id):
        items = self.findItems(str(item_id), Qt.MatchExactly, CA.item_id)
        if len(items) == 0:
            return None
        #ridx = items[0].index().row()
        return self.get_items_from_item(items[0])

    def get_picklist(self, abbrev_code):
        lst = []
        items = self.findItems(abbrev_code, Qt.MatchExactly, CA.code)
        for item in items:
            row = self.get_items_from_item(item)

            lst.append( dict(	item_code = row[CA.item_code].s(),
                                item_description = row[CA.item_description].s()
                                ))

        return lst

    def get_row(self, item):
        return self.get_row_from_item(item)

##===================================================================
## Classes
##===================================================================
class ClassesModel(xobjects.XStandardItemModel):

    sigLoaded = pyqtSignal()

    def __init__( self, parent=None):
        super(xobjects.XStandardItemModel, self).__init__(parent)

        self.set_header(0, "Class")

        self.make_root()

    def make_root(self):

        items = self.make_blank_row()
        items[0].set("All", ico=Ico.Folder)
        self.appendRow(items)

        return items

    def load_classes(self, classes):

        rootItem = self.item(0, 0)
        for r in classes:
            citems = self.make_blank_row()
            citems[0].set(r)
            rootItem.appendRow(citems)

        self.sigLoaded.emit()


##===================================================================
## Classes
##===================================================================

class CU:
    unit = 0
    description = 1

class UnitsModel(xobjects.XStandardItemModel):
    def __init__( self, parent=None):
        super(xobjects.XStandardItemModel, self).__init__(parent)

        self.set_header(CU.unit, "Unit")
        self.set_header(CU.description, "Description")


    def load_data(self, data):

        recs = data['units']

        for rec in recs:
            items = self.make_blank_row()
            items[CU.unit].set(rec['unit'], bold=True, font="monospace")
            items[CU.description].set(rec['description'])
            self.appendRow(items)


        self.emit(QtCore.SIGNAL("loaded"))
