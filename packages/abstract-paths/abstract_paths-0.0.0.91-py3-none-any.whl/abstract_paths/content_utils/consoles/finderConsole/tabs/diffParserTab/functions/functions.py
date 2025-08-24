from ..imports import *

logger = logging.getLogger(__name__)

# ---------------------- Models ----------------------

@dataclass
class Hunk:
    subs: List[str] = field(default_factory=list)      # lines expected in source (without prefixes)
    adds: List[str] = field(default_factory=list)      # lines to insert (without prefixes)
    content: List[Dict[str, Any]] = field(default_factory=list)

    def is_multiline(self) -> bool:
        return len(self.subs) > 1 or len(self.adds) > 1


@dataclass
class ApplyReport:
    changed_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    hunks_applied: int = 0
    hunks_skipped: int = 0

    def extend_changed(self, path: str):
        if path not in self.changed_files:
            self.changed_files.append(path)

    def extend_skipped(self, path: str):
        if path not in self.skipped_files:
            self.skipped_files.append(path)
# Optional: convenience setter used by your functions
def set_status(self, text: str, kind: str = "info"):
    """
    kind in {"info","ok","warn","error"}
    """
    colors = {
        "info":  "#2196f3",  # blue
        "ok":    "#4caf50",  # green
        "warn":  "#ff9800",  # orange
        "error": "#f44336",  # red
    }
    self.status_label.setText(text)
    self.status_label.setStyleSheet(f"color: {colors.get(kind,'#2196f3')}; padding: 4px 0;")

# ---------------------- File I/O ----------------------

def read_any_file(file_path: str) -> str:
    """Read file content as string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        raise

def write_to_file(data: str, file_path: str):
    """Write string to file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)
    except Exception as e:
        logger.error(f"Failed to write {file_path}: {e}")
        raise

# ---------------------- Discovery ----------------------



# ---------------------- UI helpers ----------------------


def make_list(strings: Any) -> List[str]:
    if isinstance(strings, list):
        return strings
    return [strings]

def getPaths(files: List[str], strings: Any) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Find files and positions where the contiguous block 'strings' matches exactly.
    """
    strings = make_list(strings)
    tot_strings = '\n'.join(strings) if len(strings) > 1 else (strings[0] if strings else '')
    if not tot_strings:
        return [], []

    nu_files = set()
    found_paths = []
    for file_path in files:
        try:
            og_content = read_any_file(file_path)
            if tot_strings not in og_content:
                continue
            nu_files.add(file_path)
            og_lines = og_content.split('\n')
            for m in re.finditer(re.escape(tot_strings), og_content):
                start_byte = m.start()
                start_line = og_content[:start_byte].count('\n')  # 0-based
                curr = {'file_path': file_path, 'lines': []}
                for j in range(len(strings)):
                    ln = start_line + j
                    if ln >= len(og_lines):
                        break
                    curr['lines'].append({'line': ln, 'content': og_lines[ln]})
                if len(curr['lines']) == len(strings):
                    found_paths.append(curr)
        except Exception as e:
            logger.error(f"Error in getPaths for {file_path}: {e}")
    return list(nu_files), found_paths

# ---------------------- Diff parsing ----------------------

_HUNK_HEADER = re.compile(r'^@@\s*-?\d+(?:,\d+)?\s+\+?\d+(?:,\d+)?\s*@@')

def _is_header_line(s: str) -> bool:
    # lines to ignore before/among hunks
    return (
        s.startswith('diff --git ') or
        s.startswith('index ') or
        s.startswith('--- ') or
        s.startswith('+++ ')
    )

def parse_unified_diff(diff_text: str) -> List[Hunk]:
    """
    Parse a unified diff into Hunk objects.

    Rules:
      - Hunk body begins after a line like: @@ -A,B +C,D @@ (numbers optional after commas)
      - ' ' (space) lines are context: added to BOTH subs and adds (without the space)
      - '-' lines go only to subs
      - '+' lines go only to adds
      - A bare " No newline at end of file" line is ignored
      - Headers (diff --git, ---+++, index) are skipped
      - If no hunk header exists, a best-effort parser groups contiguous +/-/space lines as one hunk
    """
    lines = diff_text.splitlines()
    hunks: List[Hunk] = []
    current: Hunk | None = None
    in_hunk = False
    saw_header = False

    def flush():
        nonlocal current, in_hunk
        if current is not None and (current.subs or current.adds):
            hunks.append(current)
        current = None
        in_hunk = False

    for raw in lines:
        # normalize CRLF safely
        line = raw.rstrip('\r')

        if _HUNK_HEADER.match(line):
            saw_header = True
            flush()
            current = Hunk()
            in_hunk = True
            logger.debug("Start hunk: %s", line)
            continue

        if not in_hunk:
            # skip file headers and noise
            if _is_header_line(line) or not line.strip():
                continue
            # Best-effort: if no official header yet, but we see +/-/space, start implicit hunk
            if line.startswith((' ', '+', '-')):
                current = current or Hunk()
                in_hunk = True
            else:
                # anything else outside hunks is ignored
                continue

        # In hunk body
        if line.startswith(' '):            # context
            # include in both sides, but drop the leading space
            content = line[1:]
            current.subs.append(content)
            current.adds.append(content)
        elif line.startswith('-'):          # deletion
            current.subs.append(line[1:])
        elif line.startswith('+'):          # insertion
            current.adds.append(line[1:])
        elif line == r'\ No newline at end of file':  # ignore marker
            continue
        else:
            # unexpected body line -> end current hunk block (be tolerant)
            flush()

    # tail
    flush()
    logger.debug("Parsed %d hunk(s)", len(hunks))
    return hunks


