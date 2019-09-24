# cocos-js-decrypt
cocos js decrypt

从其他网友的解密代码改写而来，主要用于解密jsc文件以及压缩勾选了压缩选项的jsc文件的解压\n
cocos对javascript文件进行了xxtea加密，如果开发者勾选了zip模式，那么，会将再会将加密之后的jsc进行gzip压缩，记住是gzip压缩，并不是zip压缩，最后得到的assets/src下的jsc文件\n
所以逆向过程就是先对jsc文件进行xxtea解密，然后再用gzip进行解压\n
此脚本同时包含了对生成的js代码的格式化\n
使用方法：python build.py decrypt -k "xxxxxxxx-xxxx-xx" -n false -p input/project.jsc\n
-k --key 加密时候的秘钥
-n --nozip 是否有压缩(gzip压缩)
-p --path jsc文件路径(相对于脚本的路径即可)

build.py --加/解密(压缩)脚本的逻辑
xxtea.py --xxtea加解密
jsbeautify.js --js脚本格式化
