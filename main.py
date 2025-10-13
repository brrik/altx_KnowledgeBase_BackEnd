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



def get_all_value():
    values = knowledge_sheet.get_all_values()
    header = values[0]
    body = values[1:]
    df = pd.DataFrame(body, columns=header)
    selected_df = df[["ID", "Title", "PostedBy"]].head(10)
    Selected_Knoledge = selected_df.to_dict(orient='records')
    return Selected_Knoledge

def get_filtered_data(knowledge_sheet, comment_sheet, target_id):
    # --- ナレッジシート処理 ---
    knowledge_values = knowledge_sheet.get_all_values()
    knowledge_header = knowledge_values[0]
    knowledge_body = knowledge_values[1:]
    knowledge_df = pd.DataFrame(knowledge_body, columns=knowledge_header)
    filtered_knowledge_df = knowledge_df[knowledge_df["ID"] == str(target_id)]
    filtered_knowledge = filtered_knowledge_df.to_dict(orient='records')
    # --- コメントシート処理 ---
    comment_values = comment_sheet.get_all_values()
    comment_header = comment_values[0]
    comment_body = comment_values[1:]
    comment_df = pd.DataFrame(comment_body, columns=comment_header)
    filtered_comment_df = comment_df[comment_df["KnowledgeID"] == str(target_id)]
    filtered_comment = filtered_comment_df.to_dict(orient='records')
    return filtered_knowledge, filtered_comment

filtered_knowledge, filtered_comments = get_filtered_data(
    knowledge_sheet,
    comment_sheet,
    target_id="3"
)

#selected_Knoledge = get_all_value()
#print(selected_Knoledge)
#print(filtered_knowledge)
#print(filtered_comments)

def search(query):
    values = knowledge_sheet.get_all_values()
    header = values[0]
    body = values[1:]
    df = pd.DataFrame(body, columns=header)
    df =df[["ID", "Title", "PostedBy", "Content", "Tag1", "Tag2", "Tag3"]]
    df = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, regex=False).any(), axis=1)]
    Serch_result = df.to_dict(orient='records')
    return Serch_result
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

#### 以下get通信 ##################################


#起動時にスプレッドシートの上から５件の"ID", "Title", "PostedBy", "Content"を取得する。
@app.get("/items")
async def init_get_items():
    records = knowledge_sheet.get_all_records()
    
    # 必要なカラムだけ抽出（存在する場合のみ）＋上から5件
    filtered_records = [
        {k: row[k] for k in ["ID", "Title", "PostedBy", "Content"] if k in row}
        for row in records[:10]
    ]

    return {"data": filtered_records}

@app.get("/items1")
async def init_get_all_values():
    # get_all_value関数を利用してフロント起動時の10件を取得
    filtered_records = get_all_value()
    return {"data": filtered_records}

#詳細表示の際に全てのコメントを表示する
@app.get("/items/{id}")
async def get_item_with_comments(id: str):
    # get_filtered_data関数を呼び出し
    filtered_knowledge, filtered_comments = get_filtered_data(
        knowledge_sheet,
        comment_sheet,
        target_id=id
    )

    # データが存在しない場合のエラーハンドリング
    if not filtered_knowledge:
        return {"message": f"ID {id} のナレッジが見つかりません。"}

    return {
        "knowledge": filtered_knowledge[0],  # 1件だけ返す（通常IDは一意）
        "comments": filtered_comments        # 紐づくコメント全件
    }
        
#　ポストにいいねをする
@app.get("/nice/{id}")
async def nice_post(id: int):
    # すべてのデータを取得（ヘッダー付き辞書形式）
    records = knowledge_sheet.get_all_records() 
    
    row_index = None
    for idx, row in enumerate(records, start=2):  # データは2行目から
        if row["ID"] == id:
            print(id, row["ID"]) #デバッグ用
            row_index = idx
            break

    if row_index is None:
        # 存在しなければ新規追加（ヘッダーに合わせて列を並べる）
        knowledge_sheet.append_row([id, 1])  # 例: [id, nice] の順
        return {"message": f"ID {id} に初めていいねしました！", "Nice": 1}
    else:
        # 既存レコードを更新（ヘッダー名 "nice" に対応する列番号を探す）
        header = knowledge_sheet.row_values(1)  # 1行目（ヘッダー）
        nice_col = header.index("Nice") + 1  # 1始まりに変換
        
        current_nice = knowledge_sheet.cell(row_index, nice_col).value
        #データがなかったときにエラー出るからNull判定入れた　おおにし
        if not current_nice:
            current_nice = 0
        else:
            current_nice = int(current_nice)
        new_nice = current_nice + 1
        knowledge_sheet.update_cell(row_index, nice_col, new_nice)

        return {"message": f"ID {id} にいいねしました！", "nice": new_nice}

@app.get("/search/{query}")
async def init_serch(query: str):
    # serch関数を利用してデータを取得
    serach_result = search(query)
    return {"data": serach_result}
#### 以上get通信 ##################################

#### 以下post通信 #################################

# 受け取るデータの型を定義
class KnowledgeItem(BaseModel):
    Title: str
    PostedBy: str
    Content: str
    Tag1: str
    Tag2: str
    Tag3: str

# POSTエンドポイント
@app.post("/post-knowledge")
async def post_knowledge(item: KnowledgeItem):
    add_knowledge(knowledge_sheet, item.dict())
    return {"message": "スプレッドシートにナレッジ追加成功", "posted_data": item}

# コメント投稿用モデル
class CommentItem(BaseModel):
    KnowledgeID: str  # 対応するナレッジのID
    PostedBy: str
    Content: str

# コメントをスプレッドシートに追加
@app.post("/post-comment")
async def post_comment(item: CommentItem):
    add_comment(comment_sheet, item.dict())
    return {"message": "スプレッドシートにコメント追加成功", "posted_data": item}



#### 以上post通信 ###################################
 


#スプレッドシートへの投稿用コード_川空作成分

#関数定義

#ナレッジ投稿関数
def add_knowledge(knowledge_sheet, data):

#ヘッダー情報取得
    knowledge_header = knowledge_sheet.row_values(1)

#IDの採番
    all_rows = knowledge_sheet.get_all_values()
    id_index = knowledge_header.index("ID")
    existing_ids = [int(row[id_index]) for row in all_rows[1:] if row[id_index].isdigit()]
    new_id = max(existing_ids, default=0) + 1

#行データの作成
    new_row = [""] * len(knowledge_header)
    new_row[id_index] = str(new_id)

    for key,value in data.items():
        if key in knowledge_header:
            col_index = knowledge_header.index(key)
            new_row[col_index] = value

#シートへ書込み
    next_row = len(all_rows) + 1 #次の空行を取得（既存行数+1）
    knowledge_sheet.insert_row(new_row,next_row)
    print(f"書き込み完了：ID {new_id}")


#コメント投稿関数
def add_comment(comment_sheet, comment_data):
#ヘッダー情報取得
    comment_header = comment_sheet.row_values(1)

#IDの採番
    all_rows = comment_sheet.get_all_values()
    id_index =comment_header.index("CommentID") 
    existing_ids = [int(row[id_index]) for row in all_rows[1:] if row[id_index].isdigit()]
    new_comment_id = max(existing_ids, default=0) + 1

#行データの作成
    new_row = [""] * len(comment_header)
    new_row[id_index] = str(new_comment_id)

    for key,value in comment_data.items():
        if key in comment_header:
            col_index = comment_header.index(key)
            new_row[col_index] = value

#シートへ書込み
    next_row = len(all_rows) +1
    comment_sheet.insert_row(new_row,next_row)



#投稿データと実行

#ナレッジ投稿データ（Jsonができていないので仮）
##post投稿エンドポイント作成したので一旦コメントアウトした。tarahi
#data = {
#    "Title": "最近のブーム",
#    "PostedBy": "川空のどか",
#    "Content": "蒸籠でごはんをつくること！",
#    "Tag1": "ご飯",
#    "Tag2": "日記",
#    "Tag3": "生活"
#}
#
##ナレッジ関数実行
#add_knowledge(knowledge_sheet, data)

#コメント投稿データ（Jsonができていないので仮）
comment_data = {
    "KnowledgeID": "3",  #対象のIDナレッジにコメントする
    "PostedBy": "川空のどか",
    "Content": "めっちゃ参考になりました！最高！！！"
}
