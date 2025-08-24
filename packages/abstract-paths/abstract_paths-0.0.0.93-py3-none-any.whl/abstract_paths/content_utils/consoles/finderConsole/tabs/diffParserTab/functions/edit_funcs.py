from ..imports import *
# ---------------------- Apply (directory) ----------------------
# ---------- In diffParserTab ----------
def get_all_files(self):
    files = []
    try:
        files = self.get_files()
    except ValueError as e:
        QMessageBox.critical(self, "Error", str(e))
        self.status_label.setText(f"Error: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        return report
    self.output.insertPlainText(f'files = {files}')
    return files
def get_hunks(self,diff_text):
    hunks = parse_unified_diff(diff_text)
    if not hunks:
        QMessageBox.warning(self, "Warning", "No valid hunks found in diff.")
        self.status_label.setText("Warning: No valid hunks found.")
        self.status_label.setStyleSheet("color: orange;")
        return report
    self.output.insertPlainText(f'hunks = {hunks}')
    return hunks
def get_all_subs(self,hunks):
    subs = []
    file_to_replacements: dict[str, list] = defaultdict(list)
    for hunk in hunks:
      
        subs.append(hunk.subs)
    self.output.insertPlainText(f'subs = {subs}')
    return subs
def get_test_diff(self):
    diff_text = """-def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
        if d:
            self.dir_in.setText(d)
    +def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
        if d:
            self.dir_in.setText(d)"""
    if diff_text == None or not diff_text or not diff_text.strip():
        QMessageBox.critical(self, "Error", "No diff provided.")
        self.status_label.setText("Error: No diff provided.")
        self.status_label.setStyleSheet("color: red;")
        return report
    diff_text = diff_text.strip()
    self.output.insertPlainText(f'diff_text = {diff_text}')
    return diff_text
def get_nufiles(self,files,subs):
    nu_files, found_paths = getPaths(files, subs)
    self.output.insertPlainText(f'nu_files = {nu_files}')
    self.output.insertPlainText(f'found_paths = {found_paths}')
    return nu_files, found_paths
def output_test(self,text):
    files = self.get_all_files()
    diff_text = self.get_test_diff()
    hunks= self.get_hunks(diff_text)
    subs = self.get_all_subs(hunks)
    nu_files, found_paths = self.get_nufiles(files,subs)

def append_log(self, text: str):
    if not hasattr(self, "log"):
        return
    c = self.log.textCursor()
    c.movePosition(c.MoveOperation.End)
    self.log.setTextCursor(c)
    self.log.insertPlainText(text)
    self.log.ensureCursorVisible()
def apply_diff_to_directory(self, diff_text: str) -> ApplyReport:
    report = ApplyReport()
    files = []
    try:
        files = self.get_files()
    except ValueError as e:
        QMessageBox.critical(self, "Error", str(e))
        self.status_label.setText(f"Error: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        return report

    if diff_text and  not diff_text.strip():
        QMessageBox.critical(self, "Error", "No diff provided.")
        self.status_label.setText("Error: No diff provided.")
        self.status_label.setStyleSheet("color: red;")
        return report
    
    hunks = parse_unified_diff(diff_text)
    if not hunks:
        QMessageBox.warning(self, "Warning", "No valid hunks found in diff.")
        self.status_label.setText("Warning: No valid hunks found.")
        self.status_label.setStyleSheet("color: orange;")
        return report

    file_to_replacements: dict[str, list] = defaultdict(list)
    for hunk in hunks:
        if not hunk.subs:
            report.hunks_skipped += 1
            logger.warning("Skipping hunk with empty subs")
            if hasattr(self, "log"):
                self.append_log("Skipping hunk with empty subs\n")
            continue

        nu_files, found_paths = getPaths(files, hunk.subs)
        hunk.content = found_paths
        any_applied = False
        for content in found_paths:
            if not content.get('lines'):
                continue
            start_line = content['lines'][0]['line']
            file_path = content['file_path']
            file_to_replacements[file_path].append({
                'start': start_line,
                'end': start_line + len(hunk.subs),
                'adds': hunk.adds.copy(),
                'subs': hunk.subs.copy()
            })
            any_applied = True

        if any_applied:
            report.hunks_applied += 1
            if hasattr(self, "log"):
                self.append_log(f"Applied hunk to {len(nu_files)} file(s)\n")
        else:
            report.hunks_skipped += 1
            if hasattr(self, "log"):
                self.append_log("No matches found for hunk\n")
    
    for file_path, repls in file_to_replacements.items():
        # Overlap detection
        sorted_repls = sorted(repls, key=lambda r: r['start'])
        overlaps = any(sorted_repls[i-1]['end'] > sorted_repls[i]['start'] for i in range(1, len(sorted_repls)))
        if overlaps:
            logger.error(f"Overlapping hunks detected in {file_path}. Skipping file.")
            if hasattr(self, "log"):
                self.append_log(f"Error: Overlapping hunks in {file_path}. Skipped.\n")
            report.extend_skipped(file_path)
            continue

        sorted_repls.reverse()

        try:
            og_content = read_any_file(file_path)
            lines = og_content.split('\n')
            for r in sorted_repls:
                if r['start'] >= len(lines) or r['end'] > len(lines):
                    logger.warning(f"Invalid line range {r['start']}:{r['end']} in {file_path}, skipping hunk")
                    if hasattr(self, "log"):
                        self.append_log(f"Warning: Invalid line range in {file_path}, skipping hunk\n")
                    continue
                if lines[r['start']:r['end']] != r['subs']:
                    logger.warning(f"Mismatch after previous applies in {file_path}, skipping hunk")
                    if hasattr(self, "log"):
                        self.append_log(f"Warning: Mismatch in {file_path}, skipping hunk\n")
                    continue
                lines = lines[:r['start']] + r['adds'] + lines[r['end']:]
            new_content = '\n'.join(lines)
            if new_content + '\n' != og_content and new_content != og_content:
                # write alongside, avoid destructive overwrite in directory mode
                write_to_file(new_content, f"{file_path}.new")
                report.extend_changed(file_path)
                if hasattr(self, "log"):
                    self.append_log(f"Patched {file_path}.new\n")
            else:
                report.extend_skipped(file_path)
                if hasattr(self, "log"):
                    self.append_log(f"No changes needed for {file_path}\n")
        except Exception as e:
            logger.error(f"Error applying to {file_path}: {e}")
            if hasattr(self, "log"):
                self.append_log(f"Error applying to {file_path}: {str(e)}\n")
            report.extend_skipped(file_path)

    self.status_label.setText(f"Applied {report.hunks_applied} hunks, skipped {report.hunks_skipped} hunks")
    self.status_label.setStyleSheet("color: green;" if report.hunks_applied > 0 else "color: orange;")
    return report
# ---------------------- Apply (single file preview) ----------------------

def _ask_user_to_pick_file(self, files: List[str], title: str = "Pick a file to preview") -> str | None:
    """
    If multiple candidate files exist, let the user choose one.
    Returns the selected path or None if cancelled.
    """
    if not files:
        return None
    if len(files) == 1:
        return files[0]
    dlg = QFileDialog(self, title, os.path.dirname(files[0]) if files else os.getcwd())
    dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
    dlg.setNameFilter("All files (*)")
    if dlg.exec():
        sel = dlg.selectedFiles()
        return sel[0] if sel else None
    return None


def preview_patch(self):
    """
    Generate a preview of applying the pasted diff to ONE file chosen from the
    current filter result (make_params). If many files match, prompt the user.
    The preview is shown in self.preview.
    """
    diff = self.diff_text.toPlainText().strip()
    print(f"diff_text == {diff}")
    if not diff:
        QMessageBox.critical(self, "Error", "No diff provided.")
        self.status_label.setText("Error: No diff provided.")
        self.status_label.setStyleSheet("color: red;")
        return

    try:
        # Use your existing filters to get the candidate universe
        files = self.get_files()
        
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to gather files: {e}")
        self.status_label.setText(f"Error: {e}")
        self.status_label.setStyleSheet("color: red;")
        return

    if not files:
        QMessageBox.warning(self, "No Files", "No files match the current filters.")
        self.status_label.setText("No files match filters.")
        self.status_label.setStyleSheet("color: orange;")
        return

    # Strategy:
    # 1) Build hunks from diff and try to find a file that actually contains the first hunk's 'subs'.
    # 2) If we find multiple, ask the user to pick one.
    hunks = parse_unified_diff(diff)
    print(hunks)
    
    nu_files, found_paths = getPaths(files=files, strings=hunk.subs)
    self._fill_files_tree(found_paths)   # populate the tree widget
    print(f"nu_files == {found_paths}")
    print(f"found_paths == {found_paths}")
    if not hunks:
        QMessageBox.warning(self, "Warning", "No valid hunks found in diff.")
        self.status_label.setText("Warning: No valid hunks found.")
        self.status_label.setStyleSheet("color: orange;")
        return

    target_file: str | None = None

    # Prefer files that contain the first hunk’s “subs” block
    first = next((h for h in hunks if h.subs), None)
    candidate_files = files[:]
    if first and first.subs:
        _, found = getPaths(files, first.subs)
        candidate_files = sorted({fp['file_path'] for fp in found}) or files
    
    # If still ambiguous, prompt
    target_file = self._pick_preview_target(files, hunks)
    if not target_file:
        self.status_label.setText("Preview cancelled.")
        self.status_label.setStyleSheet("color: orange;")
        return

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            original_lines = f.read().splitlines()

        patched = apply_custom_diff(original_lines, diff.splitlines())
        self.preview.setPlainText(patched)
        self.status_label.setText(f"Preview generated for: {target_file}")
        self.status_label.setStyleSheet("color: green;")
        self.append_log(f"Preview generated for {target_file}\n")
    except ValueError as e:
        QMessageBox.critical(self, "Error", str(e))
        self.status_label.setText(f"Error: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        self.append_log(f"Error in preview: {str(e)}\n")
    except Exception as e:
        QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {str(e)}")
        self.status_label.setText(f"Unexpected Error: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        self.append_log(f"Unexpected error in preview: {str(e)}\n")

def save_patch(self):
    """
    Save the current preview back to disk by asking the user which file to overwrite,
    defaulting to the file chosen during preview (we can re-prompt).
    """
    patched = self.preview.toPlainText()
    if not patched:
        QMessageBox.warning(self, "Warning", "No preview to save. Generate a preview first.")
        self.status_label.setText("Warning: No preview to save.")
        self.status_label.setStyleSheet("color: orange;")
        return

    # Let the user choose where to save (overwrite)
    dlg = QFileDialog(self, "Choose target file to overwrite")
    dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
    dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
    dlg.setNameFilter("All files (*)")
    if not dlg.exec():
        self.status_label.setText("Save cancelled.")
        self.status_label.setStyleSheet("color: orange;")
        return
    target = dlg.selectedFiles()[0] if dlg.selectedFiles() else None
    if not target:
        self.status_label.setText("No file chosen.")
        self.status_label.setStyleSheet("color: red;")
        return

    try:
        reply = QMessageBox.question(
            self, "Confirm Save",
            f"Overwrite this file?\n\n{target}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            self.status_label.setText("Save cancelled.")
            self.status_label.setStyleSheet("color: orange;")
            return

        with open(target, 'w', encoding='utf-8') as f:
            # ensure trailing newline like many tools do
            f.write(patched if patched.endswith('\n') else patched + '\n')

        QMessageBox.information(self, "Success", f"Saved: {target}")
        self.status_label.setText(f"Saved: {target}")
        self.status_label.setStyleSheet("color: green;")
        self.append_log(f"Saved patched file: {target}\n")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        self.status_label.setText(f"Error saving file: {str(e)}")
        self.status_label.setStyleSheet("color: red;")
        self.append_log(f"Error saving file: {str(e)}\n")

def apply_custom_diff(original_lines: List[str], diff_lines: List[str]) -> str:
    """
    Apply a simplified unified-diff (only +/- blocks) to a single file content.
    The algorithm matches exact multi-line 'subs' blocks and replaces them with 'adds'.
    """
    # Some diffs begin with a path header; if you keep that convention, skip it defensively.
    if diff_lines and '/' in diff_lines[0]:
        diff_lines = diff_lines[1:]

    hunks = parse_unified_diff('\n'.join(diff_lines))
    replacements = []
    og_content = '\n'.join(original_lines)

    for hunk in hunks:
        if not hunk.subs:
            continue
        tot_subs = '\n'.join(hunk.subs)

        for m in re.finditer(re.escape(tot_subs), og_content):
            start_byte = m.start()
            start_line = og_content[:start_byte].count('\n')
            # Verify still matches the current buffer
            if original_lines[start_line:start_line + len(hunk.subs)] == hunk.subs:
                replacements.append({
                    'start': start_line,
                    'end': start_line + len(hunk.subs),
                    'adds': hunk.adds[:]
                })

    # Overlap check
    replacements.sort(key=lambda r: r['start'])
    for i in range(1, len(replacements)):
        if replacements[i-1]['end'] > replacements[i]['start']:
            raise ValueError("Overlapping hunks detected.")

    # Apply from bottom to top
    lines = original_lines[:]
    for r in reversed(replacements):
        lines = lines[:r['start']] + r['adds'] + lines[r['end']:]
    return '\n'.join(lines)
