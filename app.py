from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory, flash
from PIL import Image, ImageFilter, ImageOps
import os

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
        return redirect(request.url)

    file = request.files['image']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(request.url)

    if file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        flash("File uploaded successfully!", "success")
        return render_template('index.html', filename=file.filename, effects={})

# Route to apply blur filter
@app.route('/blur/<filename>', methods=['POST'])
def blur(filename):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    blurred_img = img.filter(ImageFilter.BLUR)
    blurred_path = os.path.join(app.config['UPLOAD_FOLDER'], f"blurred_{filename}")
    blurred_img.save(blurred_path)
    return render_template('index.html', effects={'Blurred Image': f"blurred_{filename}"})

# Route to apply black and white filter
@app.route('/black_and_white/<filename>', methods=['POST'])
def black_and_white(filename):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).convert('L')
    bw_path = os.path.join(app.config['UPLOAD_FOLDER'], f"bw_{filename}")
    img.save(bw_path)
    return render_template('index.html', effects={'Black and White': f"bw_{filename}"})

# Route to apply negative filter
@app.route('/negative/<filename>', methods=['POST'])
def negative(filename):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    inverted_img = ImageOps.invert(img.convert("RGB"))
    negative_path = os.path.join(app.config['UPLOAD_FOLDER'], f"negative_{filename}")
    inverted_img.save(negative_path)
    return render_template('index.html', effects={'Negative Image': f"negative_{filename}"})

# Route to apply compression
@app.route('/compress/<filename>', methods=['POST'])
def compress(filename):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).convert("RGB")
    compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"compressed_{filename}")
    img.save(compressed_path, optimize=True, quality=20)
    return render_template('index.html', effects={'Compressed Image': f"compressed_{filename}"})

# Route to apply cartoon effect
@app.route('/cartoon/<filename>', methods=['POST'])
def cartoon(filename):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).convert("RGB")
    cartoon_img = img.convert("P", palette=Image.ADAPTIVE, colors=64).convert("RGB")
    cartoon_path = os.path.join(app.config['UPLOAD_FOLDER'], f"cartoon_{filename}")
    cartoon_img.save(cartoon_path, "JPEG")
    return render_template('index.html', effects={'Cartoon Image': f"cartoon_{filename}"})

# Route to remove background (simple transparency)
@app.route('/remove_background/<filename>', methods=['POST'])
def remove_background(filename):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).convert("RGBA")
    new_data = [(0, 0, 0, 0) if item[:3] == (255, 255, 255) else item for item in img.getdata()]
    img.putdata(new_data)
    bg_removed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"bg_removed_{filename}")
    img.save(bg_removed_path, "PNG")
    return render_template('index.html', effects={'Background Removed': f"bg_removed_{filename}"})

# Route for download with success message
@app.route('/download/<filename>/<format>', methods=['GET', 'POST'])
def download_image(filename, format):
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    download_path = os.path.join(app.config['UPLOAD_FOLDER'], f"download_{filename}.{format}")
    img.save(download_path, format)

    flash("Download Successful!", "success")
    return send_file(download_path, as_attachment=True, download_name=f"{filename}.{format}")

# Route to serve uploaded images
@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
