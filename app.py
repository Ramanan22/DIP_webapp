from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory, flash
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.secret_key = 'supersecretkey'

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Route to handle the home page
@app.route('/')
def index():
    return render_template('index.html', effects={})

# Route to handle image upload
@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        flash("No file part in the request", "error")
        return redirect(url_for('index'))

    file = request.files['image']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('index'))

    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(image_path)
        flash("File uploaded successfully!", "success")
        return render_template('index.html', filename=unique_filename, effects={})

# Route to apply image enhancement
@app.route('/enhance/<filename>', methods=['POST'])
def enhance(filename):
    try:
        enhancement_type = request.form.get('type', 'brightness')
        enhancement_factor = float(request.form.get('factor', 1.0))  # Default factor is 1.0 (no change)

        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))

        # Apply the selected enhancement
        if enhancement_type == 'brightness':
            enhancer = ImageEnhance.Brightness(img)
        elif enhancement_type == 'contrast':
            enhancer = ImageEnhance.Contrast(img)
        elif enhancement_type == 'sharpness':
            enhancer = ImageEnhance.Sharpness(img)
        else:
            flash("Invalid enhancement type!", "error")
            return redirect(url_for('index'))

        enhanced_img = enhancer.enhance(enhancement_factor)
        enhanced_filename = f"enhanced_{enhancement_type}_{filename}"
        enhanced_path = os.path.join(app.config['UPLOAD_FOLDER'], enhanced_filename)
        enhanced_img.save(enhanced_path)
        flash(f"{enhancement_type.capitalize()} enhancement applied successfully!", "success")
        return render_template('index.html', effects={f"Enhanced ({enhancement_type.capitalize()})": enhanced_filename})
    except Exception as e:
        flash(f"Error applying enhancement: {e}", "danger")
        return redirect(url_for('index'))

# Other routes remain unchanged...

# Route to apply blur filter
@app.route('/blur/<filename>', methods=['POST'])
def blur(filename):
    try:
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
        blurred_img = img.filter(ImageFilter.BLUR)
        blurred_filename = f"blurred_{filename}"
        blurred_path = os.path.join(app.config['UPLOAD_FOLDER'], blurred_filename)
        blurred_img.save(blurred_path)
        flash("Blur effect applied!", "success")
        return render_template('index.html', effects={'Blurred Image': blurred_filename})
    except Exception as e:
        flash(f"Error applying blur: {e}", "danger")
        return redirect(url_for('index'))

# Route to apply black and white filter
@app.route('/black_and_white/<filename>', methods=['POST'])
def black_and_white(filename):
    try:
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))).convert('L')
        bw_filename = f"bw_{filename}"
        bw_path = os.path.join(app.config['UPLOAD_FOLDER'], bw_filename)
        img.save(bw_path)
        flash("Black and white effect applied!", "success")
        return render_template('index.html', effects={'Black and White': bw_filename})
    except Exception as e:
        flash(f"Error applying black and white filter: {e}", "danger")
        return redirect(url_for('index'))

# Route to apply negative filter
@app.route('/negative/<filename>', methods=['POST'])
def negative(filename):
    try:
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
        inverted_img = ImageOps.invert(img.convert("RGB"))
        negative_filename = f"negative_{filename}"
        negative_path = os.path.join(app.config['UPLOAD_FOLDER'], negative_filename)
        inverted_img.save(negative_path)
        flash("Negative effect applied!", "success")
        return render_template('index.html', effects={'Negative Image': negative_filename})
    except Exception as e:
        flash(f"Error applying negative filter: {e}", "danger")
        return redirect(url_for('index'))

# Route to compress image
@app.route('/compress/<filename>', methods=['POST'])
def compress(filename):
    try:
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))).convert("RGB")
        compressed_filename = f"compressed_{filename}"
        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], compressed_filename)
        img.save(compressed_path, optimize=True, quality=20)
        flash("Image compressed successfully!", "success")
        return render_template('index.html', effects={'Compressed Image': compressed_filename})
    except Exception as e:
        flash(f"Error compressing image: {e}", "danger")
        return redirect(url_for('index'))

# Route to remove background
@app.route('/remove_background/<filename>', methods=['POST'])
def remove_background(filename):
    try:
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))).convert("RGBA")
        target_color = (255, 255, 255)  # Default to white
        if 'color' in request.form:
            color_hex = request.form['color']
            target_color = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
        new_data = [(0, 0, 0, 0) if item[:3] == target_color else item for item in img.getdata()]
        img.putdata(new_data)
        bg_removed_filename = f"bg_removed_{filename}"
        bg_removed_path = os.path.join(app.config['UPLOAD_FOLDER'], bg_removed_filename)
        img.save(bg_removed_path, "PNG")
        flash("Background removed successfully!", "success")
        return render_template('index.html', effects={'Background Removed': bg_removed_filename})
    except Exception as e:
        flash(f"Error removing background: {e}", "danger")
        return redirect(url_for('index'))

# Route to download an image
@app.route('/download/<filename>/<format>', methods=['GET', 'POST'])
def download_image(filename, format):
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        valid_formats = ['PNG', 'JPEG', 'JPG', 'BMP', 'GIF']

        if format.upper() not in valid_formats:
            flash("Invalid format requested!", "error")
            return redirect(url_for('index'))

        img = Image.open(file_path)
        if format.upper() in ['JPEG', 'JPG'] and img.mode == 'RGBA':
            img = img.convert('RGB')

        base_name, _ = os.path.splitext(filename)
        download_filename = f"{base_name}.{format.lower()}"
        download_path = os.path.join(app.config['UPLOAD_FOLDER'], download_filename)
        img.save(download_path, format.upper())

        flash("Download successful!", "success")
        return send_file(download_path, as_attachment=True, download_name=download_filename)
    except Exception as e:
        flash(f"Error downloading image: {e}", "danger")
        return redirect(url_for('index'))

# Route to serve uploaded images
@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

if __name__ == "__main__":
    app.run(debug=True)
