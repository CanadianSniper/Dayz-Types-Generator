"""
DayZ Types.xml Generator GUI

A simple desktop app to create and manage DayZ `types.xml` loot configuration.
- Load an existing `types.xml` (vanilla or custom)
- Add/Edit/Delete type entries
- Manage flags, category, usage/value/tag lists
- Export a clean, pretty-printed `types.xml`

Requirements
------------
- Python 3.9+
- PySide6 (`pip install PySide6`)

Run:
    python types_generator.py

Notes
-----
- The editor supports multiple `usage`, `value`, and `tag` entries per type.
- Numeric fields accept integers; blanks are treated as omitted (the element won't be emitted).
- Flags are exposed as checkboxes and saved as `0` or `1` attributes.
- On export, the tool writes only the fields you set.

"""
from __future__ import annotations
import sys
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QSpinBox,
    QCheckBox, QPushButton, QListWidget, QListWidgetItem, QComboBox, QGroupBox,
    QSplitter
)



# ----------------------------- Theme / Styling ----------------------------- #
from PySide6.QtGui import QPalette, QColor

DARK_QSS = """
* { font-size: 12px; }
QWidget { background-color: #121212; color: #E6E6E6; }
QLineEdit, QComboBox, QListWidget, QSpinBox {
    background-color: #1E1E1E;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 6px;
}
QListWidget::item { padding: 6px; margin: 2px; }
QPushButton {
    background-color: #2A2F3A;
    border: 1px solid #3A3F4A;
    border-radius: 10px;
    padding: 8px 12px;
}
QPushButton:hover { background-color: #343A46; }
QPushButton:pressed { background-color: #2A303B; }
QGroupBox {
    border: 1px solid #2A2A2A;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #B0B6BF;
}
QSplitter::handle {
    background: #2A2A2A;
    width: 6px;
    margin: 0 2px;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #2F2F2F;
    min-height: 24px;
}
"""

LIGHT_QSS = """
* { font-size: 12px; }
QWidget { background-color: #FFFFFF; color: #1C1C1C; }
QLineEdit, QComboBox, QListWidget, QSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #D9D9D9;
    border-radius: 8px;
    padding: 6px;
}
QPushButton {
    background-color: #F3F3F5;
    border: 1px solid #E2E2E6;
    border-radius: 10px;
    padding: 8px 12px;
}
QPushButton:hover { background-color: #ECECEF; }
QPushButton:pressed { background-color: #E4E4E8; }
QGroupBox {
    border: 1px solid #E6E6E6;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #6C6C73;
}
QSplitter::handle {
    background: #E6E6E6;
    width: 6px;
    margin: 0 2px;
}
"""

def apply_dark_palette(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18,18,18))
    palette.setColor(QPalette.WindowText, QColor(230,230,230))
    palette.setColor(QPalette.Base, QColor(30,30,30))
    palette.setColor(QPalette.AlternateBase, QColor(24,24,24))
    palette.setColor(QPalette.ToolTipBase, QColor(255,255,220))
    palette.setColor(QPalette.ToolTipText, QColor(0,0,0))
    palette.setColor(QPalette.Text, QColor(230,230,230))
    palette.setColor(QPalette.Button, QColor(42,47,58))
    palette.setColor(QPalette.ButtonText, QColor(230,230,230))
    palette.setColor(QPalette.BrightText, QColor(255,0,0))
    palette.setColor(QPalette.Highlight, QColor(64,128,255))
    palette.setColor(QPalette.HighlightedText, QColor(0,0,0))
    app.setPalette(palette)
    app.setStyleSheet(DARK_QSS)

def apply_light_palette(app):
    app.setStyle("Fusion")
    app.setPalette(QPalette())  # reset to default
    app.setStyleSheet(LIGHT_QSS)
# ---- Preset dropdown options ----
CATEGORY_PRESETS = [
    "weapons","food","tools","clothes","books","containers","explosives","lootdispatch"
]
USAGE_PRESETS = [
    "coast","farm","firefighter","hunting","industrial","medic","military",
    "office","police","prison","school","town","village","lunapark",
    "seasonalevent","contaminated area"
]
VALUE_PRESETS = ["Tier1","Tier2","Tier3","Tier4"]
TAG_PRESETS = ["none","shelves","floor","ground"]

# ----------------------------- Data Model ----------------------------- #

@dataclass
class TypeEntry:
    name: str
    nominal: Optional[int] = None
    lifetime: Optional[int] = None
    restock: Optional[int] = None
    min: Optional[int] = None
    quantmin: Optional[int] = None
    quantmax: Optional[int] = None
    cost: Optional[int] = None
    # flags attributes
    flags: Dict[str, int] = field(default_factory=lambda: {
        "count_in_cargo": 0,
        "count_in_hoarder": 0,
        "count_in_map": 1,
        "count_in_player": 0,
        "crafted": 0,
        "deloot": 0,
    })
    category: Optional[str] = None
    usages: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def from_xml(elem: ET.Element) -> "TypeEntry":
        name = elem.get("name", "")
        def get_int(tag: str) -> Optional[int]:
            t = elem.find(tag)
            if t is not None and (t.text or "").strip() != "":
                try:
                    return int(t.text.strip())
                except ValueError:
                    return None
            return None
        entry = TypeEntry(
            name=name,
            nominal=get_int("nominal"),
            lifetime=get_int("lifetime"),
            restock=get_int("restock"),
            min=get_int("min"),
            quantmin=get_int("quantmin"),
            quantmax=get_int("quantmax"),
            cost=get_int("cost"),
        )
        # flags
        flags_elem = elem.find("flags")
        if flags_elem is not None:
            for k in entry.flags.keys():
                v = flags_elem.get(k)
                if v is not None:
                    try:
                        entry.flags[k] = int(v)
                    except ValueError:
                        pass
        # category
        cat_elem = elem.find("category")
        if cat_elem is not None:
            entry.category = cat_elem.get("name")
        # usages/values/tags (multiple)
        entry.usages = [u.get("name") for u in elem.findall("usage") if u.get("name")]
        entry.values = [v.get("name") for v in elem.findall("value") if v.get("name")]
        entry.tags = [t.get("name") for t in elem.findall("tag") if t.get("name")]
        return entry

    def to_xml(self) -> ET.Element:
        t = ET.Element("type", name=self.name)
        def put_int(tag: str, val: Optional[int]):
            if val is not None:
                e = ET.SubElement(t, tag)
                e.text = str(val)
        put_int("nominal", self.nominal)
        put_int("lifetime", self.lifetime)
        put_int("restock", self.restock)
        put_int("min", self.min)
        put_int("quantmin", self.quantmin)
        put_int("quantmax", self.quantmax)
        put_int("cost", self.cost)
        # flags
        if any(int(v) != 0 for v in self.flags.values()) or True:
            f = ET.SubElement(t, "flags")
            for k, v in self.flags.items():
                f.set(k, str(int(v)))
        # category
        if self.category:
            c = ET.SubElement(t, "category")
            c.set("name", self.category)
        # usages/values/tags
        for u in self.usages:
            ue = ET.SubElement(t, "usage")
            ue.set("name", u)
        for v in self.values:
            ve = ET.SubElement(t, "value")
            ve.set("name", v)
        for tg in self.tags:
            te = ET.SubElement(t, "tag")
            te.set("name", tg)
        return t

# ----------------------------- Utilities ----------------------------- #

def prettify(elem: ET.Element) -> str:
    """Return pretty-printed XML string (without external deps)."""
    rough = ET.tostring(elem, encoding="utf-8")
    try:
        import xml.dom.minidom as minidom
        reparsed = minidom.parseString(rough)
        return reparsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")
    except Exception:
        return rough.decode("utf-8")

# ----------------------------- GUI Widgets ----------------------------- #


class ListEditor(QWidget):
    """Generic list editor (Add/Remove) for usages/values/tags with optional presets dropdown."""
    def __init__(self, label: str, presets: list[str] | None = None):
        super().__init__()
        self.list = QListWidget()

        # Optional preset dropdown + Add button
        self.preset = None
        hl_top = QHBoxLayout()
        if presets:
            self.preset = QComboBox()
            self.preset.setEditable(False)
            self.preset.addItems(presets)
            self.add_preset_btn = QPushButton(f"Add {label}")
            self.add_preset_btn.clicked.connect(self.add_from_preset)
            hl_top.addWidget(self.preset)
            hl_top.addWidget(self.add_preset_btn)

        # Manual entry (kept for flexibility)
        self.input = QLineEdit()
        self.add_btn = QPushButton(f"Add {label} (manual)")
        self.add_btn.clicked.connect(self.add_item)

        self.rm_btn = QPushButton("Remove Selected")
        self.rm_btn.clicked.connect(self.remove_selected)

        layout = QVBoxLayout(self)
        if presets:
            layout.addLayout(hl_top)

        hl = QHBoxLayout()
        hl.addWidget(self.input)
        hl.addWidget(self.add_btn)
        layout.addLayout(hl)

        layout.addWidget(self.list)
        layout.addWidget(self.rm_btn)

    def set_items(self, items: list[str]):
        self.list.clear()
        for i in items:
            self.list.addItem(i)

    def get_items(self) -> list[str]:
        return [self.list.item(i).text() for i in range(self.list.count())]

    def _add_text(self, text: str):
        text = text.strip()
        if text:
            existing = set(self.get_items())
            if text not in existing:
                self.list.addItem(text)

    def add_item(self):
        self._add_text(self.input.text())
        self.input.clear()

    def add_from_preset(self):
        if self.preset:
            self._add_text(self.preset.currentText())

    def remove_selected(self):
        for it in self.list.selectedItems():
            self.list.takeItem(self.list.row(it))
class TypeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.current: Optional[TypeEntry] = None

        form = QFormLayout()
        # Preset selector (auto-fills the form from loaded types.xml presets)
        self.preset_combo = QComboBox(); self.preset_combo.setEditable(False)
        self.preset_combo.addItem("— choose preset —")
        form.addRow("Preset", self.preset_combo)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)

        self.presets: Dict[str, TypeEntry] = {}

        self.name = QLineEdit()
        self.nominal = QSpinBox(); self.nominal.setRange(-1, 10_000)
        self.lifetime = QSpinBox(); self.lifetime.setRange(-1, 1_000_000)
        self.restock = QSpinBox(); self.restock.setRange(-1, 1_000_000)
        self.min = QSpinBox(); self.min.setRange(0, 10_000)
        self.quantmin = QSpinBox(); self.quantmin.setRange(-1, 100_000)
        self.quantmax = QSpinBox(); self.quantmax.setRange(-1, 100_000)
        self.cost = QSpinBox(); self.cost.setRange(0, 1_000_000)
        for sb in (self.nominal, self.lifetime, self.restock, self.min, self.quantmin, self.quantmax, self.cost):
            sb.setSpecialValueText("")  # blanks when at minimum if appropriate

        form.addRow("Name", self.name)
        form.addRow("Nominal", self.nominal)
        form.addRow("Lifetime", self.lifetime)
        form.addRow("Restock", self.restock)
        form.addRow("Min", self.min)
        form.addRow("Quant Min", self.quantmin)
        form.addRow("Quant Max", self.quantmax)
        form.addRow("Cost", self.cost)

        # Flags box
        flags_box = QGroupBox("Flags")
        fl = QHBoxLayout(flags_box)
        self.flag_checks: Dict[str, QCheckBox] = {}
        for key in [
            "count_in_cargo","count_in_hoarder","count_in_map",
            "count_in_player","crafted","deloot"
        ]:
            cb = QCheckBox(key)
            self.flag_checks[key] = cb
            fl.addWidget(cb)
        fl.addStretch(1)

        # Category + list editors
        cat_row = QHBoxLayout()
        self.category = QComboBox(); self.category.setEditable(True)
        self.category.addItems(CATEGORY_PRESETS)
        cat_row.addWidget(QLabel("Category"))
        cat_row.addWidget(self.category)

        self.usage_editor = ListEditor("usage", presets=USAGE_PRESETS)
        self.value_editor = ListEditor("value", presets=VALUE_PRESETS)
        self.tag_editor = ListEditor("tag", presets=TAG_PRESETS)

        # Final layout
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(flags_box)
        layout.addLayout(cat_row)

        hv = QHBoxLayout()
        hv.addWidget(self.usage_editor)
        hv.addWidget(self.value_editor)
        hv.addWidget(self.tag_editor)
        layout.addLayout(hv)
        layout.addStretch(1)

    def set_category_options(self, categories: List[str]):
        merged = list(dict.fromkeys(CATEGORY_PRESETS + sorted(set(categories))))
        self.category.clear()
        self.category.addItems(merged)

    
    def set_presets(self, presets: Dict[str, TypeEntry]):
        """Provide available presets and populate the combo."""
        self.presets = dict(sorted(presets.items()))
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem("— choose preset —")
        for name in self.presets.keys():
            self.preset_combo.addItem(name)
        self.preset_combo.blockSignals(False)

    def _on_preset_changed(self, idx: int):
        if idx <= 0:
            return
        name = self.preset_combo.currentText()
        entry = self.presets.get(name)
        if entry:
            # Apply the preset to the editor fields without touching the list selection
            self.load_entry(entry)

    def load_entry(self, entry: Optional[TypeEntry]):
        self.current = entry
        if entry is None:
            self.name.clear()
            for sb in (self.nominal, self.lifetime, self.restock, self.min, self.quantmin, self.quantmax, self.cost):
                sb.setValue(sb.minimum())
            for k, cb in self.flag_checks.items():
                cb.setChecked(False)
            self.category.setEditText("")
            self.usage_editor.set_items([])
            self.value_editor.set_items([])
            self.tag_editor.set_items([])
            return
        self.name.setText(entry.name)
        def set_sb(sb: QSpinBox, val: Optional[int]):
            if val is None:
                sb.setValue(sb.minimum())
            else:
                sb.setValue(val)
        set_sb(self.nominal, entry.nominal)
        set_sb(self.lifetime, entry.lifetime)
        set_sb(self.restock, entry.restock)
        set_sb(self.min, entry.min)
        set_sb(self.quantmin, entry.quantmin)
        set_sb(self.quantmax, entry.quantmax)
        set_sb(self.cost, entry.cost)
        for k, cb in self.flag_checks.items():
            cb.setChecked(bool(entry.flags.get(k, 0)))
        self.category.setEditText(entry.category or "")
        self.usage_editor.set_items(entry.usages)
        self.value_editor.set_items(entry.values)
        self.tag_editor.set_items(entry.tags)

    def collect_entry(self) -> Optional[TypeEntry]:
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Type name is required.")
            return None
        def val(sb: QSpinBox) -> Optional[int]:
            # interpret special value (minimum) as unset when special text is empty
            if sb.text() == "":
                return None
            return sb.value()
        entry = TypeEntry(name=name)
        entry.nominal = val(self.nominal)
        entry.lifetime = val(self.lifetime)
        entry.restock = val(self.restock)
        entry.min = val(self.min)
        entry.quantmin = val(self.quantmin)
        entry.quantmax = val(self.quantmax)
        entry.cost = val(self.cost)
        for k, cb in self.flag_checks.items():
            entry.flags[k] = 1 if cb.isChecked() else 0
        cat = self.category.currentText().strip()
        entry.category = cat if cat else None
        entry.usages = self.usage_editor.get_items()
        entry.values = self.value_editor.get_items()
        entry.tags = self.tag_editor.get_items()
        return entry

# ----------------------------- Main Window ----------------------------- #

class MainWindow(QMainWindow):
    def __init__(self):
        apply_dark_palette(QApplication.instance())
    
        super().__init__()
        self.setWindowTitle("DayZ types.xml Generator")
        self.resize(1100, 700)

        self.entries: List[TypeEntry] = []
        self.preset_db: Dict[str, TypeEntry] = {}
        self.category_pool: List[str] = []
        self.current_path: Optional[str] = None

        # UI: left list + right editor
        self.list = QListWidget()
        self.editor = TypeEditor()
        self.editor.set_presets(self.preset_db)

        btn_add = QPushButton("New Type")
        btn_dup = QPushButton("Duplicate")
        btn_del = QPushButton("Delete")
        btn_save = QPushButton("Save Changes to Selected")
        btn_add.clicked.connect(self.new_type)
        btn_dup.clicked.connect(self.duplicate_type)
        btn_del.clicked.connect(self.delete_type)
        btn_save.clicked.connect(self.save_selected_changes)

        left_box = QWidget()
        left_layout = QVBoxLayout(left_box)
        left_layout.addWidget(self.list)
        hl = QHBoxLayout()
        hl.addWidget(btn_add); hl.addWidget(btn_dup); hl.addWidget(btn_del)
        left_layout.addLayout(hl)
        left_layout.addWidget(btn_save)

        self.list.currentItemChanged.connect(self.on_select)

        splitter = QSplitter()
        splitter.addWidget(left_box)
        splitter.addWidget(self.editor)
        splitter.setSizes([350, 750])

        container = QWidget()
        root = QVBoxLayout(container)
        root.addWidget(splitter)
        self.setCentralWidget(container)

        # menu
        self._make_menu()

        # initialize editor categories
        self.editor.set_category_options(self.category_pool)

    def _make_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        presets_menu = menubar.addMenu("Presets")
        act_load_presets = QAction("Load Presets from types.xml...", self)
        act_clear_presets = QAction("Clear Presets", self)
        presets_menu.addAction(act_load_presets)
        presets_menu.addAction(act_clear_presets)
        act_load_presets.triggered.connect(self.action_load_presets)
        act_clear_presets.triggered.connect(self.action_clear_presets)

        view_menu = menubar.addMenu("View")
        self.act_dark = QAction("Dark Mode", self, checkable=True, checked=True)
        view_menu.addAction(self.act_dark)
        self.act_dark.triggered.connect(self.toggle_dark_mode)
        act_new = QAction("New List", self)
        act_new.triggered.connect(self.action_new)
        act_import = QAction("Import types.xml", self)
        act_import.triggered.connect(self.action_import)
        act_export = QAction("Export types.xml", self)
        act_export.triggered.connect(self.action_export)

        file_menu.addAction(act_new)
        file_menu.addSeparator()
        file_menu.addAction(act_import)
        file_menu.addAction(act_export)

    
    # ----- Presets management ----- #
    def action_load_presets(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open vanilla types.xml", "", "XML Files (*.xml)")
        if not path:
            return
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            count = 0
            for elem in root.findall("type"):
                entry = TypeEntry.from_xml(elem)
                if entry and entry.name:
                    self.preset_db[entry.name] = entry
                    count += 1
            # update editor combo
            self.editor.set_presets(self.preset_db)
            QMessageBox.information(self, "Presets Loaded", f"Loaded {count} presets from\n{path}")
        except Exception as ex:
            QMessageBox.critical(self, "Load Presets Failed", f"Could not parse types.xml:\n{ex}")

    def action_clear_presets(self):
        self.preset_db.clear()
        self.editor.set_presets(self.preset_db)
# ----- List management ----- #
    def refresh_list(self):
        self.list.clear()
        for e in self.entries:
            item = QListWidgetItem(e.name)
            self.list.addItem(item)
        self.editor.set_category_options(self.category_pool)

    def on_select(self, cur: Optional[QListWidgetItem], prev: Optional[QListWidgetItem]):
        if cur is None:
            self.editor.load_entry(None)
            return
        idx = self.list.row(cur)
        if 0 <= idx < len(self.entries):
            self.editor.load_entry(self.entries[idx])

    def new_type(self):
        # Clear current selection so Save treats this as a new item
        self.list.clearSelection()
        try:
            self.list.setCurrentRow(-1)
        except Exception:
            pass
        self.editor.load_entry(None)
        # start with sensible flags
        self.editor.flag_checks["count_in_map"].setChecked(True)

    def duplicate_type(self):
        cur = self.list.currentItem()
        if not cur:
            return
        idx = self.list.row(cur)
        src = self.entries[idx]
        dup = TypeEntry(
            name=src.name + "_Copy",
            nominal=src.nominal,
            lifetime=src.lifetime,
            restock=src.restock,
            min=src.min,
            quantmin=src.quantmin,
            quantmax=src.quantmax,
            cost=src.cost,
            flags=dict(src.flags),
            category=src.category,
            usages=list(src.usages),
            values=list(src.values),
            tags=list(src.tags),
        )
        self.entries.insert(idx + 1, dup)
        self.refresh_list()
        self.list.setCurrentRow(idx + 1)

    def delete_type(self):
        cur = self.list.currentItem()
        if not cur:
            return
        idx = self.list.row(cur)
        del self.entries[idx]
        self.refresh_list()
        if self.entries:
            self.list.setCurrentRow(min(idx, len(self.entries) - 1))

    def save_selected_changes(self):
        entry = self.editor.collect_entry()
        if entry is None:
            return
        cur = self.list.currentItem()
        if cur is None or getattr(self.editor, 'current', None) is None:
            # adding a new item
            if any(e.name == entry.name for e in self.entries):
                QMessageBox.warning(self, "Duplicate", f"Type '{entry.name}' already exists.")
                return
            self.entries.append(entry)
        else:
            idx = self.list.row(cur)
            # prevent renaming to an existing name (other than self)
            if any(e.name == entry.name for i, e in enumerate(self.entries) if i != idx):
                QMessageBox.warning(self, "Duplicate", f"Type '{entry.name}' already exists.")
                return
            self.entries[idx] = entryry
            self.list.item(idx).setText(entry.name)
        # update category pool
        if entry.category:
            if entry.category not in self.category_pool:
                self.category_pool.append(entry.category)
        self.refresh_list()
        # keep selection on the saved/added item
        for i, e in enumerate(self.entries):
            if e.name == entry.name:
                self.list.setCurrentRow(i)
                break

    # ----- File actions ----- #
    def action_new(self):
        if self._confirm_discard_changes():
            self.entries.clear()
            self.category_pool.clear()
            self.refresh_list()
            self.editor.load_entry(None)
            self.current_path = None

    def action_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import types.xml", os.getcwd(), "XML Files (*.xml)")
        if not path:
            return
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            if root.tag != "types":
                raise ValueError("Root element is not <types>.")
            entries: List[TypeEntry] = []
            cats = set()
            for t in root.findall("type"):
                e = TypeEntry.from_xml(t)
                entries.append(e)
                if e.category:
                    cats.add(e.category)
            self.entries = entries
            self.category_pool = sorted(set(CATEGORY_PRESETS).union(cats))
            self.refresh_list()
            self.current_path = path
            if self.entries:
                self.list.setCurrentRow(0)
        except Exception as ex:
            QMessageBox.critical(self, "Import Failed", f"Could not load types.xml:\n{ex}")

    def action_export(self):
        if not self.entries:
            QMessageBox.warning(self, "Nothing to export", "Add at least one type before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export types.xml", os.getcwd(), "XML Files (*.xml)")
        if not path:
            return
        try:
            root = ET.Element("types")
            for e in self.entries:
                root.append(e.to_xml())
            xml_str = prettify(root)
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml_str)
            QMessageBox.information(self, "Exported", f"Saved to:\n{path}")
        except Exception as ex:
            QMessageBox.critical(self, "Export Failed", f"Could not save types.xml:\n{ex}")


    def toggle_dark_mode(self, checked: bool):
        if checked:
            apply_dark_palette(QApplication.instance())
        else:
            apply_light_palette(QApplication.instance())
        self.repaint()
    def _confirm_discard_changes(self) -> bool:
        # Simple prompt; could be extended with dirty-tracking
        res = QMessageBox.question(self, "Discard changes?", "This will clear the current list. Continue?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return res == QMessageBox.Yes

# ----------------------------- App Entry ----------------------------- #

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
