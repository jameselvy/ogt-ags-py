
import os
import io
from operator import itemgetter


import ogt.ogt_doc
#from ogt import ogt_group
from ogt import utils, EXAMPLES_DIR


class AGS4_DESCRIPTOR:
    """Constants defining the data descriptors (See :ref:`ags4_rule_3`)"""
    group = "GROUP"
    heading = "HEADING"
    unit = "UNIT"
    type = "TYPE"
    data = "DATA"

    @staticmethod
    def group_header():
        """List of header defined in :ref:`ags4_rule_2a`

        :return: A list of descriptions in order
        """
        return [
            AGS4_DESCRIPTOR.group,
            AGS4_DESCRIPTOR.heading,
            AGS4_DESCRIPTOR.unit,
            AGS4_DESCRIPTOR.type
        ]

    @staticmethod
    def list():
         return AGS4_DESCRIPTOR.group_header() + [AGS4_DESCRIPTOR.data]




def doc_to_ags4_csv(doc):
    """Serialize a document to :term:`ags4` format :ref:`csv`

    :param doc: The document to convert
    :type doc: ogt.ogt_doc.OGTDocument
    :rtype: tuple
    :return:

        -
        -
    """
    #out = StringIO.StringIO()
    out = io.BytesIO()
    writer = csv.writer(out,
                        delimiter=',', lineterminator='\r\n',
                        quotechar='"', quoting=csv.QUOTE_ALL)

    for group_code in doc.groups_sort():

        grp = doc.group(group_code)

        # write "GROUP"
        writer.writerow([AGS4_DESCRIPTOR.group, group_code])

        # write headings
        lst = [AGS4_DESCRIPTOR.heading]
        lst.extend(grp.headings_sort())
        writer.writerow(lst)

        # write units
        lst = [AGS4_DESCRIPTOR.unit]
        lst.extend(grp.units_list())
        writer.writerow(lst)

        # write types
        lst = [AGS4_DESCRIPTOR.type]
        lst.extend(grp.types_list())
        writer.writerow(lst)


        # write data
        for dic in grp.data:
            lst = [AGS4_DESCRIPTOR.data]
            for ki in grp.headings_sort():
                lst.append( dic[ki] )
            writer.writerow(lst)

        writer.writerow([])


    return out.getvalue(), None

def all():
    """Return everything in the ags4 data dict

    :rtype: tuple
    :return:

        - A `dict` with the data if succesful, else `None`
        - An Error message `str` if error, otherwise `None`
    """
    print "all()"
    return utils.read_json_file(AGS4_ALL_FILE)


def groups():
    """Return all :term:`GROUP` s in the ags4 data dict

    :rtype: tuple
    :return:

        - A `dict` with the data id succesful, else `None`
        - An Error message `str` if error, otherwise `None`
    """
    return utils.read_json_file(AGS4_GROUPS_FILE)

def abbrs():
    """Return all :term:`abbreviations` in the ags4 data dict

    :rtype: tuple
    :return:

        - A `dict` with the data id succesful, else `None`
        - An Error message `str` if error, otherwise `None`
    """
    return utils.read_json_file(AGS4_ABBRS_FILE)




class AGS4GroupDataDict:

    """Data dictionary of an ags :term:`GROUP`, reads the :ref:`json` definiton file"""
    def __init__(self, group_code, auto_load=True):
        """
        :param group_code: The four character group code
        :type group_code: str
        """

        self.group_code = group_code
        #self.group_description = None

        self.raw_dict = None
        self.dd_loaded = False
        if auto_load:
            self.load_def()

    def load_def(self):
        """Loads the definition file"""
        try:
            file_path = group_file_name( self.group_code )
            self.raw_dict, err = utils.read_json_file(file_path)
            self.dd_loaded = True
            return None
        except Exception as e:
            return str(e)



    def to_dict(self):
        """
        :rtype: dict
        :return: A dictionary of the definition
        """
        return self.raw_dict

    def group(self):
        """Return the group details; description, status, suggested type etc

        :rtype: dict
        :return: A dictionary of the group details
        """
        if self.raw_dict == None:
            return None
        return {key: value for key, value in self.raw_dict.items()
                if key not in ["headings", "notes"]}


    def headings_list(self):
        """Return headings list

        :return: A `list` of `dict` items
        """
        if self.raw_dict == None:
            return None

        return self.raw_dict.get("headings")

    def headings_sort(self):
        """A list of headings in correct sort order

        :rtype: a `list` of strings
        :return: A list of head_codes
        """
        if self.headings_list() == None:
            return None
        newlist = sorted(self.headings_list(), key=itemgetter('sort_order'))
        return [rec['head_code'] for rec in newlist]


    def heading(self, head_code):
        """Return data on a heading (see :term:`HEADER`)

        :type head_code: str
        :param head_code: The
        :return: a `tuple` with:

                - A **`dict`** with the heading details if found, else **`None`**
                - **`True`** if heading found, else **`False`**
        """
        headings = self.headings_list()
        if headings == None:
            return None, False

        for head in headings:
            if head['head_code'] == head_code:
                return head, True

        return None, False

    def notes(self):
        """Returns notes for this group

        :rtype: list of strings
        :return: Notes list
        """
        if self.raw_dict == None:
            return None
        return self.raw_dict.get("notes")



class Problem:
    """A container for ags validation problems and issues"""

    def __init__(self, row=None, column=None, field=None,
                 rule=None, group_code=None, head_code=None,
                 message=None, type=None, data=None):

        self.row = row
        """The row index in the csv file, ie line_no - 1"""

        self.column = column
        """The column in the source line"""

        self.field = field
        """The csv field index"""

        self.rule = rule
        """The ags rule (:ref:`ags4_rules`)"""

        self.group_code = group_code
        """The :term:`GROUP` """

        self.head_code = head_code
        """The :term:`HEADING` """

        self.message = message
        """A quick message"""

        self.data = data
        """The data message"""

    def __repr__(self):
        return "<Problem rule=%s row=%s col=%s m=%s>" % (self.rule, self.row, self.column, self.message)

def run_tests(rules):
    """Run tests on files in ags4_tests/

    :param rules: A list of test to run eg [7 8 9]. Empty = all
    :type rule: list of int's
    :rtype: tuple
    :return:

        - A list of ags errors
        - A list of system errors
    """
    ## get files
    tests_dir = os.path.join(EXAMPLES_DIR, "ags4_tests")
    files = os.listdir(tests_dir)

    files, err = utils.list_examples("ags4_tests")
    if err:
        return None, err

    summary = []
    for ags_file in files:
        #print "-----------------------"
        print "file=", ags_file
        # print "-----------------------"

        report, err = validate_ags4_file(ags_file)
        print report, err
        """
        if err:
            dic['errors'] = err
        else:
            dic['report'] = report
        """
        summary.append(report)

    s = summary_to_string(summary)
    return s, None

def summary_to_string(summary):
    #line = "=".repeat(30)
    ret = "" # "=".repeat(30)

    for sum_dic in summary:
        ret += report_to_string(sum_dic)

    return ret

def validate_ags4_file(file_path, rules=[]):

    #print "rules=", rules

    doc, err = ogt.ogt_doc.create_doc_from_ags4_file(file_path)
    contents, err = utils.read_file(file_path)
    if err:
        return None, err

    all_problems = []
    report = {}

    rule_functions =  [
            rule_1, rule_2, rule_3, rule_4, rule_5,
            rule_6, rule_7, rule_8, rule_9, rule_10,


        ]

    def call_func(report, func_to_call):
        func_name = func_to_call.__name__
        report[func_name] = {}
        report[func_name]['problems'], report[func_name]['problems'] = func_to_call(doc)


    if len(rules) > 0:
        print rule_functions
        for ru in rules:
            print ru
            call_func( report, rule_functions[ru - 1] )

    else:
        ## iterate the pointer to  functions
        for rule_func in rule_functions:

            func_name = rule_func.__name__
            report[func_name] = {}
            report[func_name]['problems'], report[func_name]['errors'] = rule_func(doc)
            all_problems.extend(report[func_name]['problems'])

    print "ALLL=", all_problems

    th = ["rule", "row", "col", "field", "data", "message"]
    trs = []
    for p in all_problems:
        #print "p=", p
        tr = []
        tr.append(p.rule if p.rule else "-")
        tr.append(p.row if p.row != None else "-")
        tr.append(p.column if p.column != None else "-")
        tr.append(p.field if p.field != None else "-")
        tr.append(p.data if p.data != None else "-")
        tr.append(p.message if p.message != None else "-")
        trs.append(tr)
    print trs
    all = dict(file_path=file_path, rules=report)

    return all, err

def report_to_string(report):
    print report
    ret = "=" * 50
    ret += "\n%s\n" % report['file_path']
    ret += "-" * 50
    ret += "\n"
    #print report

    for rule, dic in sorted(report['rules'].items()):


        if len(dic['errors']) == 0 and len(dic['problems']) == 0:
            #ret += " PASS\n"
            pass
        else:
            ret += "%s:" % rule.replace("_", " ").capitalize()
            ret += " FAIL\n"


            if len(dic['errors']):
                ret += "\tSystem Errors:\n"
                for item in dic['errors']:
                    ret += "\t\t%s\n" % item


            lp = len(dic['problems'])
            if lp:
                ret += "\tProblem: %s %s\n" % (lp, "item" if lp == 1 else "items")
                for prob in dic['problems']:
                    ret += "\t\t%s\n" % prob

    return ret

def rule_1(doc):
    """ Validate :ref:`ags4_rule_1`

    :param raw_str:
    :rtype: tuple
    :return:
        - A list of ags_errors
        - A list of sys_errors
    """
    warnings = []
    errors = []
    try:
        ## try and force to ascii in a one liner
        doc.source.decode("ascii")
        return warnings, errors

    except UnicodeDecodeError:

        #  raw_str has problem somewhere.
        # so split to lines, = line
        # and then check every char in line = column
        # if char fail, we add to errrors
        errors.append("Unicode decode error")
        for lidx, line in enumerate(doc.source.split("\n")):

            #safeS = ""
            for cidx, charlie in  enumerate(line):
                # TODO . check visible.. maybe some < 30 chard are a hacker
                if ord(charlie) < 128:
                    pass
                else:

                    warnings.append(dict(line=lidx+1, column=cidx+1, illegal=[]))
    return warnings, errors

def rule_2(doc):
    """ Validate :ref:`ags4_rule_2`

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    #report = []
    errors = []

    RULE = 2

    ## check more than one group
    if doc.groups_count() < 2:
        #report.append("Need more than one group", rule=R)
        p = Problem(message="Need more than one group")
        problems.append( p )

    ## Each data GROUP shall comprise a number of GROUP HEADER
    # TODO


    ## rows must have one or more ref DATA rows
    for group_code, grp in doc.groups.items():
        if len(grp.data) == 0:
            p = Problem(group_code=group_code, rule=RULE)
            problems.append(p)
            #report.append("group `%s` has no DATA rows" % group_code)

    ## Rule 2b - CRLF end each line
    # so we in unix.. so split source with \n and check there's a \r at end
    # can only be done with raw files
    # TODO
    l_rep = []
    if False:
        for idx, line in enumerate( doc.source.split("\n") ):
            print line
            if len(line) > 1:
                  print line[0], ord(line[-1])
            if len(line) > 1 and line[-1] != "\r":
                l_rep.append(line)
        if len(l_rep) > 0:
            #report.append("The following lines do not end with CRLF [%s]" % ", ".join(l_rep))

            p = Problem(rule=RULE)
            p.message = "Lines do not end with CRLF"
            p.data = l_rep
            problems.append(p)

    ## Rule 2c GROUP HEADER
    # loop each group, and check the headers
    l_rep = []
    for group_code, grp in doc.groups.items():

        for idx, dd in enumerate( AGS4_DESCRIPTOR.group_header()):

            if grp.csv_rows()[0] != dd:
                p = Problem(group_code=group_code, row=idx, rule=RULE)

                p.message = "GROUP_HEADER error. "
                p.message += "Incorrect order line "
                problems.append(p)
                #m += " is `%s` and should be `%s` " % (grp.csv_rows[idx][0], dd)
                #l_rep.append(m)

    if len(l_rep):
        pass #report.append(l_rep)



    return problems, errors


def rule_3(doc):
    """Validate  :ref:`ags4_rule_3`

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    #report = []
    errors = []

    descriptors = AGS4_DESCRIPTOR.list()
    ## .. TODO
    for lidx, row in enumerate(doc.csv_rows):
        if len(row) > 0:
            if row[0] not in descriptors:
                #report.append("Invalid descriptor `%s` line %s has " % (row[0], lidx+1))
                p = Problem(row=lidx)
                p.message = "Invalid descriptor"
                p.data = row[0]
                problems.append(p)

    return problems, errors


def rule_4(doc):
    """Validate  :ref:`ags4_rule_4`

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    #report = []
    errors = []


    ## The GROUP row contains only one DATA item, the GROUP name, in addition to the Data
    for idx, row in enumerate(doc.csv_rows):
        lenny = len(row)
        if lenny > 0:

            if row[0] == AGS4_DESCRIPTOR.group:
                if lenny != 2:
                    g = "?" if lenny == 1 else row[1]
                    p = Problem(group_code=g, row=idx)
                    p.message = "Group descriptor has %s items, should be one" % idx + 1
                    problems.append(p)
                    #report.append("Group descriptor `%s` at line %s  has %s items, should be one" % (g, idx + 1, lenny - 1))


    # All other rows in the GROUP have a number of DATA items defined by the HEADING row.
    header_len = -1
    for idx, row in enumerate(doc.csv_rows):
        lenny = len(row)
        if lenny == 0:
            # got a blank line
            header_len = -1

        if lenny > 0:
            if row[0] == AGS4_DESCRIPTOR.heading:
                header_len = lenny
            if row[0] == AGS4_DESCRIPTOR.data:
                if header_len != lenny:
                    p = Problem(row=idx)
                    p.message = "DATA field's dont match headers"
                    problems.append(p)
                    #report.append("DATA field's dont match headers at line %s" % (idx + 1))


    return problems, errors

def rule_5(doc):
    """Validate  :ref:`ags4_rule_5`

    .. todo:: Rule 5 validation

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    errors.append("TODO - csv double quotes")

    return problems, errors

def rule_6(doc):
    """Validate  :ref:`ags4_rule_6`

    .. todo:: Rule 6 validation

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    errors.append("TODO - comma separated")

    return problems, errors

def rule_7(doc):
    """Validate  :ref:`ags4_rule_7`

    .. todo:: Rule 7 Field ordering

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    ## HEADING s shall be in the order described in the AGS4 Data Dictionary
    for group_code, grp in doc.groups.items():

        if grp.data_dict() == None:
            print "--------"
            print group_code
            print "+++++++++"
            #ags_sort = grp.data_dict().headings_sort()

            #print grp.headings_sort
            #sss


    return problems, errors

def rule_8(doc):
    """Validate  :ref:`ags4_rule_8`

    .. todo:: Rule 8 Units

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    return problems, errors

def rule_9(doc):
    """Validate  :ref:`ags4_rule_9`

    .. todo:: Rule 9 Data Dictionary

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    return problems, errors

def rule_10(doc):
    """Validate  :ref:`ags4_rule_10`

    .. todo:: Rule 10 validation

    :param doc:
    :type doc: :class:`~ogt.ogt_doc.OGTDocument`
    :rtype: tuple
    :return:
        - a list of ags_errors
        - a list of sys errors
    """
    problems = []
    errors = []

    return problems, errors

