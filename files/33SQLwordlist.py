import sqlite3
import random
import sys
import os
import threading
import time


def prepstrlist(string):
    string = string.replace('\n',' ')
    for i in range(0,10):
        string = string.replace('  ',' ')
    string.strip('()[]{}')
    string = string.strip()
    lis = string.split(' ')
    return lis


def prepfilelist(txtfile):
    fi = open(txtfile)
    string = fi.read()
    return prepstrlist(string)
    

def appendword(key, appword):
    conn = sqlite3.connect(sfile)
    conn.isolation_level = None
    done = False
    while done != True:
        try:
            c = conn.cursor()
            t2 = (key.lower(),appword)
            c.execute("SELECT count FROM words WHERE word=? AND subword=?",t2)
            try:
                count = c.fetchall()[0][0]
                t1 = (int(count) + 1,key,appword)
                
                c.execute("""UPDATE words
                SET count = ?
                WHERE word=? AND subword=?;""",t1)
                
            except:
                c.execute("INSERT INTO words VALUES (?,?,?)",(key.lower(),appword,1))
            done = True
        except:
            continue   
    conn.close()
    
    
def read(strlist):
    prevword = '~start~'
    for i in strlist:
        appendword(prevword, i)
        if i[-1] in ['.','?','!']:
            appendword(i, '~end~')
            prevword = '~start~'
        else:
            prevword = i
    appendword(prevword, '~end~')

    
def speak(prevword = '~start~', string = ''):
    try:
        if prevword == '~end~':
            return string.strip().capitalize()
        else:
            if prevword != '~start~':
                prevword = prevword.lower()
            conn = sqlite3.connect(sfile)
            c = conn.cursor()
            t = (prevword,)
            c.execute("SELECT * FROM words WHERE word=?",t)
            lis = c.fetchall()
            conn.close()
            temp = []
            for i in lis:
                for k in range(0,i[2]):
                    temp.append(str(i[1]))
            word = temp[random.randint(0, len(temp)-1)]
            if word == '~end~':
                return string.strip().capitalize()
            string = string + ' ' + word
            return speak(word, string)
    except:
        pass

    
def runRead(txt):
    strlist = prepfilelist('toRead\\' + txt)
    print('Starting read of {}...'.format(txt))
    try:
        read(strlist)
        print('File {} has been read into word list!'.format(txt))
    except:
        print('ERROR while reading {}...'.format(txt))    

def novelize(numsentence, txtfile, maxSentPara = 8):
    novel = '\t' + speak()
    sen = 1
    for i in range(0,numsentence - 1):
        temp = speak()
        test = random.randint(sen, maxSentPara)
        if test == maxSentPara:
            novel = novel + '\n\t' + temp
            sen = 1
        else:
            novel = novel + ' ' + temp
            sen = sen + 1
    with open(txtfile, 'w') as f:
        f.write(novel)

    
if __name__ == '__main__':
    
    sfile = 'wordlist.snai'
    
    if not os.path.exists(sfile):
        conn = sqlite3.connect(sfile)
        c = conn.cursor()
        c.execute('''CREATE TABLE words
                (word text, subword text, count)''')
        conn.close()
    
    sys.setrecursionlimit(5000)
    
    filelist = os.listdir(path='toRead')
    
    readThreads = []
    
    for txt in filelist:
        readThreads.append(threading.Thread(target=runRead, args = (txt,)))
    
    for thread in readThreads:
        thread.start()
        
    for thread in readThreads:
        thread.join()    
    
    print('All txt files read!')