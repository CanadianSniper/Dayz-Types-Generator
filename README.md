# Dayz Types Generator

A tool to **create, edit, and export** `types.xml` for DayZ servers.  
---

## 📦 Download & Run

1. Go to **Releases** on this repo.
2. Download the Dayz Types Generator`
3. Run `Dayz Types Generator.exe`.

> If SmartScreen warns: click **More info** → **Run anyway**. (See the Security notes below.)

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

## 🙌 Credits

Thanks to the DayZ community and contributors. PRs and feature requests are welcome!
