#!/usr/local/bin python3
# -*- coding: utf-8 -*-

import os
import argparse
import sys
import tweepy
import csv
import re
import sqlite3

temp_file_name      = 'tweets.csv'
output_csvfile_name = 'onedrawthema.csv'

local_db_file_name           = 'shiplist.db'
local_db_table_name          = 'dailythema'
local_db_shiplist_table_name = 'shiplist'

web_db_file_name             = './web/db.sqlite3'
web_db_table_name            = 'manager_dailythema'
web_db_shiplist_table_name   = 'manager_shiplist'

def get_tweetdata():
    #= Twitter API Key の設定
    CONSUMER_KEY        = os.environ.get('TWITTER_CONSUMER_KEY')
    CONSUMER_SECRET     = os.environ.get('TWITTER_CONSUMER_SECRET')
    ACCESS_TOKEN_KEY    = os.environ.get('TWITTER_ACCESS_TOKEN_KEY')
    ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # ツイート取得(@kancolle_1drawユーザーの投稿内容を取得する)
    tweet_data = []
    for tweet in tweepy.Cursor(api.user_timeline,screen_name = "kancolle_1draw",exclude_replies = True).items():
        tweet_data.append([tweet.id, tweet.created_at, tweet.text.replace('\n',''),tweet.favorite_count, tweet.retweet_count])

    # テンポラリCSV出力
    with open(temp_file_name, 'w',newline='',encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(["id","created_at","text","fav","RT"])
        writer.writerows(tweet_data)

def parse_tweetdata():
    # テンポラリCSVファイルを開く
    with open(temp_file_name, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # ヘッダーを読み飛ばす
        header = next(reader)
        # ワンドロテーマデータ
        onedrawthema_data = []

        for row in reader:
            # RTか？
            if row[2].startswith("RT @"):
                # RTメッセージは除外する
                pass
            else:
                # #艦これ版深夜の真剣お絵描き60分一本勝負のハッシュタグが含まれているか？
                if row[2].count('#艦これ版深夜の真剣お絵描き60分一本勝負'):
                    # 予告と開始のツイートの内、開始のツイートのみを対象とする
                    if row[2].count('ワンドロ開始の時間になりました'):
                        # 余分なメッセージを削除する（主催者の投稿内容の表記揺らぎがあるため複数パターンを使用して削除する）
                        tweet_msg1 = row[2]
                        tweet_msg1 = re.sub('ワンドロ開始の時間になりました皆様よろしくお願いします本日のお題は ',   "",  tweet_msg1)
                        tweet_msg1 = re.sub('ワンドロ開始の時間になりました 皆様よろしくお願いします本日のお題は ',  "",  tweet_msg1)
                        tweet_msg1 = re.sub('ワンドロ開始の時間になりました 皆様よろしくお願いします 本日のお題は ', "",  tweet_msg1)
                        tweet_msg1 = re.sub('ワンドロ開始の時間になりました皆様よろしくお願いします。本日のお題は ', "",  tweet_msg1)
                        tweet_msg1 = re.sub(' となります',                                                           "",  tweet_msg1)
                        tweet_msg1 = re.sub(' になります',                                                           "",  tweet_msg1)
                        tweet_msg1 = re.sub(' なります',                                                             "",  tweet_msg1)
                        tweet_msg1 = re.sub('なります',                                                              "",  tweet_msg1)
                        tweet_msg1 = re.sub('"',                                                                     '',  tweet_msg1)
                        tweet_msg1 = re.sub('"',                                                                     '',  tweet_msg1)
                        tweet_msg1 = re.sub('\u3000',                                                                " ", tweet_msg1)
                        tweet_msg1 = re.sub(' #',                                                                    "#", tweet_msg1)
                        # #で区切ることにより、テーマ告知、メインハッシュタグ、日毎ハッシュタグを分離する
                        tweet_msg2 = tweet_msg1.split("#")
                        # テーマ告知箇所をスペースで区切ることで、艦名を取り出せるようにする
                        tweet_msg3 = tweet_msg2[0].split(" ")
                        
                        # 艦名間の区切りがない箇所の為の特別な処理
                        if (tweet_msg3[0] == "卯月アクィラ"):
                            tweet_msg3.append("卯月")
                            tweet_msg3.append("アクィラ")
                            tweet_msg3.remove("卯月アクィラ")
                        # 空白項目以外を新しいリストにコピーする
                        shiplist = [i for i in tweet_msg3 if i != ""]
                        # 日毎ハッシュタグを_で分離し、日付部分を取り出せるようにする
                        hashtag2 = tweet_msg2[2].split("_")
                        # テーマが２隻の場合
                        if (len(shiplist) == 2):
                            onedrawthema_data.append([hashtag2[1], 2, shiplist[0], shiplist[1], "",          ""])
                        # テーマが３隻の場合
                        elif (len(shiplist) == 3):
                            onedrawthema_data.append([hashtag2[1], 3, shiplist[0], shiplist[1], shiplist[2], ""])
                        # テーマが４隻の場合
                        elif (len(shiplist) == 4):
                            onedrawthema_data.append([hashtag2[1], 4, shiplist[0], shiplist[1], shiplist[2], shiplist[3]])
                        # 想定外テーマ数の場合
                        else:
                            print("error:", tweet_msg3)
    return(onedrawthema_data)

def output_csv(onedrawthema_data_temp):
    with open(output_csvfile_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator = '\n')
        writer.writerow(["date","count", "ship1","ship2","ship3","ship4"])
        writer.writerows(onedrawthema_data_temp)

def output_db(args, onedrawthema_data_temp):
    if args.web == 'false':
        output_db_local(args, onedrawthema_data_temp)
    else:
        output_db_web(args, onedrawthema_data_temp)

def output_db_local(args, onedrawthema_data_temp):
    print("output_db_local()")

    # DBアクセスの前処理
    conn = sqlite3.connect(local_db_file_name)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # clean up logic
        if args.clean != 'false':
            cur.execute("drop table if exists " + local_db_table_name)

        # shiplist.db内にdaylythemaテーブルが存在しない場合は生成する  
        sql_str = 'create table if not exists ' + local_db_table_name + '(date string primary key, themacount integer, shipname1 string, shipname2 string, shipname3 string, shipname4 string);'
        cur.execute(sql_str)

        for onedrawthema in onedrawthema_data_temp:
            if args.debug != 'false':
                print(onedrawthema)
            # テーマテーブルを参照し、日付が一致するレコードを取得する
            sql_str = "select * from " + local_db_table_name + " where date = '" + onedrawthema[0] + "';"
            if args.debug != 'false':
                print(sql_str)
            is_record_exist = False
            for row in cur.execute(sql_str):
                if args.debug != 'false':
                    print(row)
                is_record_exist = True
                break
            if is_record_exist:
                if args.debug != 'false':
                    print("レコードあり")
            else:
                if args.debug != 'false':
                    print("レコードなし")
                sql_str = "insert into " + local_db_table_name + " VALUES ('" + onedrawthema[0] + "'," + str(onedrawthema[1]) + "," + "'" + onedrawthema[2] + "'" + "," + "'" + onedrawthema[3] + "'" + "," + "'" + onedrawthema[4] + "'" + "," + "'" + onedrawthema[5] + "');"
                if args.debug != 'false':
                    print(sql_str)
                cur.execute(sql_str)
    finally:
        # DBアクセスの後処理
        conn.commit()
        cur.close()
        conn.close()

def output_db_web(args, onedrawthema_data_temp):
    print("output_db_web()")

    # DBアクセスの前処理
    conn = sqlite3.connect(web_db_file_name)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # clean up logic
        if args.clean != 'false':
            cur.execute("drop table if exists " + web_db_table_name)

        # shiplist.db内にdaylythemaテーブルが存在しない場合は生成する
        sql_str = 'create table if not exists ' + web_db_table_name + ' ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" datetime NOT NULL, "themacount" integer NOT NULL, "shipno1" integer NOT NULL, "shipname1" varchar(256) NOT NULL, "shipno2" integer NOT NULL, "shipname2" varchar(256) NOT NULL, "shipno3" integer NOT NULL, "shipname3" varchar(256) NOT NULL, "shipno4" integer NOT NULL, "shipname4" varchar(256) NOT NULL, "collect_flag" integer NOT NULL);'
        cur.execute(sql_str)
        if args.debug != 'false':
            print(sql_str)

        for onedrawthema in onedrawthema_data_temp:
            if args.debug != 'false':
                print(onedrawthema)
            # テーマテーブルを参照し、日付が一致するレコードを取得する
            sql_str = "select * from " + web_db_table_name + " where date = '" + onedrawthema[0] + "';"
            if args.debug != 'false':
                print(sql_str)
            is_record_exist = False
            for row in cur.execute(sql_str):
                if args.debug != 'false':
                    print(row)
                is_record_exist = True
                break
            if is_record_exist:
                if args.debug != 'false':
                    print("レコードあり")
            else:
                if args.debug != 'false':
                    print("レコードなし")

                # 艦船番号１を取得する
                shipno1 = get_shipno(args, str(onedrawthema[2]), cur, web_db_shiplist_table_name)
                # 艦船番号２を取得する
                shipno2 = get_shipno(args, str(onedrawthema[3]), cur, web_db_shiplist_table_name)
                # 艦船番号３を取得する
                shipno3 = get_shipno(args, str(onedrawthema[4]), cur, web_db_shiplist_table_name)
                # 艦船番号４を取得する
                shipno4 = get_shipno(args, str(onedrawthema[5]), cur, web_db_shiplist_table_name)

                sql_str = "insert into " + web_db_table_name + "(date, themacount, shipno1, shipname1, shipno2, shipname2, shipno3, shipname3, shipno4, shipname4, collect_flag) VALUES ('" + onedrawthema[0] + "'," + str(onedrawthema[1]) + "," + str(shipno1) + "," + "'" + onedrawthema[2] + "'" + "," + str(shipno2) + "," + "'" + onedrawthema[3] + "'" + "," + str(shipno3) + "," + "'" + onedrawthema[4] + "'" + "," + str(shipno4) + "," + "'" + onedrawthema[5] + "'" + ",0" + ");"
                if args.debug != 'false':
                    print(sql_str)
                cur.execute(sql_str)
    finally:
        # DBアクセスの後処理
        conn.commit()
        cur.close()
        conn.close()

def get_shipno(args, shipname, cur, tablename):
    # テーマテーブルを参照し、日付が一致するレコードを取得する
    sql_str = "select shipno from " + tablename + " where shipname = '" + shipname + "';"
    # 該当艦船名レコードが存在しないと仮定する
    shipno = -1
    # 該当艦船名レコードを探す
    for row in cur.execute(sql_str):
        # 艦船番号を取得する
        shipno = row[0]
        break
    if args.debug != 'false':
        print(sql_str, ' : ', str(shipno))
    return shipno

def main():
    parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', type=str, default='false',
                        help='debug switch')
    parser.add_argument('--clean', type=str, default='false',
                        help='clean switch')
    parser.add_argument('--web',   type=str, default='true',
                        help='web switch')
    args = parser.parse_args()

    try:
        print("phase1: ツイート取得")
        get_tweetdata()
        print("phase2: ツイート解析")
        onedrawthema_data = parse_tweetdata()
        print("phase3: CSVファイル出力")
        output_csv(onedrawthema_data)
        print("phase4: DBファイル出力")
        output_db(args, onedrawthema_data)
        print("完了しました")
        sys.exit(0)
    except KeyboardInterrupt:
        print("error: ユーザーにより中断されました")
        sys.exit(1)

if __name__ == '__main__':
    main()
