from pathlib import Path
import csv
import re
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime, date

course_date = "2026-10-22"
printed_signature = True
signature = ["Cullen Bengtson","Mei Stukes"]
titleA = ["National","National"]
titleB = ["NYLT Coordinator","CDC Coordinator"]
include_card = True
card_for = "NYLT Course Directors Conference"
card_course_code = "P71"
card_expires = True

root_path = "/Users/stevensmith/Documents/pythonCode/certmaker/"
IMAGE_FILE = Path(root_path+"NYLT CDC Certificate.jpg")
IMAGE_FILE2 = Path(root_path+"Scouting Trained Card.jpg")
CSV_FILE = Path(root_path+"2027 Fall NYLT CDC Graduates.csv")
FONT_FILE1 = Path(root_path+"StyleScript-Regular.ttf")
FONT_FILE2 = Path(root_path+"DoppioOne-Regular.ttf")
FONT_FILE3 = Path(root_path+"MomoSignature-Regular.ttf")
FONT_FILE4 = Path(root_path+"PTSerif-Regular.ttf")
FONT_FILE5 = Path(root_path+"PTSerif-Italic.ttf")
OUTPUT_DIR = Path(root_path+"certificates")
ZIP_FILE = Path(root_path+"certificates.zip")

# Recipient name placement, relative to the certificate image.
NAME_X = 0.50
NAME_Y = 0.635  # Centered above the horizontal line

# Recipient name placement, relative to the certificate image.
DATE_X = 0.50
DATE_Y = 0.08  # Centered above the horizontal line

SIGNATURE_X = [.275,.725]
SIGNATURE_Y = .823
def read_names(path):
    names = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            name = row[0].strip()
            council = row[1].strip()
            if name.lower() in {"name", "names"}:  # Ignore an optional header
                continue
            if council.lower() in {"council", "councils"}:  # Ignore an optional header
                continue
            names.append([name,council])
    return names

def safe_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', "_", name).strip().rstrip(".")
    return name or "certificate"

def add_to_image(img_num,font_size,font_file,draw_text,pos_x,pos_y,font_color="#000000"):
    global image,draw,image2,draw2

    size = font_size
    font = ImageFont.truetype(str(font_file), size)

    if img_num == 1: 
        img = image
        drw = draw
        aln = "center"
        x = round(img.width * pos_x)
        y = round(img.height * pos_y)
    else:
        img = image2
        drw = draw2
        txt_len = drw.textbbox((0, 0), draw_text, font=font, stroke_width=1)[2]
        x = pos_x + txt_len/2
        y = pos_y
        aln = "left"   

    while drw.textbbox((0, 0), draw_text, font=font, stroke_width=1)[2] > img.width * 0.82:
        size -= 1
        font = ImageFont.truetype(str(font_file), size)

    drw.text(
        (x, y),
        draw_text,
        font=font,
        fill=font_color,
        anchor="mm",
        align=aln
    )

    if img_num == 1: 
        image = img
        draw = drw
    else:
        image2 = img
        draw2 = drw


base = Image.open(IMAGE_FILE).convert("RGB")
base2 = Image.open(IMAGE_FILE2).convert("RGB")
names = read_names(CSV_FILE)

if not names:
    raise ValueError("No names found in names.csv")
if not FONT_FILE1.exists():
    raise FileNotFoundError("Put GreatVibes-Regular.ttf beside this script.")

OUTPUT_DIR.mkdir(exist_ok=True)
font2 = ImageFont.truetype(str(FONT_FILE2), 40)

with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as archive:
    for name,council in names:
        image = base.copy()
        draw = ImageDraw.Draw(image)

        #create certificate

        #add texts
        add_to_image(1,74,FONT_FILE1,name,NAME_X,NAME_Y,font_color="#173f69")
        
        c_date = datetime.strptime(course_date, "%Y-%m-%d")
        add_to_image(1,40,FONT_FILE2,c_date.strftime("%B %d, %Y"),DATE_X,DATE_Y)

        for i in range(2):
            if printed_signature == True:
                add_to_image(1,22,FONT_FILE3,signature[i],SIGNATURE_X[i],SIGNATURE_Y,font_color="#173f69")
            add_to_image(1,18,FONT_FILE4,signature[i],SIGNATURE_X[i],SIGNATURE_Y+.032)
            add_to_image(1,18,FONT_FILE4,titleA[i],SIGNATURE_X[i],SIGNATURE_Y+.058)
            add_to_image(1,18,FONT_FILE4,titleB[i],SIGNATURE_X[i],SIGNATURE_Y+.081)

        pdf_path = OUTPUT_DIR / f"{safe_filename(name)}.pdf"
        DPI = 150
        height_px = int(8.5 * DPI)
        width_px = int(11 * DPI)

        #create training card
        if include_card==True:
            image2 = base2.copy()
            ImageOps.pad(image2,(100,400),color="#FFFFFF")
            draw2 = ImageDraw.Draw(image2)

            add_to_image(2,32,FONT_FILE4,name,110,329,"#173f69")
            add_to_image(2,32,FONT_FILE4,card_for,116,432)
            add_to_image(2,32,FONT_FILE4,card_course_code,240,535)
            add_to_image(2,32,FONT_FILE4,council,170,617)
            if card_expires == True: 
                y = .296
                exp_date = c_date.replace(year=c_date.year + 2)
                add_to_image(2,32,FONT_FILE4,"X",96,756)
                add_to_image(2,32,FONT_FILE4,exp_date.strftime("%B %d, %Y"),270,757)
            else: 
                add_to_image(2,32,FONT_FILE4,"X",96,805)
            
            if printed_signature == True:
                add_to_image(2,32,FONT_FILE3,signature[0],185,885)
            
            image = [image.convert("RGB").resize((width_px, height_px)), image2.convert("RGB").resize((width_px, height_px))]
            image[0].save(pdf_path, save_all=True, append_images=image[1:])
        else:
            pdf_path = OUTPUT_DIR / f"{safe_filename(name)}.pdf"
            image.convert("RGB").resize((width_px, height_px)).save(pdf_path, save_all=True)


print(f"Created {len(names)} certificates in {ZIP_FILE}")