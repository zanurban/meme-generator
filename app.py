from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

# Konfiguracija
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

# Ustvarimo mapo za nalaganje slik
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Preverimo, če je datoteka dovoljena"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_text_to_image(image_path, top_text, bottom_text):
    """
    Dodamo tekst na sliko

    Koraki:
    1. Odpremo sliko
    2. Prilagodimo velikost čim potrebno
    3. Nastavimo font
    4. Narišemo tekst na vrhu in dnu
    5. Vrnemo sliko
    """
    try:
        # 1. Odpremo sliko
        img = Image.open(image_path)

        # Pretvorimo v RGB, če je potrebno (za PNG z alfa kanalom)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # 2. Omejimo velikost slike na maksimalno 1200x900
        max_width = 1200
        max_height = 900
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        width, height = img.size
        draw = ImageDraw.Draw(img)

        # 3. Nastavimo font - poskusimo z različnimi velikostmi
        font_size = int(height / 8)
        try:
            # Poskusimo uporabiti sistemski font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except (IOError, OSError):
            try:
                # Poskusimo macOS font
                font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
            except (IOError, OSError):
                # Če fonti niso dostopni, uporabimo privzeti font
                font = ImageFont.load_default()

        # Nastavimo barvo teksta na belo z črnim obrisom
        text_color = (255, 255, 255)
        outline_color = (0, 0, 0)
        outline_width = 2

        # Razpoložljivi prostor za tekst (10% od vrha, 10% od dna)
        available_height_per_section = int(height * 0.2)

        # 4. Narišemo zgornji tekst
        if top_text:
            draw_text_with_outline(draw, top_text, font, width, height,
                                   y_position=0.05, available_height=available_height_per_section,
                                   text_color=text_color,
                                   outline_color=outline_color, outline_width=outline_width)

        # 5. Narišemo spodnji tekst
        if bottom_text:
            draw_text_with_outline(draw, bottom_text, font, width, height,
                                   y_position=0.80, available_height=available_height_per_section,
                                   text_color=text_color,
                                   outline_color=outline_color, outline_width=outline_width)

        return img

    except Exception as e:
        print(f"Napaka pri obdelavi slike: {e}")
        return None


def draw_text_with_outline(draw, text, font, width, height, y_position, available_height, text_color, outline_color, outline_width):
    """Narišemo tekst z obrisom in preverkami za preseganje mej ter dinamičnim zmanjšanjem fonta"""
    from PIL import ImageFont

    # Razdelimo tekst na več vrstic, če je predolg
    max_chars_per_line = 30
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        if len(current_line + word) < max_chars_per_line:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())

    y_offset = int(height * y_position)
    initial_line_height = int(font.size * 1.2) if hasattr(font, 'size') else 30
    line_height = initial_line_height

    # Preverimo, ali je katera vrstica predolga za širino slike
    max_width = width - 40  # 20px margina na vsaki strani
    needs_font_reduction = False

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width > max_width:
            needs_font_reduction = True
            break

    # Če je potrebna redukcija fonta, jo naredimo iterativno
    current_font = font
    if needs_font_reduction and hasattr(font, 'path'):
        current_font_size = font.size
        while current_font_size > 10:  # Najmanj 10px
            # Preverimo, ali bi manjši font ustrezal
            all_fit = True
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=current_font)
                text_width = bbox[2] - bbox[0]
                if text_width > max_width:
                    all_fit = False
                    break

            if all_fit:
                break

            current_font_size -= 2
            try:
                current_font = ImageFont.truetype(font.path, current_font_size)
            except:
                break

        line_height = int(current_font_size * 1.2)
    elif needs_font_reduction and not hasattr(font, 'path'):
        # Če je default font, zmanjšamo line_height
        line_height = int(initial_line_height * 0.7)

    # Preverimo višino
    total_text_height = len(lines) * line_height

    if total_text_height > available_height:
        # Zmanjšamo line_height, če tekst ne stane po višini
        scale_factor = available_height / total_text_height
        if scale_factor < 1:
            line_height = int(line_height * scale_factor)

    # Preverimo še enkrat, da tekst ne presega spodaj
    final_y = y_offset + total_text_height
    if final_y > height - int(height * 0.05):
        # Prilagodimo y_offset, da se tekst ne presega
        y_offset = height - total_text_height - int(height * 0.05)
        y_offset = max(int(height * 0.02), y_offset)

    for i, line in enumerate(lines):
        # Izračunamo x pozicijo (sredinsko poravnano)
        bbox = draw.textbbox((0, 0), line, font=current_font)
        text_width = bbox[2] - bbox[0]
        x_position = (width - text_width) / 2

        y = y_offset + (i * line_height)

        # Preverimo, da y ne presega slike
        if y + line_height > height:
            break  # Če je vrstica zunaj slike, jo preskočimo

        # Narišemo obris
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x_position + adj_x, y + adj_y), line,
                             font=current_font, fill=outline_color)

        # Narišemo tekst
        draw.text((x_position, y), line, font=current_font, fill=text_color)


@app.route('/')
def index():
    """Prikažemo glavno stran"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_meme():
    """
    Obdelamo nalaganje slike in generiranje mema

    Koraki:
    1. Preverimo, ali je datoteka naložena
    2. Preverimo, ali je dovoljene vrste
    3. Shranimo datoteko
    4. Dodamo tekst na sliko
    5. Vrnemo memom kot sliko
    """
    try:
        # 1. Preverimo, ali je datoteka naložena
        if 'image' not in request.files:
            return "Napaka: Slika ni bila naložena", 400

        file = request.files['image']
        top_text = request.form.get('top_text', '')
        bottom_text = request.form.get('bottom_text', '')

        if file.filename == '':
            return "Napaka: Izbrana je prazna datoteka", 400

        # 2. Preverimo, ali je dovoljene vrste
        if not allowed_file(file.filename):
            return "Napaka: Nepodprta vrsta datoteke. Dovoljene so: png, jpg, jpeg, gif, bmp", 400

        # 3. Shranimo datoteko
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 4. Dodamo tekst na sliko
        meme_image = add_text_to_image(filepath, top_text, bottom_text)

        if meme_image is None:
            return "Napaka pri obdelavi slike", 500

        # 5. Vrnemo sliko
        img_io = io.BytesIO()
        meme_image.save(img_io, 'PNG', quality=85)
        img_io.seek(0)

        # Počistimo naloženo datoteko
        os.remove(filepath)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        print(f"Napaka pri generiranju mema: {e}")
        return f"Napaka pri generiranju mema: {e}", 500


@app.route('/health')
def health():
    """Zdravstveni check za Docker"""
    return "OK", 200


if __name__ == '__main__':
    # Nastavimo host na 0.0.0.0 za Docker
    app.run(host='0.0.0.0', port=5000, debug=False)