import sqlite3
import random
import sys
import os
import threading
import time
from tqdm import *
from multiprocessing import Process, Manager, set_start_method


def prepstrlist(string):
    string = string.replace('\n',' ')
    string = string.replace('"', '')
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
    

def appendoneword(sfile, key, appword):
    conn = sqlite3.connect(sfile)
    conn.isolation_level = None
    done = False
    while done != True:
        try:
            c = conn.cursor()
            t2 = (key.lower(),appword)
            c.execute("SELECT count FROM oneword WHERE word=? AND subword=?",t2)
            try:
                count = c.fetchall()[0][0]
                t1 = (int(count) + 1,key,appword)
                
                c.execute("""UPDATE oneword
                SET count = ?
                WHERE word=? AND subword=?;""",t1)
                
            except:
                c.execute("INSERT INTO oneword VALUES (?,?,?)",(key.lower(),appword,1))
            done = True
        except:
            continue   
    conn.close()

    
def appendtwoword(sfile, key1, key2, appword):
    conn = sqlite3.connect(sfile)
    conn.isolation_level = None
    done = False
    while done != True:
        try:
            c = conn.cursor()
            t2 = (key1.lower(),key2.lower(),appword)
            c.execute("SELECT count FROM twoword WHERE word1=? AND word2=? AND subword=?",t2)
            try:
                count = c.fetchall()[0][0]
                t1 = (int(count) + 1,key1,key2,appword)
                
                c.execute("""UPDATE twoword
                SET count = ?
                WHERE word1=? AND word2=? AND subword=?;""",t1)
                
            except:
                c.execute("INSERT INTO twoword VALUES (?,?,?,?)",(key1.lower(),key2.lower(),appword,1))
            done = True
        except:
            continue   
    conn.close()
    
    
def read(sfile, strlist):
    prevword2 = '~start~'
    prevword = '~start~'
    for i in strlist:
        appendoneword(sfile, prevword, i)
        appendtwoword(sfile, prevword2, prevword, i)
        if i[-1] in ['.','?','!']:
            appendoneword(sfile, i, '~end~')
            appendtwoword(sfile, prevword, i, '~end~')
            prevword = '~start~'
            prevword2 = '~start~'
        else:
            prevword2 = prevword
            prevword = i
    appendoneword(sfile, prevword, '~end~')
    appendtwoword(sfile, prevword2, prevword, '~end~')


def readProc(strlist, done, dtwo):
    prevword2 = '~start~'
    prevword = '~start~'
    for i in strlist:
        try:
            done[(prevword.lower(), i)] = done[(prevword.lower(), i)] + 1
        except:
            done[(prevword.lower(), i)] = 1
            
        try:
            dtwo[(prevword2.lower(), prevword.lower(), i)] = dtwo[(prevword2.lower(), prevword.lower(), i)] + 1
        except:
            dtwo[(prevword2.lower(), prevword.lower(), i)] = 1

        if i[-1] in ['.','?','!']:
            try:
                done[(i, '~end~')] = done[(i, '~end~')] + 1
            except:
                done[(i, '~end~')] = 1
            try:
                dtwo[(prevword.lower(), i, '~end~')] = dtwo[(prevword.lower(), i, '~end~')] + 1
            except:
                dtwo[(prevword.lower(), i, '~end~')] = 1
            prevword = '~start~'
            prevword2 = '~start~'
        else:
            prevword2 = prevword
            prevword = i
    try:
        done[(prevword, '~end~')] = done[(prevword, '~end~')] + 1
    except:
        done[(prevword, '~end~')] = 1
    try:
        dtwo[(prevword2, prevword, '~end~')] = dtwo[(prevword2, prevword, '~end~')] + 1
    except:
        dtwo[(prevword2, prevword, '~end~')] = 1    
    
    
def onespeak(sfile, prevword = '~start~', string = ''):
    try:
        if prevword == '~end~':
            return string.strip().capitalize()
        else:
            if prevword != '~start~':
                prevword = prevword.lower()
            conn = sqlite3.connect(sfile)
            c = conn.cursor()
            t = (prevword,)
            c.execute("SELECT * FROM oneword WHERE word=?",t)
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
            return onespeak(sfile, word, string)
    except:
        pass


def twospeak(sfile, prevword2 = '~start~', prevword = '~start~', string = ''):
    #try:
    if prevword == '~end~':
        return string.strip().capitalize()
    else:
        if prevword != '~start~':
            prevword = prevword.lower()
        conn = sqlite3.connect(sfile)
        c = conn.cursor()
        t = (prevword2,prevword)
        c.execute("SELECT * FROM twoword WHERE word1=? AND word2=?",t)
        lis = c.fetchall()
        conn.close()
        temp = []
        if len(lis) > 0:
            for i in lis:
                for k in range(0,i[3]):
                    temp.append(str(i[2]))
            word = temp[random.randint(0, len(temp)-1)]
        else:
            conn = sqlite3.connect(sfile)
            c = conn.cursor()
            t = (prevword,)
            c.execute("SELECT * FROM oneword WHERE word=?",t)
            lis = c.fetchall()
            conn.close()
            for i in lis:
                for k in range(0,i[2]):
                    temp.append(str(i[1]))
            word = temp[random.randint(0, len(temp)-1)]                
        if word == '~end~':
            return string.strip().capitalize()
        string = string + ' ' + word
        return twospeak(sfile, prevword, word, string)
    #except:
        #pass    
    
    
def runRead(sfile, txt):
    strlist = prepfilelist('toRead\\' + txt)
    print('Starting read of {}... {} words found!'.format(txt, len(strlist)))
    try:
        read(sfile, strlist)
        print('File {} has been read into word list!'.format(txt))
    except:
        print('ERROR while reading {}...'.format(txt))


def runReadProc(txt, done, dtwo):
    strlist = prepfilelist('toRead\\' + txt)
    print('Reading {}... {} words found!'.format(txt, len(strlist)))
    try:
        readProc(strlist, done, dtwo)
        #print('File {} has been read into word list!'.format(txt))
    except:
        print('ERROR while reading {}...'.format(txt))    
    
    
def paratwoword(sfile, numsentence, maxSentPara = 8):
    novel = '\t' + twospeak(sfile)
    sen = 1
    for i in range(0,numsentence - 1):
        temp = twospeak(sfile)
        test = random.randint(sen, maxSentPara)
        if test == maxSentPara:
            novel = novel + '\n\n\t' + temp
            sen = 1
        else:
            novel = novel + ' ' + temp
            sen = sen + 1
    return novel


def novelizetwoword(sfile, txtfile, numchaps, minchapsennum = 10, maxchapsennum = 50):
    chap = 1
    novel = '\t\t\tChapter 1\n\n\n' + paratwoword(sfile, random.randint(minchapsennum, maxchapsennum))
    print('Chapter {} written!'.format(chap))
    while chap < numchaps:
        chap = chap + 1
        novel = novel + '\n\n\n\t\t\tChapter {}\n\n\n'.format(chap) + paratwoword(sfile, random.randint(minchapsennum, maxchapsennum))
        print('Chapter {} written!'.format(chap))
    with open(txtfile, 'w') as f:
        f.write(novel)
    print('Novel written to {}'.format(txtfile))


def buildDatabase(sfile, readPath = 'toRead'):
    if not os.path.exists(sfile):
        conn = sqlite3.connect(sfile)
        c = conn.cursor()
        c.execute('''CREATE TABLE oneword
                (word text, subword text, count)''')
        c.execute('''CREATE TABLE twoword
                (word1 text, word2 text, subword text, count)''')
        conn.close()
    
    filelist = os.listdir(path=readPath)
    
    readThreads = []
    
    for txt in filelist:
        readThreads.append(threading.Thread(target=runRead, args = (sfile, txt,)))
    
    for thread in readThreads:
        thread.start()
        
    for thread in readThreads:
        thread.join()    
    
    print('All txt files read!')    


def buildDatabaseMulti(sfile, readPath = 'toRead'):
    if not os.path.exists(sfile):
        conn = sqlite3.connect(sfile)
        c = conn.cursor()
        c.execute('''CREATE TABLE oneword
                (word text, subword text, count)''')
        c.execute('''CREATE TABLE twoword
                (word1 text, word2 text, subword text, count)''')
        conn.close()
    filelist = os.listdir(path=readPath)
    
    readProcs = []
    
    with Manager() as manager:
        done = manager.dict()
        dtwo = manager.dict()
        
        for txt in filelist:
            readProcs.append(Process(target=runReadProc(txt, done, dtwo)))
        for proc in readProcs:
            proc.start()
        for proc in readProcs:
            proc.join()
        
        print('\nAll txt Documents in Memory...')
        conn = sqlite3.connect(sfile)
        c = conn.cursor()
        print('\n\nSaving One-Word Combinations to SQL Database {}...'.format(sfile))
        for key in tqdm(done.keys()):
            #print('key: {} - {} new instances!'.format(key, done[key]))
            finished = False
            while finished != True:
                try:
                    t2 = (key[0],key[1])
                    c.execute("SELECT count FROM oneword WHERE word=? AND subword=?",t2)
                    try:
                        count = c.fetchall()[0][0]
                        t1 = (int(count) + done[key],key[0],key[1])
                        
                        c.execute("""UPDATE oneword
                        SET count = ?
                        WHERE word=? AND subword=?;""",t1)
                        
                    except:
                        c.execute("INSERT INTO oneword VALUES (?,?,?)",(key[0],key[1],done[key]))
                    finished = True
                except:
                    print('Unknown Error with {} in done.keys()'.format(key))
                    continue
        conn.commit()
        print('One-Word Combinations Successfully Saved to {}!\n\n'.format(sfile))
        c = conn.cursor()
        print('Saving Two-Word Combinations to SQL Database {}...'.format(sfile))
        for key in tqdm(dtwo.keys()):
            #print('key: {} - {} new instances!'.format(key, dtwo[key]))
            finished = False
            while finished != True:
                try:
                    t2 = (key[0],key[1],key[2])
                    c.execute("SELECT count FROM twoword WHERE word1=? AND word2=? AND subword=?",t2)
                    try:
                        count = c.fetchall()[0][0]
                        t1 = (int(count) + dtwo[key],key[0],key[1],key[2])
                        
                        c.execute("""UPDATE twoword
                        SET count = ?
                        WHERE word1=? AND word2=? AND subword=?;""",t1)
                        
                    except:
                        c.execute("INSERT INTO twoword VALUES (?,?,?,?)",(key[0],key[1],key[2],dtwo[key]))
                    finished = True
                except:
                    print('Unknown Error with {} in dtwo.keys()'.format(key))
                    continue
        conn.commit()
        print('Two-Word Combinations Successfully Saved to {}!\n\n'.format(sfile))
        conn.close()
    print('All txt files read!')  
    
    
if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    
    sfile = 'new_wordlist.snai'
    #buildDatabaseMulti(sfile)