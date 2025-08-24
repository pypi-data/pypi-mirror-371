from ..imports import *
def _clear_files_tree(self):
    # Fast clear (avoids O(N) remove)
    self.files_list.clear()

def _add_file_row(self, path: str, apply_checked: bool = True, overwrite_checked: bool = False):
    it = QTreeWidgetItem(self.files_list)
    it.setText(0, path)

    # Make the item checkable & selectable
    it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

    # Per-column check state
    it.setCheckState(1, Qt.CheckState.Checked if apply_checked else Qt.CheckState.Unchecked)
    it.setCheckState(2, Qt.CheckState.Checked if overwrite_checked else Qt.CheckState.Unchecked)

    # Optional: store full path explicitly (useful if you later change column text)
    it.setData(0, Qt.ItemDataRole.UserRole, path)

def _fill_files_tree(self, files: list[str], *, default_apply=True, default_overwrite=False):
    self._clear_files_tree()
    if not files:
        return

    # Batch insert for large lists
    self.files_list.setUpdatesEnabled(False)
    for fp in files:
        self._add_file_row(fp, apply_checked=default_apply, overwrite_checked=default_overwrite)
    self.files_list.setUpdatesEnabled(True)

def _collect_checked_files(self) -> tuple[list[str], list[str]]:
    """
    Returns (apply_list, overwrite_list) based on checkboxes.
    """
    apply_list: list[str] = []
    overwrite_list: list[str] = []
    for i in range(self.files_list.topLevelItemCount()):
        it = self.files_list.topLevelItem(i)
        path = it.data(0, Qt.ItemDataRole.UserRole) or it.text(0)
        if it.checkState(1) == Qt.CheckState.Checked:
            apply_list.append(path)
        if it.checkState(2) == Qt.CheckState.Checked:
            overwrite_list.append(path)
    return apply_list, overwrite_list

def _open_file_from_row(self, item: QTreeWidgetItem, column: int):
    # double-click anywhere on the row opens the file in column 0
    path = item.data(0, Qt.ItemDataRole.UserRole) or item.text(0)
    if path and os.path.exists(path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
def get_files(self) -> list[str]:
    params = make_params(self)
    dirs, files = get_files_and_dirs(**params)
    return files
