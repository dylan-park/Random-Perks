import sqlite3, random, base64, io
from flask import Flask, render_template, request
from PIL import Image, ImageFont, ImageDraw

app = Flask(__name__, static_url_path="/testbed/Random-Perks/static", static_folder="static")


@app.route('/testbed/Random-Perks/')
def index():
    # initiate sqlite
    con = sqlite3.connect('perks.db')
    cur = con.cursor()
    
    # get query keys (aka survivorIDs)
    query = request.args.to_dict().keys()
    
    # get all current survivors in a list (for menu)
    cur.row_factory = lambda cursor, row: row[0]
    survivors = cur.execute('SELECT name FROM survivors').fetchall()
    cur.row_factory = None
    
    # if no query, assume all survivors
    if not query:
        perk_ids = [*cur.execute('SELECT perkID FROM perks').fetchall()]
        perk_ids = list(sum(perk_ids, ()))
        # if query is empty, fill with all survivors for page menu saving
        query = list(range(1, len(survivors) + 1))
    # else get specific survivor perks
    else:
        text = ''
        # build extra sql query
        for i in query:
            text = text + 'survivorID = ' + i + ' OR '
        text = text[:-4]
        
        perk_ids = [*cur.execute('SELECT perkID FROM perks WHERE ' + text).fetchall()]
        perk_ids = list(sum(perk_ids, ()))
    
    # select 4 random perk_ids from list
    random_perks = random.sample(perk_ids, 4)
    print(random_perks)
    
    # build rows list with img name and perk name
    rows = cur.execute('SELECT img, perkName FROM perks WHERE perkID IN (' + str(random_perks[0]) + ',' + str(random_perks[1]) + ',' + str(random_perks[2]) + ',' + str(random_perks[3]) + ') ORDER BY perkName ASC').fetchall()
    print(rows)
    
    # set the 4 perk images
    perk_1 = './static/images/perks/new/' + rows[0][0]
    perk_2 = './static/images/perks/new/' + rows[1][0]
    perk_3 = './static/images/perks/new/' + rows[2][0]
    perk_4 = './static/images/perks/new/' + rows[3][0]
    images = [Image.open(x) for x in [perk_1, perk_2, perk_3, perk_4]]
    
    # draw perk names on perk images
    font = ImageFont.truetype('Roboto-Light.ttf', 25)
    for index, i in enumerate(images):
        perk_text = rows[index][1]
        textw, texth = font.getsize(perk_text)
        image_editable = ImageDraw.Draw(images[index])
        image_editable.text(((300 - textw) / 2, 260), perk_text, (255, 255, 255), font=font)
    
    # get image data
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGBA', (total_width, max_height))
    
    # set 4 perk images in a row w/ offset
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
        
    # apply images over background and prepare to handoff to html
    background = Image.open('./static/images/bg/1.png')
    background_w, background_h = background.size
    new_im_w, new_im_h = new_im.size
    offset = ((background_w - new_im_w) // 2, (background_h - new_im_h) // 2)
    background.paste(new_im, offset, new_im)
    buffer = io.BytesIO()
    background.save(buffer, format='PNG')
    encoded_img_data = base64.b64encode(buffer.getvalue())
    
    # convert query to int for ease of computation
    query = [int(i) for i in query]
    
    # close sqlite connection and handoff image to html
    con.close()
    return render_template('page.html', survivors_import=survivors, query_import=list(query), img_data=encoded_img_data.decode('utf-8'))


if __name__ == '__main__':
    app.run()
