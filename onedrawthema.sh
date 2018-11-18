#!/usr/bin/bash
echo kancolle one draw thema collect 
cd /Users/hogeuser/kancolle_pic_class
/usr/local/bin/python3 -m venv venv
source venv/bin/activate
python onedrawthema.py
deactivate
