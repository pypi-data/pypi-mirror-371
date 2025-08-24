from ..imports import *
def _on_function_clicked(self, fn_name: str):
    self.current_fn = fn_name
    self.functionSelected.emit(fn_name)
    self._render_fn_lists_for(fn_name)

def _start_func_scan(self, scope: str):
        path = self.path_in.text().strip()
        if not path or not os.path.isdir(path):
            QMessageBox.critical(self, "Error", "Invalid project path.")
            return
        self.appendLog(f"[map] starting scan ({scope})\n")
        logging.getLogger("reactRunner.functions").info(f"scan scope={scope} path={path}")


        entries = ["index", "main"]
        self.map_worker = ImportGraphWorker(path, scope=scope, entries=entries)
        self.map_worker.log.connect(self.appendLog)
        self.map_worker.ready.connect(self._on_map_ready)
        self.map_worker.finished.connect(lambda: (self.appendLog("[map] done.\n"),
                                                 logging.getLogger("reactRunner.functions").info("scan done")))
        self.map_worker.start()
