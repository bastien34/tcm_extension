import logging

# debug
# from debug import mri

from dialogs import PrefixDialog
from models import Mission

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('doc_cleaner')


ctx = XSCRIPTCONTEXT.getComponentContext()


def prefix_questions_and_answers(*args):
    dlg = PrefixDialog(context_component=ctx).dlg
    dlg.execute()
    p_question = dlg.getControl('p_question').Text
    p_answer = dlg.getControl('p_answer').Text
    dlg.dispose()
    doc = Mission(ctx)
    doc.prefix_questions_and_answers(p_question, p_answer)


def timecode_cleaner(*args):
    doc = Mission(ctx)
    doc.clean_text()


def order_question(*args):
    doc = Mission(ctx)
    doc.order_question()


def question_upper(*args):
    doc = Mission(ctx)
    doc.question_upper()


def question_lower(*args):
    doc = Mission(ctx)
    doc.question_lower()


def remove_blank_line(*args):
    doc = Mission(ctx)
    doc.remove_blank_line()


g_exportedScripts = (
    timecode_cleaner,
    order_question,
    question_upper,
    question_lower,
    remove_blank_line,
    prefix_questions_and_answers,
)
