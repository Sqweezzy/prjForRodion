from PIL import Image
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_info(file_path: str):
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            exif_data = img.getexif()
            taken_date = None
            if exif_data:
                date_str = exif_data.get(36867)
                if date_str:
                    try:
                        taken_date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    except ValueError:
                        pass
            return {
                "width": width,
                "height": height,
                "taken_date": taken_date,
                "taken_date_str": taken_date.strftime('%Y-%m-%d %H:%M:%S') if taken_date else None,
                "has_exif": bool(exif_data),
            }

    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")
        return None