from __future__ import annotations
from abstract_gui.QT6.imports import *
from abstract_apis import *


# ─── Configuration ──────────────────────────────────────────────────────
PREDEFINED_BASE_URLS = [
    ("https://abstractendeavors.com",'api'),
    ("https://clownworld.biz",'media'),
    ("https://typicallyoutliers.com",'api'),
    ("https://thedailydialectics.com",'api')
]
def _norm_prefix(p: str) -> str:
    p = (p or "/api").strip()
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/")
PREDEFINED_HEADERS = [
    ("Content-Type", "application/json"),
    ("Accept", "application/json"),
    ("Authorization", "Bearer ")
]
MIME_TYPES_HEADERS = MIME_TYPES


# --- Optional: pull user’s helpers if present ---------------------------------
try:
    # Your project constants/utilities (if available)
    from abstract_utilities import get_logFile  # noqa
except Exception:  # pragma: no cover - safe fallback
    import logging
    def get_logFile(name: str):
        logger = logging.getLogger(name)
        if not logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S'))
            logger.addHandler(h)
            logger.setLevel(logging.INFO)
        return logger

logger = get_logFile(__name__)
# ─── Logging Handler ──────────────────────────────────────────────────────
class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        self.api_prefix = "/api" # default; will update on detect or user edit
    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        self.widget.ensureCursorVisible()



# ─── Logging Handler ──────────────────────────────────────────────────────
class BoundedCombo(QComboBox):
    def __init__(self, parent=None, *, editable=False):
        super().__init__(parent)
        self.setEditable(editable)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(0)
        # ⬇⬇⬇ fix is here
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        lv = QListView(self)
        lv.setTextElideMode(Qt.TextElideMode.ElideRight)
        lv.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setView(lv)
        
    def showPopup(self):
        QComboBox.showPopup(self)
        v = self.view()
        v.setMinimumWidth(self.width())
        v.setMaximumWidth(self.width())

class RequestWorker(QObject):
    success = pyqtSignal(str)
    failure = pyqtSignal(str)

    def __init__(self, method: str, url: str, headers: dict, params: dict, timeout: float = 15.0):
        super().__init__()
        self.method  = method
        self.url     = url
        self.headers = headers or {}
        self.params  = params or {}
        self.timeout = timeout
    def run(self):
        try:
            # Try to pass timeout; if your helpers don't accept it, fallback.
            try:
                if self.method == "GET":
                    res = getRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
                else:
                    res = postRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
            except TypeError:
                if self.method == "GET":
                    res = getRequest(url=self.url, headers=self.headers, data=self.params)
                else:
                    res = postRequest(url=self.url, headers=self.headers, data=self.params)

            txt = json.dumps(res, indent=4) if isinstance(res, (dict, list)) else str(res)
            self.success.emit(txt)
        except Exception as ex:
            self.failure.emit(f"✖ Error: {ex}")


def run_worker(worker, on_success, on_failure):
    thread = QThread()
    worker.moveToThread(thread)
    worker.response_signal.connect(on_success)
    worker.error_signal.connect(on_failure)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.started.connect(worker.run)
    thread.finished.connect(thread.deleteLater)
    thread.start()
    return thread, worker
class requestThread(QObject):
    response_signal = pyqtSignal(str, str)  # txt, log_msg
    error_signal = pyqtSignal(str)
    finished = pyqtSignal()  # Custom finished signal
    
    def __init__(self, method: str, url: str, headers: dict, params: dict, timeout: float = 12.0, is_detect: bool = False):
        super().__init__()
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.params = params or {}
        self.timeout = timeout
        self.is_detect = is_detect
    
    def run(self):
        try:
            if self.is_detect:
                candidates = [f"{self.url}/config", f"{self.url}/__config", f"{self.url}/_meta"]
                found = None
                for url in candidates:
                    try:
                        r = getRequest(url=url, headers=self.headers, timeout=self.timeout)
                        if isinstance(r, dict):
                            val = r.get("static_url_path") or r.get("api_prefix")
                            if isinstance(val, str) and val.strip():
                                found = val.strip()
                                break
                    except Exception:
                        continue
                txt = found or "/api"
                log_msg = f"API prefix detected: {txt}"
                self.response_signal.emit(txt, log_msg)
            else:
                if self.method == "GET":
                    res = getRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
                else:
                    res = postRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
                txt = json.dumps(res, indent=4) if isinstance(res, (dict, list)) else str(res)
                log_msg = f"✔ {self.method} {self.url}"
                self.response_signal.emit(txt, log_msg)
        except Exception as ex:
            self.error_signal.emit(f"✖ Error: {ex}")
        finally:
            self.finished.emit()  # Emit finished signal
