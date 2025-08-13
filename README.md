# Dayz Types Generator

A modern PySide6 desktop tool to **create, edit, and export** `types.xml` for DayZ servers.  
Includes **dark mode**, **preset loader** from vanilla `types.xml`, and **dropdown editors** for Categories, Usage, Value tiers, and Tags.

> Built for Windows. Works from source on any OS with Python 3.10+ and PySide6.

---

## 📦 Download & Run

### Option A — Download the EXE (recommended)
1. Go to **Releases** on this repo.
2. Download the **`Dayz Types Generator`** onedir build (a folder with the EXE inside).
3. Run `Dayz Types Generator.exe`.

> If SmartScreen warns: click **More info** → **Run anyway**. (See the Security notes below.)

### Option B — Run from source
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt  # (PySide6 required)
python types_generator.py
```

---

## 🚀 Quick Start

1. **Open the app** (dark mode is on by default).
2. **(Optional) Load Presets:**  
   - Menu **Presets → Load Presets from types.xml…** and pick your vanilla `types.xml`  
   - The **Preset** dropdown (top of the right panel) will populate with all item names.
3. **Create a new type:**  
   - Click **New List** (for a fresh project) or **New Type** to add one.
   - Fill out the fields on the right:
     - **Name**: item class name
     - **Nominal, Lifetime, Restock, Min/QuantMin/QuantMax, Cost**: numbers
     - **Flags**: checkboxes (count_in_cargo, etc.)
     - **Category**: dropdown (pre-seeded with: weapons, food, tools, clothes, books, containers, explosives, lootdispatch)
     - **Usage / Value / Tag**: use the dropdown + **Add** button to add to the list (manual entry is still allowed)
4. **Use a preset:**  
   - Choose an item from the **Preset** dropdown to auto-fill all fields based on your loaded `types.xml`.
   - Edit anything you like after applying a preset.
5. **Save to the list:**  
   - Click **Save Changes to Selected**.  
   - If no entry is selected (e.g., after **New Type**), it **adds** a new item. If an entry is selected, it **updates** that item.
6. **Export** your final `types.xml`:  
   - Menu **File → Export types.xml** and choose the destination.

---

## 🧭 UI Overview

- **Left panel:** list of entries in your working set.
  - **New Type**: starts a fresh item (clears selection so Save = Add).
  - **Duplicate Type**: copies the selected item for quick variations.
  - **Delete Type**: removes the selected item.
- **Right panel:** editor for the selected item (or blank when creating).
  - **Preset** dropdown: auto-fills fields from loaded `types.xml`.
  - **Name & Numbers**: standard DayZ fields (Nominal, Lifetime, etc.).
  - **Flags** group: common booleans (count_in_map, etc.).
  - **Category**: dropdown with your fixed set (plus any found via import).
  - **Usage / Value / Tag** list editors:
    - Use the **dropdown** then **Add** to append items.
    - Or type in the text box and click **Add (manual)**.
    - Select and **Remove Selected** to delete an entry.
- **Dark/Light toggle:** **View → Dark Mode**.

---

## 🧩 Presets (vanilla types)

**Load Presets** from **Presets → Load Presets from types.xml…** (your vanilla `types.xml`).  
Then use the **Preset** dropdown in the editor:

- Selecting a preset **fills all fields** (name, numbers, flags, category, usages/values/tags).
- After applying a preset, **Save Changes to Selected** to add/update your list.

> Tip: If you want selection of a preset to **auto-create** a new entry immediately, ask in Issues—we can enable the auto-add behavior.

---

## 🔄 Import / Export

- **Import types.xml**: **File → Import types.xml**  
  - Adds all items from a file to your working list.
  - Detected categories are merged with the fixed Category dropdown options.
- **Export types.xml**: **File → Export types.xml**  
  - Writes your current working list to `types.xml`.

---

## ✅ Data fields supported

- `name`
- `nominal`, `lifetime`, `restock`  
- `min`, `quantmin`, `quantmax`
- `cost`
- `flags` (all common booleans that appear in DayZ types)
- `category` (single)
- `usage` (list)
- `value` (list; includes **Tier1–Tier4** presets)
- `tag` (list; includes **none/shelves/floor/ground** presets)

---

## 🌓 Dark Mode

- Default is **Dark Mode** (Fusion style + tuned palette).
- Toggle in **View → Dark Mode**.

---

## 🛟 Tips & Troubleshooting

- **“Save Changes to Selected” overwrote my item:**  
  Use **New Type** first (it clears selection so Save = *Add*), or ensure no left-list item is selected before saving.
- **Preset list is huge:**  
  Start typing in the Preset dropdown to search; we can also enable a contains-filter completer if you prefer.
- **AV / SmartScreen warning:**  
  See **Security notes** below—use the onedir build, check the SHA-256 hash, and consider code signing for releases.

---

## 🔐 Security notes

- The release uses **onedir** (fewer AV flags than onefile).
- No UPX packing (reduces false positives).
- Version info is embedded into the EXE.
- For extra trust:
  - Verify the **SHA-256** in `checksums.txt` (on the Release).
  - Build from source locally.
  - Code signing is recommended for maintainers (we can help wire this into CI).

---

## 🛠️ Build from source (developer)

### Local
```bat
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install pyinstaller PySide6
pyinstaller types_generator_onedir.spec --clean
```

### GitHub Actions (Windows)
- Put the workflow at `.github/workflows/build-windows.yml` (provided).
- Tag a release:
```bat
git tag v1.0.0
git push origin v1.0.0
```
- The workflow builds and uploads artifacts + `checksums.txt`, and attaches them to the Release.

---

## 📄 License

MIT (or your choice—update this section if you prefer a different license).

---

## 🙌 Credits

Thanks to the DayZ community and contributors. PRs and feature requests are welcome!
