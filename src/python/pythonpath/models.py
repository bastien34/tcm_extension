from com.sun.star.awt import FontWeight
from com.sun.star.beans import PropertyValue
from com.sun.star.awt.FontSlant import ITALIC
from debug import mri

QUESTION_STYLE = "Inter Q"
ANSWER_STYLE = "Inter R"


class Mission:
    def __init__(self, ctx):
        self.ctx = ctx
        self.smgr = self.ctx.ServiceManager
        self.desktop = self.smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
        self.doc = self.desktop.getCurrentComponent()
        self.text = self.doc.Text
        self._remove_blank_space_at_the_end_of_lines()
        self._apply_question_style()

    def _remove_blank_space_at_the_end_of_lines(self):
        rd = self.doc.createReplaceDescriptor()
        rd.SearchRegularExpression = True
        rd.SearchString = '\s*$'
        rd.ReplaceString = ""
        self.doc.replaceAll(rd)

    def _apply_question_style(self):
        # check if document has INTERQ style
        styles = self.doc.getStyleFamilies().getByName("ParagraphStyles")
        if not styles.hasByName(QUESTION_STYLE):
            return

        text_enum = self.text.createEnumeration()
        while text_enum.hasMoreElements():
            element = text_enum.nextElement()
            if element.supportsService("com.sun.star.text.Paragraph"):
                # element.CharWeight is not reliable. We check first & last letter
                # to determine if **element** is a question
                if element.getStart().CharWeight == FontWeight.BOLD \
                        or element.getEnd().CharWeight == FontWeight.BOLD:
                    element.ParaStyleName = QUESTION_STYLE
                else:
                    element.ParaStyleName = ANSWER_STYLE

    def prefix_questions_and_answers(self, p_question, p_answer):
        text_enum = self.text.createEnumeration()
        while text_enum.hasMoreElements():
            element = text_enum.nextElement()
            if element.supportsService("com.sun.star.text.Paragraph"):
                if element.getStart().CharWeight == FontWeight.BOLD \
                        or element.getEnd().CharWeight == FontWeight.BOLD:
                    self._prefix_str(p_question, element)
                else:
                    self._prefix_str(p_answer, element)

    def _prefix_str(self, prefix, element):
        string = element.String
        if string and not string.startswith('['):
            element.String = prefix + " : " + string

    def clean_text(self):
        # Create Regex descriptor
        rd = self.doc.createReplaceDescriptor()
        rd.SearchRegularExpression = True

        # Remove if any, milliseconds
        rd.SearchString = '(\d{2}),\d{2}\]'
        rd.ReplaceString = "$1]"
        self.doc.replaceAll(rd)

        # Replace . or blank char with ':'
        rd.SearchString = '[\(|\[]?(\d{1,2})\s?[:|.]\s?(\d{2})\s?[:|.]\s?(\d{2})[\)|\]]?'
        rd.ReplaceString = "[$1:$2:$3]"
        self.doc.replaceAll(rd)

        # Be sure hours is made of 2 chars
        rd.SearchString = '\[(\d{1}):'
        rd.ReplaceString = "[0$1:"
        self.doc.replaceAll(rd)

        rd.SearchString = '^\s?(\[\d{2}:\d{2}:\d{2}\])\s?$'
        rd.ReplaceString = "$1"
        self.doc.replaceAll(rd)

        # Remove double open bracket (ie. [INAUDIBLE [33:29:11])
        rd.SearchString = "(\[[^\]]+)\["
        rd.ReplaceString = "$1"
        self.doc.replaceAll(rd)

        # apply style to tc
        self.apply_style_to_orphan_timecode()
        self.remove_mission_ref_as_title()

    def question_upper(self):
        text_enum = self.text.createEnumeration()

        while text_enum.hasMoreElements():
            element = text_enum.nextElement()
            if element.supportsService("com.sun.star.text.Paragraph"):
                if element.ParaStyleName == QUESTION_STYLE:
                    element.String = element.String.upper()

    def question_lower(self):
        text_enum = self.text.createEnumeration()

        while text_enum.hasMoreElements():
            element = text_enum.nextElement()
            if element.supportsService("com.sun.star.text.Paragraph"):
                if element.ParaStyleName == QUESTION_STYLE and element.String:
                    q = f"{element.String[0:1].upper()}{element.String[1:].lower()}"
                    element.String = q

    def remove_blank_line(self):
        rd = self.doc.createReplaceDescriptor()
        rd.SearchRegularExpression = True
        rd.SearchString = '^$'
        rd.ReplaceString = ""
        self.doc.replaceAll(rd)

    def remove_mission_ref_as_title(self):
        rd = self.doc.createReplaceDescriptor()
        rd.SearchRegularExpression = True
        rd.SearchString = '^M\d{4}$'
        rd.ReplaceString = ""
        self.doc.replaceAll(rd)

    def apply_style_to_orphan_timecode(self):
        # method by regex
        bold = PropertyValue('CharWeight', 0, FontWeight.BOLD, 0)
        color = PropertyValue('CharColor', 0, 6710932, 0)
        rd = self.doc.createReplaceDescriptor()
        rd.SearchRegularExpression = True
        rd.SearchString = '^\s?(\[\d{2}:\d{2}:\d{2}\])\s?$'
        rd.setReplaceAttributes((bold, color))
        rd.ReplaceString = "$1"
        self.doc.replaceAll(rd)

    def order_question(self):
        """Place a incremental number before each question"""
        text_enum = self.text.createEnumeration()

        i = 0
        while text_enum.hasMoreElements():
            element = text_enum.nextElement()
            if element.supportsService("com.sun.star.text.Paragraph"):
                if element.ParaStyleName == QUESTION_STYLE:
                    element.String = f"{i} - {element.String}"
                    i += 1
