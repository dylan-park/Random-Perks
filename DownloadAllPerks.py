import requests, urllib.request, sqlite3, os
from bs4 import BeautifulSoup
from PIL import Image

# create empty lists
perks, perks_survivors, imagepages, survivors, filenames, images = [], [], [], ['All'], [], []


# 
def RipPerks(): 
    # create soup of survivors wiki, get survivor names and perk links
    soup = BeautifulSoup(requests.get('https://deadbydaylight.fandom.com/wiki/Survivors').content, 'html.parser')
    survivor_name_soup = soup.find(class_='mw-parser-output').findAll('div')[4].findAll('div', attrs={'style': 'display: inline-block; text-align:center; margin: 10px'})
    perk_link_soup = soup.find(class_='wikitable sortable').find('tbody').findAll(class_='image')
    perks_survivors_soup = soup.find(class_='wikitable sortable').findAll('th')
    
    # loop through survivor_name_soup, fill survivors list
    for i in survivor_name_soup:
        survivors.append(i.find('a').get('title'))
    print(survivors)
    
    # loop through perks_survivors_soup, fill perks_survivors list
    for i in perks_survivors_soup:
        # if perk is for all, set all
        if (i.contents[0] == 'All\n'):
            perks_survivors.append('All Survivors')
        # else if perk is for specific survivor
        elif (i.find('a', attrs={'class': 'mw-redirect'}) is not None):
            # if name is david, set full name (avoid David King/David Tapp collision)
            if (i.find('a', attrs={'class': 'mw-redirect'}).get('title') == 'David'):
                perks_survivors.append('David King')
            # else get survivor name
            else:
                perks_survivors.append(i.find('a', attrs={'class': 'mw-redirect'}).get('title'))
    print(perks_survivors)
    
    # loop through perk_link_soup, fill lists of perks, image links, and file names
    for i in perk_link_soup:
        perks.append(i.get('title')[:-2])
        imagepages.append('https://deadbydaylight.fandom.com' + i.get('href'))
        filenames.append(('https://deadbydaylight.fandom.com' + i.get('href')).split('_')[-1])
    print(perks)
    print(imagepages)
    print(filenames)
    
    # loop through image link list, get direct links to the images
    for i in imagepages:
        soup_image = BeautifulSoup(requests.get(i).content, 'html.parser')
        div = soup_image.find(class_='fullMedia')
        images.append(div.find('a').get('href'))
    print(images)
    
    # download each image link to the hard drive
    counter = 0
    perksfile = open('perks.txt', 'a')
    for i in images:
        urllib.request.urlretrieve(i, './images/perks/' + filenames[counter])
        perksfile.write(perks[counter] + '\n')
        counter += 1


def BuildPerks():
    directory = os.fsencode('./images/perks/')
    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if os.path.isdir(path):
            # skip directories
            continue
        filename = os.fsdecode(file)
    
        background = Image.open('./images/very_rare.png')
        background_w, background_h = background.size
        overlay = Image.open('./images/perks/' + filename)
        overlay_w, overlay_h = overlay.size
        
        background = background.convert('RGBA')
        overlay = overlay.convert('RGBA')
        offset = ((background_w - overlay_w) // 2, (background_h - overlay_h) // 2)
        
        background.paste(overlay, offset, overlay)
        background.save('./images/perks/new/' + filename)
        
        background.close()
        overlay.close()
        print('Created ' + filename)


def FillDatabase():
    con = sqlite3.connect('perks.db')
    cur = con.cursor()
    
    print('Inserting into survivors table')
    for index, i in enumerate(survivors):
        cur.execute('INSERT OR IGNORE INTO survivors (name) VALUES (?)', (i,))
        con.commit()
    
    print('Inserting into perks table')
    for index, i in enumerate(perks):
        perk_id = cur.execute('SELECT survivorID FROM survivors WHERE name LIKE ?;', ('%' + perks_survivors[index] + '%',)).fetchone()[0]
        cur.execute('INSERT OR IGNORE INTO perks (perkName, survivorID, img) VALUES (?, ?, ?)', (i, perk_id, filenames[index],))
        con.commit()
    con.close()
    
    
RipPerks()
BuildPerks()
FillDatabase()
