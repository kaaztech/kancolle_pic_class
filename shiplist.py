#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import csv
import urllib3
import requests
from bs4 import BeautifulSoup
import sqlite3

db_file_name         = 'shiplist.db'
output_csv_file_name = 'shiplist.csv'

def get_wikidata(args):
    # Wikiからhtmlファイルを取得する
    http = urllib3.PoolManager()
    r = http.request('GET','https://wikiwiki.jp/kancolle/%E8%89%A6%E5%A8%98%E3%82%AB%E3%83%BC%E3%83%89%E4%B8%80%E8%A6%A7')
    return(r)

def parse_wikidata(args, r):
    # Wikiから取得したデータを解析する
    soup = BeautifulSoup(r.data, "html.parser")
    htmlParsed = soup.find_all("a")
    shiplist_data = []
    for a in htmlParsed:
        if (a is not None):
            if (a.find('img') is not None):
                # imageタグ内のtitle属性の情報を取得する
                titleattr = a.find('img')['title']
                if (titleattr is not None):
                    if (titleattr.count(':') == 1):
                        shipinfo = titleattr.split(':')
                        shiplist_data.append([shipinfo[0], shipinfo[1]]) 
                        if (args.debug == 'true'):
                            print(shipinfo[0], shipinfo[1])

    return(shiplist_data)

def output_csv(args, shiplist_data_temp):
    with open(output_csv_file_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator = '\n')
        writer.writerow(["no","name"])
        writer.writerows(shiplist_data_temp)

def output_db(args, shiplist_data_temp):
    # DBアクセスの前処理
    conn = sqlite3.connect(db_file_name)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # test logic
        if (args.clean == 'true'):
            cur.execute("drop table if exists shiplist")

        # shiplist.db内にshiplistテーブルが存在しない場合は生成する  
        sql_str = 'create table if not exists shiplist(shipno integer primary key, shipname string);'
        cur.execute(sql_str)

        # test logic
        if (args.debug == 'true'):
            sql_str = 'select * from sqlite_master;'
            for row in cur.execute(sql_str):
                print(row)

        for shipdata in shiplist_data_temp:
            shipno = int(shipdata[0])
            # 艦船番号が一致するレコードが存在しないと仮定する
            is_record_exist = False
            # 艦船リストテーブルを参照し、艦船番号が一致するレコードを取得する
            sql_str = "select * from shiplist where shipno = " + str(shipno) + ";"
            if (args.debug == 'true'):
                print(sql_str)
            for row in cur.execute(sql_str):
                if (args.debug == 'true'):
                    print(row)
                # 艦船番号が一致するレコードが存在する
                is_record_exist = True
                break
            # 艦船番号が一致するレコードが存在するか？
            if is_record_exist:
                if (args.debug == 'true'):
                    print("レコードあり")
                sql_str = "update shiplist set shipname = '" + shipdata[1] + "' where shipno = " + str(shipno) + ";"
                if (args.debug == 'true'):
                    print(sql_str)
                cur.execute(sql_str)
            else:
                if (args.debug == 'true'):
                    print("レコードなし")
                sql_str = "insert into shiplist VALUES (" + str(shipno) + "," + "'" + shipdata[1] + "');"
                if (args.debug == 'true'):
                    print(sql_str)
                cur.execute(sql_str)
    finally:
        # DBアクセスの後処理    
        conn.commit()
        cur.close()
        conn.close()

def main():
    parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', type=str, default='false',
                        help='debug switch')
    parser.add_argument('--clean', type=str, default='false',
                        help='clean switch')
    args = parser.parse_args()

    try:
        print("phase1: Wikiデータ取得")
        r = get_wikidata(args)
        if r.status != requests.codes.ok:
            print("error: Wikiへのアクセスに失敗しました(", str(r.status), ")")
            sys.exit(1)
        else:
            print("Wikiへのアクセスに成功しました")
        print("phase2: Wikiデータ解析")
        shiplist_data = parse_wikidata(args, r)
        print("phase3: CSVファイル出力")
        output_csv(args, shiplist_data)
        print("phase4: DBファイル出力")
        output_db(args, shiplist_data)
        print("完了しました")
        sys.exit(0)
    except KeyboardInterrupt:
        print("error: ユーザーにより中断されました")
        sys.exit(1)

if __name__ == '__main__':
    main()
