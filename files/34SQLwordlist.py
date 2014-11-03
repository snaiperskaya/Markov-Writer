import sqlite3
import random
import sys
import os
import time
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
    for i in swaps:
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


def prepstrlist(string):
    string = string.replace('\n',' ')
    string = string.replace(" '", " ")
    string = string.replace("' ", " ")
    rem = ['_', '*', '@', '(', ')', '[', ']', '{', '}', '\t', '"']
    for i in rem:
        string = string.replace(i, '')
    gap = ['.', ',', '!', '?', ';', ':', '&']
    for i in gap:
        string = string.replace(' ' + i, i)
    for i in gap:
        string = string.replace(i, i + ' ')
    for i in range(0,25):
        string = string.replace('  ',' ')
        string = string.replace('--','-')
    string = string.strip()
    lis = string.split(' ')
    return lis


def prepfilelist(txtfile):
    fi = open(txtfile, encoding='utf8', errors='replace')
    string = fi.read()
    return prepstrlist(string)

def buildLocalWordDicts(sfile):
    d3 = {}
    d2 = {}
    d1 = {}
    conn = sqlite3.connect(sfile)
    c = conn.cursor()
    c.execute("SELECT * FROM threeword")
    SQLthree = {}
    threetemp = c.fetchall()
    conn.close()
    for i in threetemp:
        d3[(i[0], i[1], i[2], i[3])] = int(i[4])
        d2[(i[1], i[2], i[3])] = int(i[4])
        d1[(i[2], i[3])] = int(i[4])
    return (d3, d2, d1)


### -------- 3RD GEN SQLITE BUILD VOODOO -------- ###

def runRead(txt, dthree):
    strlist = prepfilelist('toRead\\' + txt)
    print('Reading {}... {} words found!'.format(txt, len(strlist)))
    #try:
    dthree = read(strlist, dthree)
    return dthree
        #print('File {} has been read into word list!'.format(txt))
    #except:
        #print('ERROR while reading {}...'.format(txt))  


def read(strlist, dthree):
    prevword3 = '~start~'
    prevword2 = '~start~'
    prevword = '~start~'
    for i in strlist:
        #i = i.lstrip("\'").rstrip("\'") 
        try:
            dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), i)] = dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), i)] + 1
        except:
            dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), i)] = 1
        #print(i)
        if i[-1] in ['.','?','!'] and i.lower() not in ['mr.', 'mrs.', 'st.', 'rd.', 'ln.', 'ct.', 'dr.', 'prof.']:
            try:
                dthree[(prevword2.lower(), prevword.lower(), i.lower(), '~end~')] = dthree[(prevword2.lower(), prevword.lower(), i.lower(), '~end~')] + 1
            except:
                dthree[(prevword2.lower(), prevword.lower(), i.lower(), '~end~')] = 1
            prevword = '~start~'
            prevword2 = '~start~'
            prevword3 = '~start~'
        else:
            prevword3 = prevword2
            prevword2 = prevword
            prevword = i
    try:
        dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), '~end~')] = dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), '~end~')] + 1
    except:
        dthree[(prevword3.lower(), prevword2.lower(), prevword.lower(), '~end~')] = 1
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

def tryspeak(d3, d2, d1):
    done = False
    while done != True:
        try:
            words = speak(d3, d2, d1)
            done = True
        except:
            continue
    return words
    

def speak(d3, d2, d1, prevword3 = '~start', prevword2 = '~start~', prevword = '~start~', string = ''):
    if prevword == '~end~':
        return string.strip().capitalize()
    else:
        if prevword != '~start~':
            prevword = prevword.lower()
        lis = []
        for i in d3.keys():
            if (i[0], i[1], i[2]) == (prevword3, prevword2, prevword):
                lis.append((i[3], d3[i]))
        temp = []
        if len(lis) > 0:
            for i in lis:
                for k in range(0,i[1]):
                    temp.append(str(i[0]))
            word = temp[random.randint(0, len(temp)-1)]
        else:
            lis = []
            for i in d2.keys():
                if (i[0], i[1]) == (prevword2, prevword):
                    lis.append((i[2], d2[i]))
            temp = []
            if len(lis) > 0:
                for i in lis:
                    for k in range(0,i[1]):
                        temp.append(str(i[0]))
                word = temp[random.randint(0, len(temp)-1)]
            else:
                lis = []
                for i in d1.keys():
                    if i[0] == prevword:
                        lis.append((i[1], d1[i]))
                temp = []
                if len(lis) > 0:
                    for i in lis:
                        for k in range(0,i[1]):
                            temp.append(str(i[0]))
                    word = temp[random.randint(0, len(temp)-1)]         
        if word == '~end~':
            return string.strip().capitalize()
        string = string + ' ' + word
        return speak(d3, d2, d1, prevword2, prevword, word, string)


def paraGen(d3, d2, d1, numsentence, maxSentPara):
    novel = '\t' + tryspeak(d3, d2, d1)
    sen = 1
    for i in tqdm(range(0,numsentence - 1)):
        temp = tryspeak(d3, d2, d1)
        test = random.randint(sen, maxSentPara)
        if test == maxSentPara:
            novel = novel + '\n\n\t' + temp
            sen = 1
        else:
            novel = novel + ' ' + temp
            sen = sen + 1
    return novel


def novelize(sfile, txtfile, numchaps, minchapsennum = 10, maxchapsennum = 50, maxSentPara = 8):
    dicts = buildLocalWordDicts(sfile)
    d3 = dicts[0]
    d2 = dicts[1]
    d1 = dicts[2]
    print("Starting Novel write of {} chapters of {}-{} sentences each with paragraphs up to {} sentences long...".format(numchaps, minchapsennum, maxchapsennum, maxSentPara))
    chap = 1
    print('Chapter {} processing...'.format(chap))
    novel = '\t\t\t\tChapter 1\n\n\n' + paraGen(d3, d2, d1, random.randint(minchapsennum, maxchapsennum), maxSentPara)
    print('Chapter {} written!'.format(chap))
    while chap < numchaps:
        chap = chap + 1
        print('\nChapter {} processing...'.format(chap))
        novel = novel + '\n\n\n\t\t\t\tChapter {}\n\n\n'.format(chap) + paraGen(d3, d2, d1, random.randint(minchapsennum, maxchapsennum), maxSentPara)
        print('Chapter {} written!'.format(chap))
    novel = cleantext(novel)
    with open(txtfile, 'w', encoding='utf8') as f:
        f.write(novel)
    print('Novel written to {}'.format(txtfile))

   



if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    
    sfile = "F:\\sqllite\\threewordlist.snai" #Running SQLite file on a persistent RAMDisk
    buildDatabase(sfile)
    
    novelize(sfile, 'Output txts\\threetest03.txt', 4, maxchapsennum=100, maxSentPara=10)
    
    input()