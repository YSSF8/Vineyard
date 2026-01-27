# Vineyard V1.5

## Executive Summary

Vineyard V1.5 is here, and we’ve added a **Find** tool to the Advanced tab to make your life a little easier. It’s a simple addition that makes a massive difference when you’re deep in a project—less time hunting for text, and more time actually creating.

---

## Changelog

### ✨ Features

* **Find Tool in Theme Maker**:
    * Added **"Find `Ctrl+F`"** to the Advanced tab context menu.
    * Floating search dialog with **case-sensitive** toggle (off by default) and **regex support** (off by default).
    * Keyboard navigation: `Enter`/`Down` for next match, `Up` for previous match, `Escape` to close.
    * Visual highlighting of current match with wrap-around search.

---

# Vineyard V1.4

## Executive Summary

Vineyard V1.4 introduces significant compatibility upgrades and aesthetic flexibility, headlined by full support for **Wine 9.0+** and a new theme conversion tool for the **COSMIC Desktop Environment**. This release focuses on streamlining the user experience through a redesigned ContextMenu API and "Quality of Life" improvements to the Theme Maker, ensuring the tool remains both powerful for power users and accessible for newcomers.

---

## Changelog

### 🚀 Improvements

* **Wine Compatibility**: Standardized **Universal Wine Versions** to ensure seamless operation across Wine 9.0+ and legacy versions.
* **Refreshed UI Themes**:
* **New**: Added **Catppuccin** (Dark & Light) and **Matrix** themes.
* **Updated**: Refined the **Everforest** color palette for better legibility.

### ✨ Features

* **COSMIC DE Integration**: Introduced a specialized utility to convert `.ron` configuration files to `.reg` files, allowing for deep theme synchronization within the COSMIC Desktop Environment.
* **Enhanced ContextMenu API**:
* Redesigned the layout to reduce visual clutter.
* Added **keyboard shortcut hints** next to menu items for faster navigation.

* **Theme Maker Power Tools**:
* Added a **"Select All"** option to the context menu.
* Implemented the `Ctrl + A` global hotkey for bulk selection.

### 🛠️ Fixes

* **Theme Maker**: Resolved a specific initialization error that occurred when launching the Theme Maker module.