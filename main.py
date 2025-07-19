from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware #CORS用
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
import requests
from pydantic import BaseModel
import pandas as pd


#ここからGspread用=============================================

#GspreadからGoogleに接続する用のデータを別ファイルからとってくる
Auth = "./norse-lotus-423606-i2-353a26d9cd49.json" #別ファイルのパス（予定）
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Auth

#Gspreadから、Googleの接続用アカウントを使えるようにする認証作業
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(Auth, scope)
Client = gspread.authorize(credentials)

#スプシに接続する
SpreadSheet = Client.open_by_key("1vwzM38sPQCTwS2dSlq9HQuutd823psOz-KV2wd0HZyE")
knowledge_sheet = SpreadSheet.worksheet("ナレッジ") #ナレッジ用シート
comment_sheet = SpreadSheet.worksheet("コメント") #コメント用シート



def get_all_value_rensyu():
    values = knowledge_sheet.get_all_values()
    header = values[0]
    body = values[1:]
    df = pd.DataFrame(body, columns=header)
    selected_df = df[["ID", "Title", "PostedBy"]]
    print(selected_df.to_string(index=False))
get_all_value_rensyu()


#ここからFastAPI用=============================================
# CORS
# 消さないで　担当大西

app = FastAPI() #FastAPIインスタンス作成

# 外部からの通信を受け付けるためのやつ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# ここまで

#### 以下get通信 ####

@app.get("/")
async def getMain():
    print("hello, world")
    #川空コメント
    #川空ブランチにあげる練習
    #升村の愚痴
    print("raigetu nikkinn ooi urepi-")

#大西アップデート
@app.get("/hoge")
async def hogeta():
    print("hoge")
    
#たらひテスト
@app.get("/test-tarahi")
async def tarahi_test_def():
    return "これはtarahiのテストです"

@app.get("/test-item")
async def test_def():
    return "this is a test"

#masu test
@app.get("/gorenkin-saiko")
async def gorenkin():
    return "これはmasuのテストです"

#いまいテスト
@app.get("/natsubategimi")
async def natsubate():
    return "これはimaiのテストです"

#### 以上get通信 ####

#### 以下post通信 ####

# 受け取るデータの型を定義
class Item(BaseModel):
    title: str
    name: str
    detail: str
    tag1: str
    tag2: str   #今井追加

# POSTリクエストを受け取るエンドポイント
@app.post("/post-test")
async def post_test(item: Item):
    return {"message": "受信成功", "受け取ったデータ": item}



#### 以上post通信 ####
 


#スプレッドシートへの投稿用コード_川空作成分

#ナレッジシートのヘッダー情報取得
knowledge_header = knowledge_sheet.row_values(1)

#IDの採番
all_rows = knowledge_sheet.get_all_values()
id_index = knowledge_header.index("id")
existing_ids = [int(row[id_index]) for row in all_rows[1:] if row[id_index].isdigit()]
new_id = max(existing_ids, default=0) + 1

#投稿データ（Jsonができていないので仮）
data = {
    "Title": "最近のブーム",
    "PostedBy": "川空のどか",
    "Content": "蒸籠でごはんをつくること！",
    "Tag1": "ご飯",
    "Tag2": "日記",
    "Tag3": "生活"
}

#行データの作成
new_row = [""] * len(knowledge_header)
new_row[id_index] = str(new_id)

for key,value in data.items():
    if key in knowledge_header:
        col_index = knowledge_header.index(key)
        new_row[col_index] = value

#シートへの書き込み
next_row = len(all_rows) + 1 #次の空行を取得（既存行数+1）
knowledge_sheet.insert_row(new_row,next_row)
print(f"書き込み完了：ID {new_id}")


#コメントシートのヘッダー情報取得
comment_header = comment_sheet.row_values(1)

#IDの採番
all_rows = comment_sheet.get_all_values()
id_index =comment_header.index("コメントID") #ここ"コメントID"変わったらその項目に変更(ヘッダーと同じ項目)
existing_ids = [int(row[id_index]) for row in all_rows[1:] if row[id_index].isdigit()]
new_comment_id = max(existing_ids, default=0) + 1

#投稿データ（Jsonができていないので仮）
comment_data = {
    "紐付け先ナレッジID": "3",  #対象のIDナレッジにコメントする
    "投稿者": "川空のどか",
    "内容": "めっちゃ参考になりました！最高！！！"
}

#行データの作成
new_row = [""] * len(comment_header)
new_row[id_index] = str(new_comment_id)

for key,value in comment_data.items():
    if key in comment_header:
        col_index = comment_header.index(key)
        new_row[col_index] = value

#シートへの書き込み
next_row = len(all_rows) +1
comment_sheet.insert_row(new_row,next_row)
print(f"コメントの書き込み完了：ID {new_comment_id}")


