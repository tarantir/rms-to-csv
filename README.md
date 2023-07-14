# About

rmsmsg2csv.py is a simple utility that will parse RMS Messages and output to CSV.

This script leverages standard email mime processing to parse the following details:
- Date, From, Subject, To, Message-id, X-Source, X-Location, Body Content

Author: Randall Tarantino (rtaranti AT gmail DOT com) is a HAM Radio enthusiast 
 not affiliated with Winlink Global Radio Email or the Amateur Radio Safety Foundation, Inc.

## Not Supported

GUI this is all command line

# Installation on Windows 10

Install has been tested on Windows 10 and Linux Mint 21 +

## Python 3

Manually install Python 3 from Microsoft Store
 or
```
C:\winget install python3
```
## Pandas

```
pip install pandas
```
or
```
C:\pip install pandas
```

## Installation Instructions:

- copy rmsmsg2csv.py to "C:\RMS Express\NOCALL\" where NOCALL = your callsign

# Usage

WARNING!! Use at your own risk; it works fine for me!
```
python ./rmsmsg2csv.py
```
or
```
"C:\RMS Express\NOCALL\python rmsmsg2csv.py"
```

# License

 This code is licensed under:
 MIT License

 Copyright (c) 2023 Randall Tarantino (rtaranti AT gmail DOT com)

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the “Software”), to deal in the
 Software without restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
 Software, and to permit persons to whom the Software is furnished to do so, subject
 to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
 OR OTHER DEALINGS IN THE SOFTWARE.
