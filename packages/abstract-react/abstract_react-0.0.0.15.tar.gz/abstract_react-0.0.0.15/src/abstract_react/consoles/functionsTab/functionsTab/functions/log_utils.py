from ..imports import *

def append_log(self, text):
    cursor = self.log_view.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    self.log_view.setTextCursor(cursor)
    self.log_view.insertPlainText(text)
    logging.getLogger("functionsTab.ui").info(text.rstrip("\n"))
    
appendLog = append_log
