from ..imports import *
from .http_helpers import canonicalize_slash

def send_request(self):
        sel = self.endpoints_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, "No endpoint", "Select an endpoint row first.")
            return
        ep = self.endpoints_table.item(sel[0].row(), 0).text().strip()
        if not ep:
            QMessageBox.warning(self, "Invalid endpoint", "Empty endpoint path.")
            return

        headers = self._collect_headers()
        kv = self._collect_kv(self.body_table)
        method = self.method_box.currentText().upper()

        try:
            url = self._build_url(ep)
        except Exception as e:
            QMessageBox.warning(self, "Invalid URL", str(e))
            return

        req = QNetworkRequest(QUrl(url))
        for k, v in headers.items():
            req.setRawHeader(QByteArray(k.encode()), QByteArray(v.encode()))

        self.response_out.clear()
        label = f"{method} {url}"
        self._log(f"→ {label} | headers={headers} | params={kv}")

        # Body formatting by header
        ctype = headers.get("Content-Type", "").lower()
        body_bytes: Optional[QByteArray] = None
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            if "application/json" in ctype:
                body_bytes = QByteArray(json.dumps(kv).encode())
            elif "application/x-www-form-urlencoded" in ctype:
                body_bytes = QByteArray(urlencode(kv).encode())
            elif "text/plain" in ctype:
                body_bytes = QByteArray("\n".join(f"{k}={v}" for k, v in kv.items()).encode())
            else:
                # default to JSON if body exists without content-type
                if kv and not ctype:
                    req.setRawHeader(b"Content-Type", b"application/json")
                    body_bytes = QByteArray(json.dumps(kv).encode())

        # Dispatch
        if method == "GET":
            # For GET, append query string
            if kv:
                u = QUrl(url)
                q = u.query()
                q_extra = urlencode(kv)
                u.setQuery(q + ("&" if q else "") + q_extra)
                req.setUrl(u)
            reply = self._nam.get(req)
        elif method == "POST":
            reply = self._nam.post(req, body_bytes or QByteArray())
        elif method == "PUT":
            reply = self._nam.put(req, body_bytes or QByteArray())
        elif method == "PATCH":
            # Qt lacks native PATCH helper; use custom verb
            reply = self._nam.sendCustomRequest(req, QByteArray(b"PATCH"), body_bytes or QByteArray())
        elif method == "DELETE":
            # DELETE may carry a body; Qt supports sendCustomRequest
            if body_bytes:
                reply = self._nam.sendCustomRequest(req, QByteArray(b"DELETE"), body_bytes)
            else:
                reply = self._nam.deleteResource(req)
        else:
            QMessageBox.information(self, "Unsupported", f"Method {method} not supported.")
            return

        self._bind_common(reply, label)

def _on_send_response(self, txt: str, log_msg: str):
    try:
        self.response_output.setPlainText(txt)
        logging.info(log_msg)
    except RuntimeError as e:
        logging.error(f"_on_send_response RuntimeError: {e}")
    finally:
        self._thread = None

def _on_send_error(self, err: str):
    try:
        self.response_output.setPlainText(err)
        logging.error(err)
        QMessageBox.warning(self, "Request Error", err)
    except RuntimeError as e:
        logging.error(f"_on_send_error RuntimeError: {e}")
    finally:
        self._thread = None
