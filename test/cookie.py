#coding:utf-8
import urllib,urllib2,cookielib

cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.2.0'),('referer','http://bgp.he.net')]
login_path = 'http://bgp.he.net/dns/www.bstaint.net/#_dns'

request = urllib2.Request(login_path)
html = opener.open(request).read()
print html

if cj:
    print cj
for index, cookie in enumerate(cj):
    print cookie
