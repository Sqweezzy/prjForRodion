import os
from datetime import datetime
from database.engine import start_db, orm_db
from flask import Flask, jsonify, request
from database.models import User, Photos, Favorites, Comments
from Common import allowed_file, get_image_info

CACHE = dict()

UPLOAD_FOLDER = './photos'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return "Hello, World!"

#---------------------------------------------------------------------USERS---------------------------------------------------------------------

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    data = CACHE.get('all_users')
    if data is None:
        data = orm_db.session.query(User).all()
        if data == []:
            return jsonify({'error': 'No users found'}), 404
        CACHE['all_users'] = data
    return jsonify({'result': [[f'id - {user.id}',
                                f'username - {user.username}',
                                f'email - {user.email}',
                                f'created_at - {user.created_at}',
                                f'updated_at - {user.updated_at}'] for user in data]
                    }), 200

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    data = orm_db.session.query(User).filter(User.id == user_id).first()
    if data is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'result': [f'id - {data.id}',
                                f'username - {data.username}',
                                f'email - {data.email}',
                                f'created_at - {data.created_at}',
                                f'updated_at - {data.updated_at}']}), 200

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    required_fields = ['username', 'email', 'password']
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    try:
        user = User(**data)
        orm_db.session.add(user)
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_users'] = None
    return jsonify({'message': 'User created successfully',
                    'data': data}), 201

@app.route('/api/v1/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    user = orm_db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    for key, value in data.items():
        setattr(user, key, value)
    try:
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_users'] = None
    return jsonify({'message': 'User updated successfully',
                    'data': data}), 200

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = orm_db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    try:
        orm_db.session.delete(user)
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_users'] = None
    return jsonify({'message': 'User deleted successfully'}), 200

#---------------------------------------------------------------------PHOTOS---------------------------------------------------------------------

@app.route('/api/v1/photos', methods=['GET'])
def get_photos():
    data = CACHE.get('all_photos')
    if data is None:
        data = orm_db.session.query(Photos).all()
        if data == []:
            return jsonify({'error': 'No photos found'}), 404
        CACHE['all_photos'] = data
    return jsonify({'result': [[f'id - {photo.id}',
                                f'user_id - {photo.user_id}',
                                f'file_path - {photo.file_path}',
                                f'file_name - {photo.file_name}',
                                f'size - {photo.size}',
                                f'upload_date - {photo.upload_date}',
                                f'taken_date - {photo.taken_date}',
                                f'width - {photo.width}',
                                f'height - {photo.height}'] for photo in data]
                    }), 200

@app.route('/api/v1/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    data = orm_db.session.query(Photos).filter(Photos.id == photo_id).first()
    if data is None:
        return jsonify({'error': 'Photo not found'}), 404
    return jsonify({'result': [f'id - {data.id}',
                                f'user_id - {data.user_id}',
                                f'file_path - {data.file_path}',
                                f'file_name - {data.file_name}',
                                f'size - {data.size}',
                                f'upload_date - {data.upload_date}',
                                f'taken_date - {data.taken_date}',
                                f'width - {data.width}',
                                f'height - {data.height}']}), 200

@app.route('/api/v1/photos', methods=['POST'])
def upload_photo():
    required_fields = ['user_id']
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo part in the request'}), 400

    data = request.form.to_dict()
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    file = request.files['photo']
    filename = file.filename
    if filename == '':
        return jsonify({"error": "Файл не выбран"}), 400
    
    if file and allowed_file(filename):
        base, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_name = f"{timestamp}_{base}{ext}"
        
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)
    
        get_image_info_result = get_image_info(save_path)

        photo = Photos(
            user_id=data['user_id'],
            file_path=save_path,
            file_name=unique_name,
            size=f"{os.path.getsize(save_path)} bytes",
            upload_date=datetime.now(),
            taken_date=get_image_info_result['taken_date'] if get_image_info_result else None,
            width=get_image_info_result['width'] if get_image_info_result else None,
            height=get_image_info_result['height'] if get_image_info_result else None
        )
        orm_db.session.add(photo)
        try:
            orm_db.commit_db()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({
            'message': 'Photo uploaded successfully',
            'data': {
                'id': photo.id,
                'user_id': photo.user_id,
                'file_path': photo.file_path,
                'file_name': photo.file_name,
                'size': photo.size,
                'upload_date': photo.upload_date,
                'taken_date': photo.taken_date,
                'width': photo.width,
                'height': photo.height
            }
        }), 201

    return jsonify({"error": "Недопустимый формат"}), 400

@app.route('/api/v1/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    photo = orm_db.session.query(Photos).filter(Photos.id == photo_id).first()
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    try:
        orm_db.session.delete(photo)
        orm_db.commit_db()
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_photos'] = None
    return jsonify({'message': 'Photo deleted successfully'}), 200

#---------------------------------------------------------------------FAVORITES---------------------------------------------------------------------

@app.route('/api/v1/favorites', methods=['GET'])
def get_favorites():
    data = CACHE.get('all_favorites')
    if data is None:
        data = orm_db.session.query(Favorites).all()
        if data == []:
            return jsonify({'error': 'No favorites found'}), 404
        CACHE['all_favorites'] = data
    return jsonify({'result': [[f'user_id - {favorite.user_id}',
                                f'photo_id - {favorite.photo_id}'] for favorite in data]
                    }), 200

@app.route('/api/v1/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json()
    required_fields = ['user_id', 'photo_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    try:
        favorite = Favorites(**data)
        orm_db.session.add(favorite)
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_favorites'] = None
    return jsonify({'message': 'Photo added to favorites successfully',
                    'data': data}), 201

#---------------------------------------------------------------------COMMENTS---------------------------------------------------------------------

@app.route('/api/v1/comments', methods=['GET'])
def get_comments():
    data = CACHE.get('all_comments')
    if data is None:
        data = orm_db.session.query(Comments).all()
        if data == []:
            return jsonify({'error': 'No comments found'}), 404
        CACHE['all_comments'] = data
    return jsonify({'result': [[f'id - {comment.id}',
                                f'user_id - {comment.user_id}',
                                f'photo_id - {comment.photo_id}',
                                f'text - {comment.text}',
                                f'created_at - {comment.created_at}',
                                f'updated_at - {comment.updated_at}'] for comment in data]
                    }), 200

@app.route('/api/v1/comments/<int:photo_id>', methods=['GET'])
def get_comment(photo_id):
    data = orm_db.session.query(Comments).filter(Comments.photo_id == photo_id).all()
    if data is None or data == []:
        return jsonify({'error': 'Comment not found'}), 404
    return jsonify({'result': [[f'id - {comment.id}',
                                f'user_id - {comment.user_id}',
                                f'photo_id - {comment.photo_id}',
                                f'text - {comment.text}',
                                f'created_at - {comment.created_at}',
                                f'updated_at - {comment.updated_at}'] for comment in data]
                    }), 200

@app.route('/api/v1/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    required_fields = ['user_id', 'photo_id', 'text']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    try:
        comment = Comments(**data)
        orm_db.session.add(comment)
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_comments'] = None
    return jsonify({'message': 'Comment created successfully',
                    'data': data}), 201

@app.route('/api/v1/comments/<int:comment_id>', methods=['PATCH'])
def update_comment(comment_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    comment = orm_db.session.query(Comments).filter(Comments.id == comment_id).first()
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    for key, value in data.items():
        setattr(comment, key, value)
    try:
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_comments'] = None
    return jsonify({'message': 'Comment updated successfully',
                    'data': data}), 200

@app.route('/api/v1/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = orm_db.session.query(Comments).filter(Comments.id == comment_id).first()
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    try:
        orm_db.session.delete(comment)
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_comments'] = None
    return jsonify({'message': 'Comment deleted successfully'}), 200

@app.route('/api/v1/comments', methods=['POST'])
def add_comment():
    data = request.get_json()
    required_fields = ['user_id', 'photo_id', 'text']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    try:
        comment = Comments(**data)
        orm_db.session.add(comment)
        orm_db.commit_db()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    CACHE['all_comments'] = None
    return jsonify({'message': 'Comment added successfully',
                    'data': data}), 201

#---------------------------------------------------------------------START---------------------------------------------------------------------

if __name__ == '__main__':
    if False:
        start_db.reset_db()
    else:
        start_db.init_db()
    app.run(debug=True) 
    