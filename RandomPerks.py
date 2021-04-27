import sqlite3, random, base64, io
from flask import Flask, render_template
from PIL import Image, ImageFont, ImageDraw

app = Flask(__name__)


@app.route("/testbed/Random-Perks/")
def index():
    con = sqlite3.connect('perks.db')
    cur = con.cursor()
    
    cur.execute('SELECT * FROM perks')
    size = len(cur.fetchall())
    
    perk_ids = random.sample(range(size - 1), 4)
    perks = []
    for index, i in enumerate(perk_ids):
        perk_ids[index] = perk_ids[index] + 1
        cur.execute('SELECT perkName FROM perks WHERE perkID = ' + str(perk_ids[index]))
        perks.append(cur.fetchone()[0])
    print(perk_ids)
    print(perks)
    rows = cur.execute('SELECT img, perkName FROM perks WHERE perkID IN (' + str(perk_ids[0]) + ',' + str(perk_ids[1]) + ',' + str(perk_ids[2]) + ',' + str(perk_ids[3]) + ') ORDER BY perkName ASC').fetchall()
    print(rows)
    perk_1 = './images/perks/new/' + rows[0][0]
    perk_2 = './images/perks/new/' + rows[1][0]
    perk_3 = './images/perks/new/' + rows[2][0]
    perk_4 = './images/perks/new/' + rows[3][0]
    images = [Image.open(x) for x in [perk_1, perk_2, perk_3, perk_4]]
    
    font = ImageFont.truetype('Roboto-Light.ttf', 25)
    for index, i in enumerate(images):
        perk_text = rows[index][1]
        textw, texth = font.getsize(perk_text)
        image_editable = ImageDraw.Draw(images[index])
        image_editable.text(((300 - textw) / 2, 260), perk_text, (255, 255, 255), font=font)
    
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    
    new_im = Image.new('RGBA', (total_width, max_height))
    
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
        
    background = Image.open("./images/bg/1.png")
    background_w, background_h = background.size
    new_im_w, new_im_h = new_im.size
    offset = ((background_w - new_im_w) // 2, (background_h - new_im_h) // 2)
    background.paste(new_im, offset, new_im)
    buffer = io.BytesIO()
    background.save(buffer, format="PNG")
    encoded_img_data = base64.b64encode(buffer.getvalue())
    
    con.close()
    return render_template("page.html", img_data=encoded_img_data.decode('utf-8'))


if __name__ == "__main__":
    app.run()
