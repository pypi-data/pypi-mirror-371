# Colossus_LTSM

[![Website](https://img.shields.io/badge/Website-Link-blue.svg)](https://gavinlyonsrepo.github.io/)  [![Rss](https://img.shields.io/badge/Subscribe-RSS-yellow.svg)](https://gavinlyonsrepo.github.io//feed.xml)  [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/paypalme/whitelight976)

**Colossus_LTSM** is a Python tool for **converting TrueType fonts** (`.ttf`) into **C/C++ bitmap arrays** and for **visualizing font data** stored in C/C++ header files.  
It is aimed at users working with **embedded systems, LCDs, and GUIs** where compact fonts are needed.

## Features

- Convert `.ttf` fonts to C/C++ arrays
- Adjustable **font size**, **ASCII range**, and **addressing mode**
- Visualize fonts from existing C/C++ headers
- GUI built with **Tkinter**
- Lightweight: only depends on `Pillow`

## Installation

1. [github repository](https://www.github.com/gavinlyonsrepo/Colossus_LTSM)
2. [Pypi package](https://pypi.org/project/colossus-ltsm/)

The program is present in python package index, Pypi.
Install (you can use *pip* or *pipx*) to the location or environment of your choice.

## Libraries

- [Pillow](https://python-pillow.org/) for image processing

## Usage

0. Github repository: Colossus_LTSM
1. PyPI package name: colossus-ltsm
2. Import path: import colossus_ltsm
3. Executable command: colossus

Run the GUI:

```python
colossus
// or directly with Python
 python3 -m colossus_ltsm.colossus_main
```

## Input

- Select a `.ttf` font file
- Set font size Width and Height(e.g., 12, 16, 24)
- Define ASCII range (e.g., 32-126)
- Choose addressing mode (horizontal or vertical)
- Choose C or C++ arrays
- Choose file extension (.h or .hpp)
- Choose font name and file name

## Output

- Generates a C or C++ header file with bitmap arrays
- Example output

```c
// Example Font
// An 8 by 8 character size font starting at 
// ASCII offset 0x30 in ASCII table with 0x02 characters in font. 
// 0 and 1 , size 20 bytes, 4 Control bytes at start.
static const std::array<uint8_t, 20> FontBinaryExample =
{
0x08, 0x08, 0x30, 0x01,   // x-size, y-size, offset, (last character-offset : 0x31-0x30)
0x7C,0xC6,0xCE,0xD6,0xE6,0xC6,0x7C,0x00, // ASCII font data '0' : 0x30
0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00 // ASCII font data  '1' : 0x31
};
```

## Configuration file

The configuration file is created on startup and populated by default values.
The file is located at '~/.config/colossus_ltsm/colossus_ltsm.cfg' on Linux systems.

| Setting  | Value |  Default | Note |
| ------ | ------ | ----- | ----- |
| scale | int | 8 | Scale of font displayed  |
| Columns | int |16 | Number of columns of font characters to display|

## Screenshots

![ image ](https://github.com/gavinlyonsrepo/Colossus_LTSM/blob/main/extras/images/screenshot.png)
