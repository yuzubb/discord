from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import random
import os
import requests

app = Flask(__name__)

# 環境変数の読み込み
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
APP_ID = os.getenv('DISCORD_APPLICATION_ID')
GUILD_ID = os.getenv('GUILD_ID')

def register_command():
    """Discordにスラッシュコマンドを登録する関数"""
    if not BOT_TOKEN or not APP_ID or not GUILD_ID:
        return "Error: Missing Environment Variables (TOKEN, APP_ID, or GUILD_ID)"
    
    url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{GUILD_ID}/commands"
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    json_data = {
        "name": "おみくじ",
        "description": "今日のおみくじを引きます"
    }
    response = requests.post(url, headers=headers, json=json_data)
    return response.status_code

def handle_interactions():
    """Discordからのリクエストを処理する関数"""
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    if not signature or not timestamp or not PUBLIC_KEY:
        return 'Unauthorized', 401

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        return 'Invalid request signature', 401

    data = request.json
    
    # 1. Ping (Discordからの接続確認)
    if data.get('type') == 1:
        return jsonify({"type": 1})

    # 2. スラッシュコマンド実行
    if data.get('type') == 2:
        if data.get('data', {}).get('name') == 'おみくじ':
            user_id = data['member']['user']['id']
            results = ['大吉', '中吉', '小吉', '末吉', '凶']
            selected_result = random.choice(results)

            # Embedメッセージの構築
            embed = {
                "title": "おみくじ",
                "description": f"<@{user_id}>さんの今日の運勢は！",
                "color": 11403055, # #ADFF2F
                "fields": [
                    {"name": "[運勢]", "value": selected_result, "inline": True}
                ],
                "thumbnail": {"url": "https://3.bp.blogspot.com/-cPqdLavQBXA/UZNyKhdm8RI/AAAAAAAASiM/NQy6g-muUK0/s400/syougatsu2_omijikuji2.png"},
                "url": "https://3.bp.blogspot.com/-cPqdLavQBXA/UZNyKhdm8RI/AAAAAAAASiM/NQy6g-muUK0/s400/syougatsu2_omijikuji2.png"
            }

            return jsonify({
                "type": 4,
                "data": {"embeds": [embed]}
            })

    return jsonify({"type": 1})

@app.route('/api', methods=['GET', 'POST'])
def main():
    # ブラウザでアクセス（GET）した場合はコマンド登録を実行
    if request.method == 'GET':
        status = register_command()
        return f"Register Command Status: {status} (If 200 or 201, it's Success!)"
    
    # Discordからの信号（POST）はボット処理を実行
    return handle_interactions()

# Vercel用
app.debug = True
