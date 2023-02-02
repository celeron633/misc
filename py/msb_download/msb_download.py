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

g_m3u8_download_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 
    'Accept-Encoding': 'gzip, deflate', 
    'Accept': '*/*', 
    'Connection': 'keep-alive'
}

g_m3u8_file_name = ""

# whether a live class
g_if_live = False

# AES-128-CBC
# iv
g_iv_str = ""
# key
g_key_str = ""

# download file list
g_vid_list = []
g_file_name_list = []

def input_key() -> bytes:
    raw_key_str = input("please input the key:")
    str_list = raw_key_str.split(",")
    hex_str = ""

    for item in str_list:
        hex_str = hex_str + ("%02x" % (int(item.strip())))

    return bytes.fromhex(hex_str)

def init_dir() -> None:
    if os.path.isdir("msb_downloaded") != True:
        os.mkdir("msb_downloaded")
    if os.path.isdir("msb_downloaded/decrypted") != True:
        os.mkdir("msb_downloaded/decrypted")

def decrypted_downloaded_files() -> None:
    # input AES key
    key_bytes = input_key()
    for item in g_file_name_list:
        print("decrypting %s" % item)
        if g_if_live == False:
            short_file_name = item.split('_')[2]
        else:
            short_file_name = item.split('_')[1].replace('.ts', '') + ".ts"

        iv_bytes = bytes.fromhex(g_iv_str)
        key_bytes = key_bytes

        # read encrypted file
        with open(item, 'rb') as encrypted_file_stream:
            encrypted_file_bytes = encrypted_file_stream.read()
        encrypted_file_stream.close()

        # run decrypt
        aes_context = AES.new(key = key_bytes, iv = iv_bytes, mode = AES.MODE_CBC)
        decrypted_file_bytes = aes_context.decrypt(encrypted_file_bytes)

        print("writing %s" % short_file_name)
        # write decrypted file
        with open("decrypted/" + short_file_name, 'wb') as decrypted_file_stream:
            decrypted_file_stream.write(decrypted_file_bytes)
        decrypted_file_stream.close()

def download_video_files() -> None:
    # session persistent
    download_session = requests.session()
    # set header
    download_session.headers = g_m3u8_download_headers
    for item in g_vid_list:
        try:
            if (g_if_live == False):
                file_name = item.split('/')[10].split("?")[0]
                g_file_name_list.append(file_name)
            else:
                # get filename with index
                match_obj = re.search(r'[0-9A-Z]{32}.*ts', item)
                video_index = re.search(r'video=[0-9]*&', item).group().split('=')[1].replace('&', '')

                file_name = match_obj.group().split('.')[0] + "_" + video_index + "." + match_obj.group().split('.')[1]
                g_file_name_list.append(file_name)
            print("downloading %s" % file_name)
            print("url: %s" % item)
            # issue GET request
            resp = download_session.get(item)

            # save to file
            with open(file_name, 'wb') as video_stream:
                video_stream.write(resp.content)
            video_stream.close()

            sleep(0.1)
            # break
        except ...:
            print("download %s failed" % item)
            pass

def parse_m3u8_file() -> None:
    # parse m3u8 file
    if g_if_live == False:
        # normal class
        with open(g_m3u8_file_name, 'r') as m3u8_file_stream:
            for line in m3u8_file_stream:
                # print(line)
                if re.match(r'^#EXT-X-KEY.*', line):
                    g_iv_str = line.split(",")[2].split("=0x")[1].replace('\n', '')
                elif re.match(r'https:.*ts.*', line):
                    g_vid_list.append(line.replace('\n', ''))
                else:
                    pass
        m3u8_file_stream.close()
    else:
        # live
        base_vid_url = input("input base url:")
        with open(g_m3u8_file_name, 'r') as m3u8_file_stream:
            for line in m3u8_file_stream:
                # get iv
                if re.match(r'^#EXT-X-KEY.*', line):
                    g_iv_str = line.split(",")[2].split("=0x")[1].replace('\n', '')
                elif re.match(r'[A-Z0-9]{32}.*ts', line):   # get urls
                    g_vid_list.append(base_vid_url + (line.replace('\n', '')))
                else:
                    pass
        m3u8_file_stream.close()

def init_args() -> None:
    global g_if_live
    global g_m3u8_file_name

    try :
        g_m3u8_file_name = sys.argv[1]
        print("m3u8_file_name: %s" % g_m3u8_file_name)

        if len(sys.argv) >= 3 and int(sys.argv[2]) == 1:
            g_if_live = True
    except IndexError:
        print("%s <path_to_m3u8> [is_live_class]" % sys.argv[0])
        exit(-1)

if __name__ == "__main__":
    # argc/argv
    init_args()

    # create necessary dirs
    init_dir()

    # parse m3u8 file
    parse_m3u8_file()

    # print basic download info
    print("iv: [%s]" % g_iv_str)
    print("ts count: [%d]" % len(g_vid_list))
    print("if_live: [%d]" % g_if_live)

    # enter dir
    os.chdir("msb_downloaded")

    # download
    download_video_files()

    # decrypt downloaded file
    decrypted_downloaded_files()