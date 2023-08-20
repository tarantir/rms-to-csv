#/bin/python
#
# Name: rmsmsg2csv.py
# Version: 20230713
#
# Description: Simple utility to parse RMS Messages and output to CSV
#
# Requires:
#   pip install pandas
#
# Steps have been tested on Windows 10 and Linux Mint 21 +
#
# WARNING!! Use at your own risk; it works fine for me!
#
# Author: Randall Tarantino (rtaranti AT gmail DOT com) is a HAM Radio enthusiast
# not affiliated with Winlink Global Radio Email or the Amateur Radio Safety Foundation, Inc.
#
# This code is licensed under:
#
# MIT License
#
# Copyright (c) 2023 Randall Tarantino (rtaranti AT gmail DOT com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the “Software”), to deal in the
# Software without restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
import os
import email
import csv
import argparse
from datetime import datetime
import pandas as pd

P_MSG_PATH = "./Messages/" #specify the path to your Winlink Messages Folder Typically "C:\RMS Express\NOCALL\Messages" where NOCALL = your callsign (trailing backslash required)
P_DATA_PATH = "./Data/" #specify the path to your Winlink Messages Folder Typically "C:\RMS Express\NOCALL\Data" where NOCALL = your callsign (trailing backslash required)

# change below this line at your own risk
F_REGISTRY_FILE = "Registry.txt"
F_REGISTRY_WORK_FILE = "Registry.wrk"

parser = argparse.ArgumentParser(description="RMS Message to CSV Utility",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("rms_folder_name",
                    help="Specify RMS Folder e.g. InBox or \"Sent Items\" (if spaces use quotes)")
parser.add_argument("csv_filename", help="Specify CSV Output File e.g. ARES.csv")
parser.add_argument('-d', action='store_true', default=False, dest='detailed_output', help="Output detailed mime output")
args = parser.parse_args()

RMS_FOLDER = args.rms_folder_name
F_OUTPUT_FILE_PATH = args.csv_filename
F_OUTPUT_DETAIL = args.detailed_output

def main():
    #Parse Registry.txt to find message ID's in Inbox
    # (1) Copy Registry.txt to Registry.wrk as tab (\t) delimited text
    with open(P_DATA_PATH + F_REGISTRY_FILE, "r", encoding="utf-8") as f_src, open(P_DATA_PATH + F_REGISTRY_WORK_FILE,"w", encoding="utf-8") as f_wrk:
        f_wrk_header = 'a\tb\tc\td\te\tf\tg\th\ti\tj\tk\tl\tm\tn\to\tp\tq\tr\ts\tt\tu\tv\n'
        f_wrk.write(f_wrk_header)
        for f_wrk_item in f_src:
            # (2) Need to convert Start of Heading (SOH) to Tab (\t)
            f_wrk_item = f_wrk_item.replace('\x01', '\t')
            f_wrk.write(f_wrk_item)
    # (3) Use pandas to get RMS Express message-id's for the specified folder e.g. InBox and update workfile
    d_frame = pd.read_table(P_DATA_PATH + F_REGISTRY_WORK_FILE, sep='\t')
    d_frame = d_frame.query('i == "' + RMS_FOLDER + '"')
    d_frame['a'].to_csv(P_DATA_PATH + F_REGISTRY_WORK_FILE, sep='\t', index_label=None, header=False, index=False)
    with open(F_OUTPUT_FILE_PATH, "w", newline="", encoding="utf-8") as f_out:
        file_counter = 0
        f_out_file = csv.writer(f_out)
        if F_OUTPUT_DETAIL:
            f_out_header = 'rms-date', 'rms-source', 'rms-subject', 'rms-to', 'rms-message-id', 'rms-from', 'rms-sender-location', 'rms-message-body'
        else:
            f_out_header = 'rms-date', 'rms-source', 'rms-subject'
        f_out_file.writerow(f_out_header)
        # (4) Parse message files for the selected message-id's only
        with open(P_DATA_PATH + F_REGISTRY_WORK_FILE, "r", encoding="utf-8") as f_wrk:
            f_msg_files = f_wrk.read().splitlines() #remove EOL
        for f_msg_file in f_msg_files:
            is_file = os.path.isfile(P_MSG_PATH + f_msg_file + ".mime")
            if is_file:
                f_msg_mime = email.message_from_file(open(P_MSG_PATH + f_msg_file + ".mime", "r", encoding="utf-8"))
                if f_msg_mime.is_multipart():
                    for f_msg_payload in f_msg_mime.get_payload():
                        f_msg_body = f_msg_payload.get_payload()
                else:
                    f_msg_body = f_msg_mime.get_payload()
                # (5) Write summary to CSV e.g. output.csv
                if F_OUTPUT_DETAIL:
                    f_out_item = datetime.strptime(f_msg_mime.get('Date'), '%a, %d %b %Y %H:%M:%S %z'), f_msg_mime.get('X-Source'), f_msg_mime.get('Subject'), f_msg_mime.get('To'), f_msg_mime.get('Message-ID'), f_msg_mime.get('From'), f_msg_mime.get('X-Location'), f_msg_body
                else:
                    f_out_item = datetime.strptime(f_msg_mime.get('Date'), '%a, %d %b %Y %H:%M:%S %z'), f_msg_mime.get('X-Source'), f_msg_mime.get('Subject')
                f_out_file.writerow(f_out_item)
                file_counter = file_counter + 1
    os.remove(P_DATA_PATH + F_REGISTRY_WORK_FILE)
    print(file_counter, "Messages Processed!")

if __name__ == "__main__":
    main()
