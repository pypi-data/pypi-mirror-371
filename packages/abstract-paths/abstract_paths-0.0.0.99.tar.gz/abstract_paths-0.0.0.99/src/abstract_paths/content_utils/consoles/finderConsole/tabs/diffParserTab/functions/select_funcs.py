from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem
from ..imports import *
def _get_selected_path_from_tree(self) -> str | None:
    it: QTreeWidgetItem | None = self.files_list.currentItem()
    if not it:
        return None
    # only accept if Apply is checked, else ignore selection
    if it.checkState(1) != Qt.CheckState.Checked:
        return None
    return it.data(0, Qt.ItemDataRole.UserRole) or it.text(0)

def _get_first_apply_checked_from_tree(self) -> str | None:
    for i in range(self.files_list.topLevelItemCount()):
        it = self.files_list.topLevelItem(i)
        if it.checkState(1) == Qt.CheckState.Checked:
            return it.data(0, Qt.ItemDataRole.UserRole) or it.text(0)
    return None

def _get_selected_path_from_list(self) -> str | None:
    sel: list[QListWidgetItem] = self.files_list.selectedItems()  # type: ignore[attr-defined]
    if sel:
        return sel[0].data(Qt.ItemDataRole.UserRole) or sel[0].text()
    # fallback to first row
    if getattr(self.files_list, "count", None) and self.files_list.count() > 0:
        it = self.files_list.item(0)  # type: ignore[attr-defined]
        return it.data(Qt.ItemDataRole.UserRole) or it.text()
    return None

def _pick_preview_target(self, files_from_filters: list[str], hunks) -> str | None:
    """
    Priority:
      A) Selected (and Apply-checked) row in QTreeWidget
      B) First Apply-checked row in QTreeWidget
      C) Selected (or first row) in QListWidget
      D) Old behavior: first file that contains the first hunk's 'subs', else ask user
    """
    # A/B/C
    if isinstance(self.files_list, QTreeWidget):
        path = self._get_selected_path_from_tree()
        if path and os.path.exists(path):
            return path
        path = self._get_first_apply_checked_from_tree()
        if path and os.path.exists(path):
            return path
    elif isinstance(self.files_list, QListWidget):
        path = self._get_selected_path_from_list()
        if path and os.path.exists(path):
            return path

    # D) fallback to your previous "match first hunk" logic
    first = next((h for h in hunks if h.subs), None)
    candidates = files_from_filters[:]
    if first and first.subs:
        _, found = getPaths(files_from_filters, first.subs)
        candidates = sorted({fp['file_path'] for fp in found}) or files_from_filters

    return self._ask_user_to_pick_file(candidates, title="Pick a file to preview")
