#!/usr/bin/env python
# -*- coding: utf8 -*-

import commands
import datetime
import json
import os
import re
import sys
import time
import urllib
import urllib2
from contextlib import nested

BLACK_LIST = ("http", "https")


def get_clipboard_data():
    if (sys.platform == 'darwin'):
        return_code, output = commands.getstatusoutput('pbpaste')
    elif (sys.platform == 'linux2'):
        return_code, output = commands.getstatusoutput('xclip -d :0 -o')
    else:
        reutrn_code, output = 1, None

    if return_code != 0:
        return None
    else:
        return output


def is_empty_str(str):
    return str == None or str.strip() == ''


def filter(word):
    if is_empty_str(word):
        return None
    pat = re.compile(r'[a-zA-Z]+')
    ml = pat.match(word)
    if ml == None:
        return None
    m = ml.group()
    if is_empty_str(m) or m in BLACK_LIST:
        return None
    return m


def get_word():
    word = get_clipboard_data()
    return filter(word)


def notify(word, mean, pos):
    cmd = None
    if (sys.platform == 'darwin'):
        cmd = 'osascript -e \'display notification "%s  %s" with title "%s"\'' % (
            pos, mean, word)
    elif (sys.platform == 'linux2'):
        cmd = 'notify-send --urgency=critical "%s"  "%s %s"' % (
            word, pos, mean)

    if cmd != None:
        print("cmd: " + cmd)
        commands.getstatusoutput(cmd)


def say(word):
    if (sys.platform == 'darwin'):
        print('say: ' + word)
        commands.getstatusoutput('say ' + word)


def record(word, mean, pos):
    # prepare dirs
    root = os.environ['HOME']
    recdir_root = '%s/learn_word' % (root,)
    recdir_date = '%s/bydate' % (recdir_root,)

    try:
        if not os.path.isdir(recdir_date):
            os.makedirs(recdir_date)

        recf_all = '%s/all.txt' % (recdir_root,)
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        recf_date = '%s/%s.txt' % (recdir_date, today)
        with nested(open(recf_all, 'a'), open(recf_date, 'a')) as (f_all, f_date):
            rec = '%s | %s | %s\n' % (word, pos, mean)
            print('rec: ' + rec)
            f_all.write(rec)
            f_date.write(rec)
    except IOError, msg:
        print msg


def get_mean(word):
    url = 'https://www.shanbay.com/api/v1/bdc/search/'
    parms = {'version': 2, 'word': word}
    parms = urllib.urlencode(parms)
    # print("parms: " + parms)
    try:
        req = urllib2.Request(url='%s%s%s' % (url, '?', parms))
        res = urllib2.urlopen(req).read()
        j = json.loads(res)
        print(j)
        if j['status_code'] != 0:
            return
        mean = j['data']['definitions']['cn'][0]['defn']
        pos = j['data']['definitions']['cn'][0]['pos']
        print("mean: " + mean)
        print("pos: " + pos)
        notify(word, mean, pos)
        say(word)
        record(word, mean, pos)
    except IOError, msg:
        print msg
        return


def loop():
    lastl = None
    while True:
        time.sleep(1)

        l = get_word()
        if l is None or lastl == l:
            continue

        print("\n-----------")
        # search in dict
        lastl = l
        get_mean(l)


def main(argv):
    reload(sys)
    sys.setdefaultencoding("utf-8")
    loop()


if __name__ == '__main__':
    main(sys.argv[1:])
