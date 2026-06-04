# Windows 8 Custom Start Screen

A lightweight, high-performance Windows 8-inspired Start Screen built with Python and PyQt6. It replaces the default Windows 11 Start Menu with a customizable grid layout featuring fully responsive tiles and custom 3D animations.

## Features
* **3D Pop-Out Animation:** Custom "bomb/impact" entrance animation with perspective scaling and elastic bounce effect.
* **Smart Grid Layout:** Drag-and-drop tiles that automatically adjust to avoid overlapping.
* **Fluent Integration:** Seamlessly overrides the Windows key using an AutoHotkey helper script.
* **Modern Transparency:** Custom RGBA background blurring that doesn't compromise tile opacity.

## Requirements
* Python 3.10+
* PyQt6 (`pip install PyQt6`)
* AutoHotkey v1.1 (for the `start_blocker.ahk` script)

## Installation & Usage
1. Clone the repository or download the files into `C:\customstart\`.
2. Install the Python dependencies: `pip install -r requirements.txt`.
3. Run `start_blocker.ahk` to hook the Windows key.
4. Press the **Windows Key** on your keyboard to toggle your new Start Screen!
5. Whenever you press the start key on the keyboard, instead of opening the default windows start it opens this windows 8 start, but if you press start button in the taskbar it won't work, but this is still in beta.
6. This script creates a json file to config all of the tiles: color, position,size ecc... but this script is made in italian
