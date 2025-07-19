import gspread
from oauth2client.service_account import ServiceAccountCredentials

#ここから---------------------------------------------------------------------------------------
#Gspreadから、Googleの接続用アカウントを使えるようにする認証作業
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(Auth, scope)
Client = gspread.authorize(credentials)

#スプシに接続する
SpreadSheet = Client.open_by_key("1vwzM38sPQCTwS2dSlq9HQuutd823psOz-KV2wd0HZyE")
knowledge_sheet = SpreadSheet.worksheet("ナレッジ") #ナレッジ用シート
comment_sheet = SpreadSheet.worksheet("コメント") #コメント用シート
#ここまでは大西さんのコードから引用-------------------------------------------------------------------

#mainで組んでもらってる↑


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

