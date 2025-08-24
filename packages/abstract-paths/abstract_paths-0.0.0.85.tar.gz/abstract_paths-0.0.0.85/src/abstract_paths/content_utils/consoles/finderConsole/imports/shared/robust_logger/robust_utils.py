import  threading, traceback, logging, os, sys,io
from logging.handlers import RotatingFileHandler
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
LOG_DIR = os.path.join(os.path.expanduser("~"), ".cache", "abstract_finder")
LOG_FILE = os.path.join(LOG_DIR, "finder.log")
print(LOG_FILE)
os.makedirs(LOG_DIR, exist_ok=True)
def get_log_file_path():
    return LOG_FILE

class QtLogEmitter(QObject):
    new_log = pyqtSignal(str)

class QtLogHandler(logging.Handler):
    def __init__(self, emitter: QtLogEmitter):
        super().__init__()
        self.emitter = emitter
    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.emitter.new_log.emit(msg + "\n")
# ---- singletons ----
_emitter: QtLogEmitter | None = None
_handler: QtLogHandler | None = None
class CompactFormatter(logging.Formatter):
    def format(self, record):
        return f"{self.formatTime(record)} [{record.levelname}] {record.getMessage()}"

def get_log_emitter() -> QtLogEmitter:
    global _emitter
    if _emitter is None:
        _emitter = QtLogEmitter()
    return _emitter
def install_qt_log_handler() -> QtLogHandler:
    global _handler
    if _handler is None:
        _handler = QtLogHandler(_emitter())
        _handler.setLevel(logging.DEBUG)
        _handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(_handler)
    return _handler

def install_qt_message_handler():
    def qt_message_handler(mode, ctx, message):
        level = {
            QtMsgType.QtDebugMsg:    logging.DEBUG,
            QtMsgType.QtInfoMsg:     logging.INFO,
            QtMsgType.QtWarningMsg:  logging.WARNING,
            QtMsgType.QtCriticalMsg: logging.ERROR,
            QtMsgType.QtFatalMsg:    logging.CRITICAL,
        }.get(mode, logging.INFO)
        logging.log(level, "Qt: %s (%s:%d)", message, ctx.file, ctx.line)
    qInstallMessageHandler(qt_message_handler)

def install_python_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    f = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    f.setLevel(logging.DEBUG)
    f.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"))
    root.addHandler(f)

    c = logging.StreamHandler(sys.stderr)
    c.setLevel(logging.INFO)
    c.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    root.addHandler(c)

    def _format_exc(exctype, value, tb):
        return "".join(traceback.format_exception(exctype, value, tb))
    def excepthook(exctype, value, tb):
        logging.critical("UNCAUGHT EXCEPTION:\n%s", _format_exc(exctype, value, tb))
    sys.excepthook = excepthook

def install_qt_logging():
    """Call once during app startup."""
    install_python_logging()
    install_qt_log_handler()
    install_qt_message_handler()
def ensure_qt_log_handler_attached() -> QtLogHandler:
    """Attach one QtLogHandler to the root logger (idempotent)."""
    global _handler
    if _handler is None:
        _handler = QtLogHandler(get_log_emitter())
        _handler.setLevel(logging.DEBUG)
        _handler.setFormatter(CompactFormatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(_handler)
    return _handler
def set_self_log(self):
    self.log = QTextEdit()
    self.log.setReadOnly(True)
    self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File: rotating, safe in long sessions
    f = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    f.setLevel(logging.DEBUG)
    f.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    ))
    logger.addHandler(f)

    # Console (stderr) for dev runs
    c = logging.StreamHandler(sys.stderr)
    c.setLevel(logging.INFO)
    c.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(c)

setup_logging()

# ---- crash handlers: keep app alive, log, and surface in GUI ----
def _format_exc(exctype, value, tb):
    return "".join(traceback.format_exception(exctype, value, tb))

def excepthook(exctype, value, tb):
    msg = _format_exc(exctype, value, tb)
    logging.critical("UNCAUGHT EXCEPTION:\n%s", msg)
    # Don't kill the app; just warn. You can emit to a Qt signal if desired.
    # (Qt will keep running.)

sys.excepthook = excepthook

def threading_excepthook(args):
    # Python 3.8+: threading.excepthook
    msg = _format_exc(args.exc_type, args.exc_value, args.exc_traceback)
    logging.critical("THREAD EXCEPTION:\n%s", msg)

setattr(threading, "excepthook", threading_excepthook)



def qt_message_handler(mode, ctx, message):
    level = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,
        QtMsgType.QtFatalMsg: logging.CRITICAL,
    }.get(mode, logging.INFO)
    logging.log(level, "Qt: %s (%s:%d)", message, ctx.file, ctx.line)

qInstallMessageHandler(qt_message_handler)

# ---------- 2) Add a log pane to any host ----------
def _lazy_attach_to(text: QPlainTextEdit, *, max_lines=2000, debounce_ms=100, tail_file: str | None = LOG_FILE):
    """Batch appends + trim; start from end (no heavy startup)."""
    install_qt_log_handler()  # ensure handler exists

    buf: list[str] = []
    timer = QTimer(text)
    timer.setInterval(debounce_ms)

    def flush():
        if not buf: return
        chunk = "".join(buf); buf.clear()
        text.appendPlainText(chunk)
        _trim(text, max_lines)

    timer.timeout.connect(flush)
    timer.start()
    text._log_batch_timer = timer

    def on_line(s: str): buf.append(s)
    _emitter().line.connect(on_line)
    text._log_conn = on_line

    if tail_file:
        # start from EOF so startup is cheap
        text._tail_pos = 0
        try:
            with open(tail_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                text._tail_pos = f.tell()
        except FileNotFoundError:
            pass
        t = QTimer(text); t.setInterval(500)
        def poll():
            try:
                with open(tail_file, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(getattr(text, "_tail_pos", 0))
                    chunk = f.read()
                    text._tail_pos = f.tell()
                if chunk: buf.append(chunk)
            except FileNotFoundError:
                pass
        t.timeout.connect(poll); t.start()
        text._tail_timer = t

def _trim(te: QPlainTextEdit, max_lines: int):
    doc = te.document()
    extra = doc.blockCount() - max_lines
    if extra <= 0: return
    cur = te.textCursor()
    cur.beginEditBlock()
    first = doc.firstBlock()
    for _ in range(extra):
        if not first.isValid(): break
        cur.setPosition(first.position())
        cur.movePosition(cur.MoveOperation.NextBlock, cur.MoveMode.KeepAnchor)
        cur.removeSelectedText()
        cur.deleteChar()
        first = first.next()
    cur.endEditBlock()

def add_logs_to(host) -> QPlainTextEdit:
    """
    - If host is QMainWindow: creates a dock named 'Logs'.
    - Else (QWidget): inserts a bottom panel with a Show/Hide button.
    Returns the QPlainTextEdit so you can attach when you want.
    """
    log = QPlainTextEdit(host)
    log.setReadOnly(True)
    log.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    log.setMinimumHeight(140)

    if isinstance(host, QMainWindow):
        dock = QDockWidget("Logs", host)
        dock.setObjectName("DockLogs")
        dock.setWidget(log)
        host.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        # start hidden by default; user can open from View > Toolbars/Docks menu if you expose it
        dock.hide()

        # Add a quick toggle button in a small bar at the bottom of central widget
        cw = host.centralWidget() or QWidget(host); host.setCentralWidget(cw)
        lay = cw.layout() or QVBoxLayout(); cw.setLayout(lay)
        bar = QWidget(cw); bl = QHBoxLayout(bar); bl.setContentsMargins(0,0,0,0)
        btn = QPushButton("Show Logs", bar)
        def toggle():
            if dock.isHidden():
                dock.show(); btn.setText("Hide Logs")
            else:
                dock.hide(); btn.setText("Show Logs")
        btn.clicked.connect(toggle)
        bl.addStretch(1); bl.addWidget(btn)
        lay.addWidget(bar)
        return log

    # Plain QWidget host
    lay = host.layout() or QVBoxLayout(host); host.setLayout(lay)
    # toolbar
    bar = QWidget(host); bl = QHBoxLayout(bar); bl.setContentsMargins(0,0,0,0)
    btn = QPushButton("Show Logs", bar)
    log.hide()
    def toggle():
        if log.isHidden():
            log.show(); btn.setText("Hide Logs")
        else:
            log.hide(); btn.setText("Show Logs")
    btn.clicked.connect(toggle)
    bl.addStretch(1); bl.addWidget(btn)
    lay.addWidget(bar)
    lay.addWidget(log)
    return log



def attach_textedit_to_logs(
    textedit: QPlainTextEdit,
    *,
    tail_file: str | None = None,
    max_lines: int = 2000,
    debounce_ms: int = 100,
    start_from_end: bool = True,     # don't slurp the whole file at startup
    initial_tail_kb: int = 64        # if we do read, cap to last N KB
):
    """
    - Batches log appends on a timer to reduce UI churn.
    - Trims to `max_lines`.
    - If tailing a file, start at EOF by default (fast startup).
    """

    ensure_qt_log_handler_attached()  # idempotent
    emitter = get_log_emitter()

    # In-memory buffer to batch UI updates
    buf: list[str] = []
    timer = QTimer(textedit)
    timer.setInterval(debounce_ms)

    def _flush():
        if not buf:
            return
        # Single append is far cheaper than per-line
        chunk = "".join(buf)
        buf.clear()
        textedit.appendPlainText(chunk)
        # Trim to max_lines (cheap for QPlainTextEdit)
        _trim_plain_text_edit(textedit, max_lines)

    timer.timeout.connect(_flush)
    timer.start()
    textedit._batch_timer = timer  # keep alive
    textedit._batch_buf = buf

    def _on_new_log(line: str):
        buf.append(line)

    # Connect live Python/Qt logs
    emitter.new_log.connect(_on_new_log)
    textedit._emitter_conn = _on_new_log  # for optional disconnect later

    # Optional file tailing — **start from end** for fast startup
    if tail_file:
        textedit._tail_pos = 0
        fpos = 0
        try:
            with io.open(tail_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                fpos = f.tell()
                if not start_from_end:
                    # read last N KB at most
                    read_from = max(0, fpos - initial_tail_kb * 1024)
                    f.seek(read_from, os.SEEK_SET)
                    chunk = f.read().decode("utf-8", errors="replace")
                    textedit.appendPlainText(chunk)
                    _trim_plain_text_edit(textedit, max_lines)
                textedit._tail_pos = fpos
        except FileNotFoundError:
            pass

        tail_timer = QTimer(textedit)
        tail_timer.setInterval(500)

        def _poll():
            try:
                with io.open(tail_file, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(getattr(textedit, "_tail_pos", 0))
                    chunk = f.read()
                    textedit._tail_pos = f.tell()
                if chunk:
                    buf.append(chunk)
            except FileNotFoundError:
                pass

        tail_timer.timeout.connect(_poll)
        tail_timer.start()
        textedit._tail_timer = tail_timer


def _trim_plain_text_edit(te: QPlainTextEdit, max_lines: int):
    doc = te.document()
    block_count = doc.blockCount()
    if block_count <= max_lines:
        return
    # Remove oldest blocks
    cursor = te.textCursor()
    cursor.beginEditBlock()
    cur = doc.firstBlock()
    lines_to_remove = block_count - max_lines
    while cur.isValid() and lines_to_remove > 0:
        nxt = cur.next()
        cursor.setPosition(cur.position())
        cursor.movePosition(cursor.MoveOperation.NextBlock, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.deleteChar()  # remove newline
        lines_to_remove -= 1
        cur = nxt
    cursor.endEditBlock()
