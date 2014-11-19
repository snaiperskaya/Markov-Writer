import sqlite3
import random
import sys
import os
import time
import datetime
from tqdm import *

nonSenEnds = ['mr.', 'mrs.', 'st.', 'rd.', 'ln.', 'ct.', 'dr.', 'prof.', 'mt.', 'etc.', 'ph.', 'hon.', 'seq.', 'a.', 'b.', 'c.', 'd.', 'e.', 'f.', 'g.', 'h.', 'j.', 'k.', 'l.', 'm.', 'n.', 'o.', 'p.', 'q.', 'r.', 's.', 't.', 'u.', 'v.', 'w.', 'x.', 'y.', 'z.']

genWeights = [2, 3, 4, 5, 2, 3, 4, 5, 3, 4, 5, 4, 5, 5, 5, 4, 3, 5, 4, 5]

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
    d5 = {}
    d4 = {}
    d3 = {}
    d2 = {}
    d1 = {}
    print('Building in-memory dictionary....')
    conn = sqlite3.connect(sfile)
    c = conn.cursor()
    c.execute("SELECT * FROM words")
    SQL = {}
    wordtemp = c.fetchall()
    conn.close()
    for i in tqdm(wordtemp):
        try:
            d5[(i[0], i[1], i[2], i[3], i[4])].extend([(i[5], int(i[6]))])
        except:
            d5[(i[0], i[1], i[2], i[3], i[4])] = [(i[5], int(i[6]))]        
        
        try:
            d4[(i[1], i[2], i[3], i[4])].extend([(i[5], int(i[6]))])
        except:
            d4[(i[1], i[2], i[3], i[4])] = [(i[5], int(i[6]))]        
        
        try:
            d3[(i[2], i[3], i[4])].extend([(i[5], int(i[6]))])
        except:
            d3[(i[2], i[3], i[4])] = [(i[5], int(i[6]))]
        
        try:
            d2[(i[3], i[4])].extend([(i[5], int(i[6]))])
        except:
            d2[(i[3], i[4])] = [(i[5], int(i[6]))]        
        
        try:
            d1[(i[4])].extend([(i[5], int(i[6]))])
        except:
            d1[(i[4])] = [(i[5], int(i[6]))]
        
    return (d5, d4, d3, d2, d1)


def getNewFile(folder):
    filename = '\\NewText_' + datetime.datetime.now().isoformat('_')
    filename = filename.replace(':', '-')
    filename = filename.replace('.', '-')
    return folder + filename + '.txt'


### -------- 3RD GEN SQLITE BUILD VOODOO -------- ###

def runRead(txt, dwords):
    strlist = prepfilelist('toRead\\' + txt)
    print('Reading {}... {} words found!'.format(txt, len(strlist)))
    dwords = read(strlist, dwords)
    return dwords


def read(strlist, dwords):
    prevword5 = '~start~'
    prevword4 = '~start~'
    prevword3 = '~start~'
    prevword2 = '~start~'
    prevword = '~start~'
    senprev5 = '~start~'
    senprev4 = '~start~'
    senprev3 = '~start~'
    senprev2 = '~start~'
    senprev1 = '~start~'
    for i in strlist:
        if i.isupper():
            i = i.lower()
        try:
            dwords[(prevword5.lower(), prevword4.lower(), prevword3.lower(), prevword2.lower(), prevword.lower(), i)] = dwords[(prevword3.lower(), prevword2.lower(), prevword.lower(), i)] + 1
        except:
            dwords[(prevword5.lower(), prevword4.lower(), prevword3.lower(), prevword2.lower(), prevword.lower(), i)] = 1
        if senprev5 != prevword5:
            try:
                dwords[(senprev5.lower(), senprev4.lower(), senprev3.lower(), senprev2.lower(), senprev1.lower(), i)] = dwords[(senprev5.lower(), senprev4.lower(), senprev3.lower(), senprev2.lower(), senprev1.lower(), i)] + 1
            except:
                dwords[(senprev5.lower(), senprev4.lower(), senprev3.lower(), senprev2.lower(), senprev1.lower(), i)] = 1            
        if i[-1] in ['.','?','!'] and i.lower() not in nonSenEnds:
            senprev1 = '~start~'
            senprev2 = '~start~'
            senprev3 = '~start~'
            senprev4 = '~start~'
            senprev5 = '~start~'
        else:
            senprev5 = senprev4
            senprev4 = senprev3
            senprev3 = senprev2
            senprev2 = senprev1
            senprev1 = i
        prevword5 = prevword4
        prevword4 = prevword3
        prevword3 = prevword2
        prevword2 = prevword
        prevword = i
    return dwords


def buildDatabase(sfile, readPath = 'toRead'):
    if not os.path.exists(sfile):
        conn = sqlite3.connect(sfile)
        c = conn.cursor()
        c.execute('''CREATE TABLE words
                (word1 text, word2 text, word3 text, word4 text, word5 text, subword text, count)''')
        conn.close()
    filelist = os.listdir(path=readPath)
    dwords = {}
        
    for txt in filelist:
        dwords = runRead(txt, dwords)
    
    print('\nAll txt Documents in Memory...')
    
    conn = sqlite3.connect(sfile)
    c = conn.cursor()
    c.execute("SELECT * FROM words")
    SQL = {}
    wordtemp = c.fetchall()
    print('\n\nEstablishing Existing Words for Word Database Updates... ',)
    for i in wordtemp:
        SQL[(i[0], i[1], i[2], i[3], i[4], i[5])] = i[6]
    wordupdate = []
    wordnew = []
    for i in dwords.keys():
        try:
            count = SQL[i]
            wordupdate.append((i[0], i[1], i[2], i[3], d[4], d[5], dwords[i] + count))
        except:
            wordnew.append((i[0], i[1], i[2], i[3], i[4], i[5], dwords[i]))
    print('Done!')
    print('\n\nProcessing Updated Word Combinations to SQL Database {}... '.format(sfile),)
    c.executemany("""UPDATE words
                    SET count = ?
                    WHERE word1=? AND word2=? AND word3=? AND word4=? AND word5=? AND subword=?;""",wordupdate)
    print("Done!")
    print('\n\nAdding New Word Combinations to SQL Database {}... '.format(sfile),)
    c.executemany("INSERT INTO words VALUES (?,?,?,?,?,?,?)",wordnew)
    print("Done!\n\n")
    conn.commit()
    print('Word Combinations Successfully Saved to {}!\n\n'.format(sfile))
    conn.close()
    print('All txt files read!')
    

### -------- 3RD GEN SQLITE WRITE VOODOO -------- ###

def gen5Word(d5, d4, d3, d2, d1, prevword5 = '~start', prevword4 = '~start~', prevword3 = '~start', prevword2 = '~start~', prevword = '~start~'):
    if prevword != '~start~':
        prevword = prevword.lower()
    lis = []
    try:
        lis = d5[(prevword5, prevword4, prevword3, prevword2, prevword)]
    except:
        lis = []
    temp = []
    if len(lis) > 0:
        for i in lis:
            for k in range(0,i[1]):
                temp.append(str(i[0]))
        word = temp[random.randint(0, len(temp)-1)]
        return (prevword4, prevword3, prevword2, prevword, word) 
    else:
        return gen4Word(d4, d3, d2, d1, prevword4, prevword3, prevword2, prevword) 


def gen4Word(d4, d3, d2, d1, prevword4 = '~start~', prevword3 = '~start', prevword2 = '~start~', prevword = '~start~'):
    if prevword != '~start~':
        prevword = prevword.lower()
    lis = []
    try:
        lis = d4[(prevword4, prevword3, prevword2, prevword)]
    except:
        lis = []
    temp = []
    if len(lis) > 0:
        for i in lis:
            for k in range(0,i[1]):
                temp.append(str(i[0]))
        word = temp[random.randint(0, len(temp)-1)]
        return (prevword4, prevword3, prevword2, prevword, word) 
    else:
        return gen3Word(d3, d2, d1, prevword4, prevword3, prevword2, prevword) 


def gen3Word(d3, d2, d1, prevword4 = '~start~', prevword3 = '~start', prevword2 = '~start~', prevword = '~start~'):
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
        return (prevword4, prevword3, prevword2, prevword, word) 
    else:
        return gen2Word(d2, d1, prevword4, prevword3, prevword2, prevword)   


def gen2Word(d2, d1, prevword4 = '~start~', prevword3 = '~start', prevword2 = '~start~', prevword = '~start~'):
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
        return (prevword4, prevword3, prevword2, prevword, word) 
    else:
        return gen1Word(d1, prevword4, prevword3, prevword2, prevword)        


def gen1Word(d1, prevword4 = '~start~', prevword3 = '~start', prevword2 = '~start~', prevword = '~start~'):
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
    return (prevword4, prevword3, prevword2, prevword, word)     


def genWord(d5, d4, d3, d2, d1, prevword5 = '~start~', prevword4 = '~start', prevword3 = '~start', prevword2 = '~start~', prevword = '~start~'):
    wordtest = genWeights[random.randint(0, len(genWeights)-1)]
    if wordtest == 5:
        return gen5Word(d5, d4, d3, d2, d1, prevword5, prevword4, prevword3, prevword2, prevword)
    elif wordtest == 4:
        return gen4Word(d4, d3, d2, d1, prevword4, prevword3, prevword2, prevword)    
    elif wordtest == 3:
        return gen3Word(d3, d2, d1, prevword4, prevword3, prevword2, prevword)
    elif wordtest == 2:
        return gen2Word(d2, d1, prevword4, prevword3, prevword2, prevword)
    elif wordtest == 1:
        return gen1Word(d1, prevword4, prevword3, prevword2, prevword)
    else:
        return gen5Word(d5, d4, d3, d2, d1, prevword5, prevword4, prevword3, prevword2, prevword)


def paraGen(d5, d4, d3, d2, d1, numsentence, maxSentPara):
    print("Generating {} sentences...".format(numsentence))
    words = genWord(d5, d4, d3, d2, d1)
    word = words[4]
    novel = '\t' + word.capitalize()
    totsen = 0
    sen = 1
    senup = False
    while totsen < numsentence:
        words = genWord(d5, d4, d3, d2, d1, words[0], words[1], words[2], words[3], words[4])
        word = words[4]       
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
        if word[-1] in ['.','?','!'] and word.lower() not in nonSenEnds:
            sen = sen + 1
            totsen = totsen + 1
            senup = True
    return novel


def novelize(dicts, txtfile, numchaps, minchapsennum = 10, maxchapsennum = 50, maxSentPara = 8):
    d5 = dicts[0]
    d4 = dicts[1]
    d3 = dicts[2]
    d2 = dicts[3]
    d1 = dicts[4]
    print("\nStarting Novel write of {} chapters of {}-{} sentences each with paragraphs up to {} sentences long...\n".format(numchaps, minchapsennum, maxchapsennum, maxSentPara))
    chap = 1
    print('Chapter {} processing...'.format(chap))
    novel = '\t\t\t\tChapter 1\n\n\n' + paraGen(d5, d4, d3, d2, d1, random.randint(minchapsennum, maxchapsennum), maxSentPara)
    print('Chapter {} written!\n'.format(chap))
    while chap < numchaps:
        chap = chap + 1
        print('\nChapter {} processing...'.format(chap))
        novel = novel + '\n\n\n\t\t\t\tChapter {}\n\n\n'.format(chap) + paraGen(d5, d4, d3, d2, d1, random.randint(minchapsennum, maxchapsennum), maxSentPara)
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
    
    testFiles = 'D:\\Google Drive\\Generated Texts'
    genBooks = 'Book Runs'
    
    #sfile = "5wordlist.snai"
    sfile = "F:\\sqllite\\5wordlist.snai" #Running SQLite file on a persistent RAMDisk
    #buildDatabase(sfile) #Uncomment to build a new database
    dicts = buildLocalWordDicts(sfile)
    for i in range(0,5):
        novelize(dicts, getNewFile(testFiles), 4, minchapsennum=1, maxchapsennum=100, maxSentPara=10)
    for i in range(0,5):
        novelize(dicts, getNewFile(genBooks), 16, minchapsennum=1, maxchapsennum=150, maxSentPara=12)
    input()