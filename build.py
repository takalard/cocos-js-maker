#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xxtea
import zipfile
import sys
import getopt
import string
import gzip
import shutil
from optparse import OptionParser
import execjs


def write_content_to_file(file_name, content):
    print("file_name = %s",file_name)
    file_ob = open(file_name, 'wb')
    file_ob.write(content)
    file_ob.close()


def read_file_content(file_name):
    file_ob = open(file_name, 'rb')
    content = file_ob.read()
    file_ob.close()
    return content

def getJSCode():
    f = open("jsbeautify.js", 'r') # 打开JS文件
    line = f.readline()
    jsCode = ''
    while line:
        jsCode = jsCode+line
        line = f.readline()
    return jsCode

def zip_file(file_name, file_name_in_zip, zip_file_name):
    z_f = zipfile.ZipFile(zip_file_name, 'wb')
    z_f.write(file_name, file_name_in_zip, zipfile.ZIP_DEFLATED)
    z_f.close()


def unzip_file(file_name, target_dir):
    # try:
    #     z_f = zipfile.ZipFile(file_name, 'a')
    #     z_f.extractall(target_dir)
    #     z_f.close()
    # except zipfile.BadZipfile:
    #     print 'error: unzip failed, please confirm zip opt and key is right.'
    #     return False
    # else:
    #     return True

    _outputpath_ = os.path.join(target_dir,'tmp.js')
    with gzip.open(file_name, 'rb') as f:
        file_content = f.read()
        _strContent_ = str(file_content)

        _jsCode_ = getJSCode()
        _ctx_ = execjs.compile(_jsCode_) #加载JS文件
        _jsPrettyCode_ = _ctx_.call('js_beautify', _strContent_)
        write_content_to_file(_outputpath_,_jsPrettyCode_.encode('utf-8'))

    return True




# the decrypt function contains :
# 1. decrypt .jsc file
# 2. unzip file if required

def decrypt(is_zip, input_key, input_jsc_path):

    print 'begin decrypt.'
    prefix = 'decryptOutput'

    jsc_path = input_jsc_path
    if jsc_path == '':
        jsc_path = raw_input('please input your .jsc path:')

    if os.path.exists(jsc_path) is False:
        print "error: your .jsb file is not exist."
        return False

    enc_file_content = read_file_content(jsc_path)
    print("decrypt enc_file_content length = %d",len(enc_file_content))

    key = input_key
    if key == '':
        key = raw_input('please input your encrypt key:')

    if key == '':
        print "error: your key is empty."
        return False
    print "begin decrypt 1111."
    dec = xxtea.decrypt(enc_file_content, key)
    print "begin decrypt 2222."
    des_file_name = prefix + '/dec.js'
    if os.path.exists(des_file_name) is True:
        os.remove(des_file_name)

    if os.path.exists(prefix) is True:
        # os.system('rm -r ' + prefix)
        shutil.rmtree(prefix, ignore_errors=True)
    os.mkdir(prefix)
    write_content_to_file(des_file_name, dec)

    print "begin decrypt 333 des_file_name = %s"%(des_file_name)

    # decrypt_file_name = prefix + '/decrypt.js'
    _file_name_ = os.path.basename(input_jsc_path)
    _file_name_ = os.path.splitext(_file_name_)[0]
    decrypt_file_name = prefix + '/'+_file_name_+'.js'
    if is_zip is True:
        print 'begin unzip.'
        isUnzipSuc = unzip_file(des_file_name, prefix)
        print "begin decrypt 444 des_file_name = %s, isUnzipSuc = %s"%(des_file_name,isUnzipSuc)
        if isUnzipSuc is True:
            os.remove(des_file_name)
            os.rename(prefix + '/tmp.js', decrypt_file_name)
            #format js code
            return True
        else:
            print '55555 prefix = %s, decrypt_file_name = %s'%(prefix,decrypt_file_name)
            # os.rename(prefix + '/encrypt.js', decrypt_file_name)
    else:
        os.rename(des_file_name, decrypt_file_name)

    print "success. please check 'decryptOutput' directory."
    print '> note: if your decrypt.js is 0b,',
    print 'please confirm your zip option and your decrypt key is right.'
    return True


# the encrypt function contains :
# 1. zip file if required
# 2. encrypt the code and write to file

def encrypt(is_zip, input_key, input_js_path):

    prefix = 'encryptTemp'
    if os.path.exists(prefix) is True:
        # os.system('rm -r ' + prefix)
        shutil.rmtree(prefix, ignore_errors=True)
    os.mkdir(prefix)

    if os.path.exists("encryptOutput") is True:
        # os.system('rm -r ' + "encryptOutput")
        shutil.rmtree("encryptOutput", ignore_errors=True)
    os.mkdir("encryptOutput")

    js_path = input_js_path
    if js_path == '':
        js_path = raw_input('please input your .js path:')

    if os.path.exists(js_path) is False:
        print "error: your .js file is not exist."
        return False

    key = input_key
    if key == '':
        key = raw_input('please input your encrypt key:')

    if key == '':
        print "error: your key is empty."
        return False

    # zip .jsc
    if is_zip is True:
        print 'begin zip.'
        project_zip_name = prefix + '/projectChanged.zip'
        if os.name == 'nt':
            js_path = js_path.replace('/','\\')
            prefix = prefix.replace('/','\\')
            os.system("copy /Y " + js_path + " " + prefix + '\\encrypt.js')
        else:
            os.system("cp " + js_path + " " + prefix + '/encrypt.js')
        zip_file(prefix + '/encrypt.js', 'encrypt.js', project_zip_name)
        project_content = read_file_content(project_zip_name)
    else:
        project_content = read_file_content(js_path)
    # encrypt
    print 'begin encrypt.'
    enc = xxtea.encrypt(project_content, key)
    final_jsc_name = prefix + '/projectChanged.jsc'
    write_content_to_file(final_jsc_name, enc)

    if os.name == 'nt':
        final_jsc_name = final_jsc_name.replace('/','\\')
        # print("final_jsc_name = %s",final_jsc_name)
        os.system('copy /Y ' + final_jsc_name + " encryptOutput\\projectChanged.jsc")
    else:
        os.system('cp ' + final_jsc_name + " encryptOutput/projectChanged.jsc")

    print 'remove temp file.'
    if os.path.exists(prefix) is True:
        # os.system('rm -r ' + prefix)
        shutil.rmtree(prefix, ignore_errors=True)
    print "success. please check 'encryptOutput' directory."
    return True


def main():
    parser = OptionParser()

    path_help = "this is the encrypt/decrypt's source file path"
    nozip_help = "if set this param to 'true', it won't excute zip/unzip"
    key_help = "this is the encrypt/decrypt's key"

    parser.add_option("-p", "--path", dest="path", help=path_help)
    parser.add_option("-n", "--nozip", dest="nozip", help=nozip_help)
    parser.add_option("-k", "--key", dest="key", help=key_help)

    is_decrypt = True
    argv_len = len(sys.argv)
    if argv_len < 2:
        parser.print_help()
        return
    else:
        if sys.argv[1] == 'decrypt':
            is_decrypt = True
        elif sys.argv[1] == 'encrypt':
            is_decrypt = False
        elif (sys.argv[1] == '-h') | (sys.argv[1] == '--help'):
            parser.print_help()
            return
        else:
            print "please choose your function: decrypt or encrypt.",
            print "run the command like './build.py decrypt'"
            return
        sys.argv.pop(1)

    (options, args) = parser.parse_args(sys.argv)

    is_zip = True
    key = ''
    path = ''

    if options.nozip == 'true':
        is_zip = False
    if options.key is not None:
        key = options.key

    if is_decrypt is True:
        if options.path is not None:
            path = options.path
        decrypt(is_zip, key, path)
    else:
        if options.path is not None:
            path = options.path
        encrypt(is_zip, key, path)


if __name__ == "__main__":
    main()
