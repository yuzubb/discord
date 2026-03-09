from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import random
import os

app = Flask(__name__)
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

@app.route('/api', methods=['POST'])
def interactions():
    # 署名検証
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    if not signature or not timestamp:
        return 'Unauthorized', 401

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        return 'Invalid request signature', 401

    data = request.json
    
    # 接続確認(PING)
    if data.get('type') == 1:
        return jsonify({"type": 1})

    # スラッシュコマンド実行
    if data.get('type') == 2:
        if data.get('data', {}).get('name') == 'おみくじ':
            user_id = data['member']['user']['id']
            results = ['大吉', '中吉', '小吉', '末吉', '凶']
            selected_result = random.choice(results)

            # Embedの構築 (辞書形式で定義します)
            embed = {
                "title": "おみくじ",
                "description": f"<@{user_id}>さんの今日の運勢は！",
                "color": 11403055, # 16進数 #ADFF2F を10進数に変換したもの
                "fields": [
                    {"name": "[運勢]", "value": selected_result, "inline": True}
                ],
                "thumbnail": {"url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"}, # 代わりの画像
                "url": "https://zenn.dev/articles/0b3ce05e269d70/"
            }

            return jsonify({
                "type": 4,
                "data": {
                    "embeds": [embed]
                }
            })

    return jsonify({"type": 1})
