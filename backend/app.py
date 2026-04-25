from flask import Flask, jsonify, request
from flask_cors import CORS
import requests as req
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

@app.route('/api/shops', methods=['GET'])
def get_shops():
    search    = request.args.get('search', '')
    category  = request.args.get('category', '')
    sort      = request.args.get('sort', 'newest')
    page      = int(request.args.get('page', 0))
    page_size = 9

    params = {
        'select': '*,profiles(name,profile_image)',
        'order': 'created_at.desc' if sort != 'top_rated' else 'average_rating.desc',
        'offset': page * page_size,
        'limit': page_size
    }

    if search:
        params['or'] = f'(title.ilike.%{search}%,description.ilike.%{search}%,category.ilike.%{search}%)'

    if category and category != 'All':
        params['category'] = f'eq.{category}'

    headers = {**HEADERS, 'Prefer': 'count=exact'}
    response = req.get(f'{SUPABASE_URL}/rest/v1/shops', headers=headers, params=params)

    count = int(response.headers.get('content-range', '0/0').split('/')[-1])

    return jsonify({
        'shops': response.json(),
        'count': count
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
