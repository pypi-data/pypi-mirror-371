from ..imports import *
def _on_function_clicked(self, fn_name: str):
    self.current_fn = fn_name
    self.functionSelected.emit(fn_name)
    self._render_fn_lists_for(fn_name)

def _start_func_scan(self, scope: str):
        try:
            path = self.path_in.text().strip()
            if not path or not os.path.isdir(path):
                QMessageBox.critical(self, "Error", "Invalid project path.")
                return
            self.appendLog(f"[map] starting scan ({scope})\n")
            logging.getLogger("reactRunner.functions").info(f"scan scope={scope} path={path}")

            # Resolve worker dynamically so missing imports don’t hard-crash the UI
            Worker = globals().get("ImportGraphWorker")
            if Worker is None:
                self.appendLog("⚠️ ImportGraphWorker not available (check imports).\n")
                logging.getLogger("reactRunner.functions").warning("ImportGraphWorker missing")
                return

            entries = ["index", "main"]
            self.map_worker = Worker(path, scope=scope, entries=entries)
            self.map_worker.log.connect(self.appendLog)
            self.map_worker.ready.connect(self._on_map_ready)
            self.map_worker.finished.connect(lambda: (self.appendLog("[map] done.\n"),
                                                     logging.getLogger("reactRunner.functions").info("scan done")))
            self.map_worker.start()
        except Exception:
            self.appendLog("start_func_scan error:\n" + traceback.format_exc() + "\n")
