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
