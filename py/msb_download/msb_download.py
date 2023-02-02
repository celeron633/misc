#!/usr/bin/python3
# only support python3

# crypto support
from  Crypto.Cipher import AES

import os
import sys
from time import sleep

# http downloader
import requests

# regular expression
import re

g_m3u8DownloadHeaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 
    'Accept-Encoding': 'gzip, deflate', 
    'Accept': '*/*', 
    'Connection': 'keep-alive'
}

# whether a live class
g_ifLive = False

# AES-128-CBC
# iv
g_ivStr = ""
# key
g_keyStr = ""

# download file list
g_vidVec = []
g_fNameVec = []

def InputKey() -> bytes:
    rawKeyStr = input("please input the key:")
    strVec = rawKeyStr.split(",")
    hexStr = ""

    for item in strVec:
        hexStr = hexStr + ("%02x" % (int(item.strip())))

    return bytes.fromhex(hexStr)

if os.path.isdir("msb_downloaded") != True:
    os.mkdir("msb_downloaded")
if os.path.isdir("msb_downloaded/decrypted") != True:
    os.mkdir("msb_downloaded/decrypted")

try :
    m3u8FileName = sys.argv[1]
    print("m3u8FileName: %s" % m3u8FileName)

    if len(sys.argv) >= 3 and int(sys.argv[2]) == 1:
        g_ifLive = True
except IndexError:
    print("%s <path_to_m3u8> [is_live_class]" % sys.argv[0])
    exit(-1)

# parse m3u8 file
if g_ifLive == False:
    # normal class
    with open(m3u8FileName, 'r') as m3u8FileStream:
        for line in m3u8FileStream:
            # print(line)
            if re.match(r'^#EXT-X-KEY.*', line):
                g_ivStr = line.split(",")[2].split("=0x")[1].replace('\n', '')
            elif re.match(r'https:.*ts.*', line):
                g_vidVec.append(line.replace('\n', ''))
            else:
                pass
    m3u8FileStream.close()
else:
    # live
    baseVidUrl = input("input base url:")
    with open(m3u8FileName, 'r') as m3u8FileStream:
        for line in m3u8FileStream:
            # get iv
            if re.match(r'^#EXT-X-KEY.*', line):
                g_ivStr = line.split(",")[2].split("=0x")[1].replace('\n', '')
            elif re.match(r'[A-Z0-9]{32}.*ts', line):   # get urls
                g_vidVec.append(baseVidUrl + (line.replace('\n', '')))
            else:
                pass
    m3u8FileStream.close()

print("iv: [%s]" % g_ivStr)
print("ts count: [%d]" % len(g_vidVec))
print("ifLive: [%d]" % g_ifLive)

# enter dir
os.chdir("msb_downloaded")

# download
# session persistent
dlSession = requests.session()
# set header
dlSession.headers = g_m3u8DownloadHeaders
for item in g_vidVec:
    try:
        if (g_ifLive == False):
            fName = item.split('/')[10].split("?")[0]
            g_fNameVec.append(fName)
        else:
            # get filename with index
            matchObj = re.search(r'[0-9A-Z]{32}.*ts', item)
            vidIndex = re.search(r'video=[0-9]*&', item).group().split('=')[1].replace('&', '')

            fName = matchObj.group().split('.')[0] + "_" + vidIndex + "." + matchObj.group().split('.')[1]
            g_fNameVec.append(fName)
        print("downloading %s" % fName)
        print("url: %s" % item)
        # issue GET request
        resp = dlSession.get(item)
        # print(resp)

        # save to file
        with open(fName, 'wb') as vidStream:
            vidStream.write(resp.content)
        vidStream.close()

        sleep(0.1)
        # break
    except ...:
        print("download %s failed" % item)

# decrypt downloaded file
# input AES key
g_ivBytes = InputKey()
for item in g_fNameVec:
    print("decrypting %s" % item)
    if g_ifLive == False:
        shortFileName = item.split('_')[2]
    else:
        shortFileName = item.split('_')[1].replace('.ts', '') + ".ts"

    ivBytes = bytes.fromhex(g_ivStr)
    keyBytes = g_ivBytes
    # print("iv: %s" % ivBytes.hex())
    # print("key: %s" % keyBytes.hex())

    # read encrypted file
    with open(item, 'rb') as encryptedFileStream:
        encFileBytes = encryptedFileStream.read()
    encryptedFileStream.close()

    # run decrypt
    aesContext = AES.new(key = keyBytes, iv = ivBytes, mode = AES.MODE_CBC)
    decFileBytes = aesContext.decrypt(encFileBytes)

    print("writing %s" % shortFileName)
    # write decrypted file
    with open("decrypted/" + shortFileName, 'wb') as decryptedFileStream:
        decryptedFileStream.write(decFileBytes)
    decryptedFileStream.close()