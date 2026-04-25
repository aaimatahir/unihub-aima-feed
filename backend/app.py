from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@app.route('/api/shops', methods=['GET'])
def get_shops():
    search   = request.args.get('search', '')
    category = request.args.get('category', '')
    sort     = request.args.get('sort', 'newest')
    page     = int(request.args.get('page', 0))
    page_size = 9

    query = supabase.from_('shops').select(
        '*, profiles(name, profile_image)', count='exact'
    )

    if search:
        query = query.or_(f'title.ilike.%{search}%,description.ilike.%{search}%,category.ilike.%{search}%')

    if category and category != 'All':
        query = query.eq('category', category)

    if sort == 'top_rated':
        query = query.order('average_rating', desc=True)
    else:
        query = query.order('created_at', desc=True)

    query = query.range(page * page_size, (page + 1) * page_size - 1)

    response = query.execute()

    return jsonify({
        'shops': response.data,
        'count': response.count
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
