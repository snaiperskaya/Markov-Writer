import sqlite3
import random
import sys
import os
import time
import datetime
from tqdm import *


### -------- HELPER FUNCTIONS -------- ###

def cleantext(text):
    swaps = [
        ('i', 'I'),
        ('john', 'John'),
        ('sherlock', 'Sherlock'),
        ('holmes', 'Holmes'),
        ('mary', 'Mary'),
        ('frankenstein', 'Frankenstein'),
        ('dracula', 'Dracula'),
        ('new england', 'New England'),
        ('tom', 'Tom'),
        ('huck', 'Huck'),
        ('jim', 'Jim'),
        ('finn', 'Finn'),
        ('hercules', 'Hercules'),
        ('achilles', 'Achilles'),
        ('troy', 'Troy'),
        ('mars', 'Mars'),
        ('venus', 'Venus'),
        ('adrian','Adrian'),
        ('alice', 'Alice'),
        ('ophelia', 'Ophelia'),
        ('jonathan', 'Jonathan'),
        ('mr', 'Mr'),
        ('mrs', 'Mrs'),
        ('st', 'St'),
        ('jove', 'Jove'),
        ('christ', 'Christ'),
        ('jesus', 'Jesus'),
        ('jekyll', 'Jekyll'),
        ('hyde', 'Hyde'),
        ('dorian gray', 'Dorian Gray'),
        ('dorian', 'Dorian'),
        ('beowulf', 'Beowulf'),
        ('gregor', 'Gregor'),
        ('jane', 'Jane'),
        ('emma', 'Emma'),
        ('elizabeth', 'Elizabeth'),
        ('george', 'George'),
        ('mccarthy', 'McCarthy'),
        ('polly', 'Polly'),
        ('sid', 'Sid'),
        ('Mccarthy', 'McCarthy'),
        ('gulliver', 'Gulliver'),
        ('willett', 'Willett'),
        ('sympson', 'Sympson'),
        ('agamemnon', 'Agamemnon'),
        ('huckleberry', 'Huckleberry'),
        ('nicholas', 'Nicholas'),
        ('liverpool', 'Liverpool'),
        ('fogg', 'Fogg'),
        ('ulysses', 'Ulysses'),
        ('apollo', 'Apollo'),
        ('leucus', 'Leucus'),
        ('lucy', 'Lucy'),
        ('menestheus', 'Menestheus'),
        ('peteos', 'Peteos'),
        ('peleus', 'Peleus'),
        ('new york', 'New York')
    ]
    print('\nPost-processing text...\n')
    for i in tqdm(swaps):
        text = text.replace(' {} '.format(i[0]), ' {} '.format(i[1]))
        text = text.replace(" {}'".format(i[0]), " {}'".format(i[1]))
        text = text.replace(" {};".format(i[0]), " {};".format(i[1]))
        text = text.replace(" {},".format(i[0]), " {},".format(i[1]))
        text = text.replace(" {}:".format(i[0]), " {}:".format(i[1]))
        text = text.replace(" {}?".format(i[0]), " {}?".format(i[1]))
        text = text.replace(" {}!".format(i[0]), " {}!".format(i[1]))
        text = text.replace(" {}.".format(i[0]), " {}.".format(i[1]))
        text = text.replace(" {}-".format(i[0]), " {}-".format(i[1]))
    return text


def prepstrlist(oldstring):
    string = ''
    for i in oldstring:
        if ord(i) in range(32, 127):
            string = string + i
        else:
            string = string + ' '
    string = string.replace('\n',' ')
    string = string.replace(" '", " ")
    string = string.replace("' ", " ")
    rem = [' . ', ' , ', '_', '*', '@', '(', ')', '[', ']', '{', '}', '\t', '\"', '~', '<', '>', '+', '=', '^', '\`', '-']
    for i in rem:
        string = string.replace(i, ' ')
    gap = [',', '!', '?', ';', ':']
    for i in gap:
        string = string.replace(' ' + i, i)
    for i in gap:
        string = string.replace(i, i + ' ')
    for i in range(0,50):
        string = string.replace('  ',' ')
        string = string.replace('--','-')
    string = string.strip()
    lis = string.split(' ')
    pop = []
    for i in range(0, len(lis) - 1):
        if lis[i].strip() in ['', ' ', '.']:
            pop.append(i)
    pop.reverse()
    for i in pop:
        lis.pop(i)
    return lis


def prepfilelist(txtfile):
    fi = open(txtfile, encoding='utf8', errors='replace')
    string = fi.read()
    return prepstrlist(string)


def buildLocalWordDicts(sfile):
    d3 = {}
    d2 = {}
    d1 = {}
    print('Building in-memory dictionary....')
    conn = sqlite3.connect(sfile)
    c = conn.cursor()
    c.execute("SELECT * FROM threeword")
    SQLthree = {}
    threetemp = c.fetchall()
    conn.close()
    for i in tqdm(threetemp):
        try:
            d3[(i[0], i[1], i[2])].extend([(i[3], int(i[4]))])
        except:
            d3[(i[0], i[1], i[2])] = [(i[3], int(i[4]))]
        
        try:
            d2[(i[1], i[2])].extend([(i[3], int(i[4]))])
        except:
            d2[(i[1], i[2])] = [(i[3], int(i[4]))]        
        
        try:
            d1[(i[2])].extend([(i[3], int(i[4]))])
        except:
            d1[(i[2])] = [(i[3], int(i[4]))]
        
    return (d3, d2, d1)


def getNewFile(folder):
    filename = '\\NewText_' + datetime.datetime.now().isoformat('_')
    filename = filename.replace(':', '-')
    filename = filename.replace('.', '-')
    return folder + filename + '.txt'


### -------- 3RD GEN SQLITE BUILD VOODOO -------- ###

def runRead(txt, dthree):
    strlist = prepfilelist('toRead\\' + txt)
    print('Reading {}... {} words found!'.format(txt, len(strlist)))
    dthree = read(strlist, dthree)
    return dthree


def read(strlist, dthree):
    prevword3 = '~start~'
    prevword2 = '~start~'
    prevword = '~start~'
    senprev3 = '~start~'
    senprev2 = '~start~'
    senprev1 = '~start~'
    for i in strlist:
        if i.isupper():
            i = i.lower()
        try:
            dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), i)] = dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), i)] + 1
        except:
            dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), i)] = 1
        if senprev3 != prevword3:
            try:
                dthree[(senprev3.lower(), senprev2.lower(), senprev1.lower(), i)] = dthree[(senprev3.lower(), senprev2.lower(), senprev1.lower(), i)] + 1
            except:
                dthree[(senprev3.lower(), senprev2.lower(), senprev1.lower(), i)] = 1            
        if i[-1] in ['.','?','!'] and i.lower() not in ['mr.', 'mrs.', 'st.', 'rd.', 'ln.', 'ct.', 'dr.', 'prof.', 'mt.', 'm.', 'd.', 'etc.', 'ph.', 'hon.']:
            senprev1 = '~start~'
            senprev2 = '~start~'
            senprev3 = '~start~'
        else:
            senprev3 = senprev2
            senprev2 = senprev1
            senprev1 = i
        prevword3 = prevword2
        prevword2 = prevword
        prevword = i        
    return dthree


def buildDatabase(sfile, readPath = 'toRead'):
    if not os.path.exists(sfile):
        conn = sqlite3.connect(sfile)
        c = conn.cursor()
        c.execute('''CREATE TABLE threeword
                (word1 text, word2 text, word3 text, subword text, count)''')
        conn.close()
    filelist = os.listdir(path=readPath)
    dthree = {}
        
    for txt in filelist:
        dthree = runRead(txt, dthree)
    
    print('\nAll txt Documents in Memory...')
    
    conn = sqlite3.connect(sfile)
    c = conn.cursor()
    c.execute("SELECT * FROM threeword")
    SQLthree = {}
    threetemp = c.fetchall()
    print('\n\nEstablishing Existing Words for Three-Word Database Updates... ',)
    for i in threetemp:
        SQLthree[(i[0], i[1], i[2], i[3])] = i[4]
    threeupdate = []
    threenew = []
    for i in dthree.keys():
        try:
            count = SQLthree[i]
            threeupdate.append((i[0], i[1], i[2], i[3], dthree[i] + count))
        except:
            threenew.append((i[0], i[1], i[2], i[3], dthree[i]))
    print('Done!')
    print('\n\nProcessing Updated Three-Word Combinations to SQL Database {}... '.format(sfile),)
    c.executemany("""UPDATE threeword
                    SET count = ?
                    WHERE word1=? AND word2=? AND word3=? AND subword=?;""",threeupdate)
    print("Done!")
    print('\n\nAdding New Three-Word Combinations to SQL Database {}... '.format(sfile),)
    c.executemany("INSERT INTO threeword VALUES (?,?,?,?,?)",threenew)
    print("Done!\n\n")
    conn.commit()
    print('Three-Word Combinations Successfully Saved to {}!\n\n'.format(sfile))
    conn.close()
    print('All txt files read!')
    

### -------- 3RD GEN SQLITE WRITE VOODOO -------- ###

def gen3Word(d3, d2, d1, prevword3 = '~start', prevword2 = '~start~', prevword = '~start~'):
    if prevword != '~start~':
        prevword = prevword.lower()
    lis = []
    try:
        lis = d3[(prevword3, prevword2, prevword)]
    except:
        lis = []
    temp = []
    if len(lis) > 0:
        for i in lis:
            for k in range(0,i[1]):
                temp.append(str(i[0]))
        word = temp[random.randint(0, len(temp)-1)]
        return (prevword2, prevword, word) 
    else:
        return gen2Word(d2, d1, prevword2, prevword)   


def gen2Word(d2, d1, prevword2 = '~start~', prevword = '~start~'):
    if prevword != '~start~':
        prevword = prevword.lower()    
    lis = []
    try:
        lis = d2[(prevword2, prevword)]
    except:
        lis = []
    temp = []
    if len(lis) > 0:
        for i in lis:
            for k in range(0,i[1]):
                temp.append(str(i[0]))
        word = temp[random.randint(0, len(temp)-1)]
        return (prevword2, prevword, word) 
    else:
        return gen1Word(d1, prevword2, prevword)        


def gen1Word(d1, prevword2 = '~start~', prevword = '~start~'):
    if prevword != '~start~':
        prevword = prevword.lower()       
    lis = []
    try:
        lis = d1[(prevword)]
    except:
        lis = []
    temp = []
    if len(lis) > 0:
        for i in lis:
            for k in range(0,i[1]):
                temp.append(str(i[0]))
        word = temp[random.randint(0, len(temp)-1)]
    return (prevword2, prevword, word)     


def genWord(d3, d2, d1, prevword3 = '~start', prevword2 = '~start~', prevword = '~start~', wordtest = 3):
    if wordtest == 3:
        return gen3Word(d3, d2, d1, prevword3, prevword2, prevword)
    elif wordtest == 2:
        return gen2Word(d2, d1, prevword2, prevword)
    elif wordtest == 1:
        return gen1Word(d1, prevword2, prevword)
    else:
        return gen3Word(d3, d2, d1, prevword3, prevword2, prevword)


def paraGen(d3, d2, d1, numsentence, maxSentPara, wordtest = 3):
    print("Generating {} sentences...".format(numsentence))
    words = genWord(d3, d2, d1, wordtest=wordtest)
    word = words[2]
    novel = '\t' + word.capitalize()
    totsen = 0
    sen = 1
    senup = False
    while totsen < numsentence:
        words = genWord(d3, d2, d1, words[0], words[1], words[2], wordtest=wordtest)
        word = words[2]       
        if senup == True:
            test = random.randint(sen, maxSentPara)
            if test == maxSentPara:
                novel = novel + '\n\n\t' + word.capitalize()
                sen = 1
            else:
                novel = novel + ' ' + word.capitalize()
            senup = False
        else:
            novel = novel + ' ' + word
        if word[-1] in ['.','?','!'] and word.lower() not in ['mr.', 'mrs.', 'st.', 'rd.', 'ln.', 'ct.', 'dr.', 'prof.', 'mt.', 'm.', 'd.', 'etc.', 'ph.', 'hon.']:
            sen = sen + 1
            totsen = totsen + 1
            senup = True
    return novel


def novelize(dicts, txtfile, numchaps, minchapsennum = 10, maxchapsennum = 50, maxSentPara = 8, wordtest = 3):
    d3 = dicts[0]
    d2 = dicts[1]
    d1 = dicts[2]
    print("\nStarting Novel write of {} chapters of {}-{} sentences each with paragraphs up to {} sentences long...\n".format(numchaps, minchapsennum, maxchapsennum, maxSentPara))
    chap = 1
    print('Chapter {} processing...'.format(chap))
    novel = '\t\t\t\tChapter 1\n\n\n' + paraGen(d3, d2, d1, random.randint(minchapsennum, maxchapsennum), maxSentPara, wordtest)
    print('Chapter {} written!\n'.format(chap))
    while chap < numchaps:
        chap = chap + 1
        print('\nChapter {} processing...'.format(chap))
        novel = novel + '\n\n\n\t\t\t\tChapter {}\n\n\n'.format(chap) + paraGen(d3, d2, d1, random.randint(minchapsennum, maxchapsennum), maxSentPara, wordtest)
        print('Chapter {} written!\n'.format(chap))
    novel = cleantext(novel)
    with open(txtfile, 'w', encoding='utf8') as f:
        f.write(novel)
    print('Novel written to {}\n'.format(txtfile))

   
def fullNovelize(sfile, txtfile, numchaps, minchapsennum = 10, maxchapsennum = 50, maxSentPara = 8, wordtest = 3):
    dicts = buildLocalWordDicts(sfile)
    novelize(dicts, txtfile, numchaps, minchapsennum, maxchapsennum, maxSentPara, wordtest)


if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    
    #sfile = "doublenewthreewordlist.snai"
    sfile = "F:\\sqllite\\newnewthreewordlist.snai" #Running SQLite file on a persistent RAMDisk
    #buildDatabase(sfile) #Uncomment to build a new database
    dicts = buildLocalWordDicts(sfile)
    for i in range(0,5):
        novelize(dicts, getNewFile('D:\\Google Drive\\Generated Texts'), 4, minchapsennum=1, maxchapsennum=100, maxSentPara=10)
    #novelize(sfile, 'Output txts\\newtwo03.txt', 3, minchapsennum=1, maxchapsennum=100, maxSentPara=10, wordtest=2)
    
    input()