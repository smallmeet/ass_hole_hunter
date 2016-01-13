#coding=utf-8
'''
Demo modules for ass_hole_hunter
'''

#import sys
#sys.path.append('dbs/')
from libs.functions import *
#import modules.*
import hashlib
import json
#import sqlite3
#import requests
#from libs.Threads import ThreadPool
#from libs.functions import *
#from config import global_config

class hunter_plugin:
    '''cms feature detect'''
    infos = {
        'plugin_name':'what_web module',
        'author':'demon',
        'update':'2015/04/22',
        'site':'http://www.dawner.info',
        }
    opts  = {
        'url':'192.168.1.254 or default',
        'protocol':'http or https or other',
        'threads':'10'
        }
    
    
    def __init__(self,url,protocol,specified_plugin_id = ""):
        self.url = url
        self.protocol = protocol
        self.result = []
        self.specified_plugin_id = specified_plugin_id




    def exploit(self):
        #global rcx,rcu
        global result_db_path
        result_db_path = global_config.infos['result_path']+"/result.db"

        #设定全局exp_path
        cx = sqlite3.connect("dbs/ass.db")
        cu = cx.cursor()
        cu.execute("select * from vulns")
        contents = cu.fetchall()
        vuln_counts = len(contents)
        global exploit_path
        exploit_path = ""

        if self.specified_plugin_id != "" and self.specified_plugin.isdigit() and self.specified_plugin_id <= vuln_counts:
            #取数据库第几条结果
            exploit_path= contents[vuln_counts][4]
        else:
            log_record("No such plugin...","e")
            exit(0)

     
        if self.protocol == 'http' or self.protocol == 'https':
            url = self.protocol+'://'+self.url+'/'
        else:
            return None
        print 'Exp_start...'
        #print self.url+'\n'
        print '[+]Current exp_url:'+url
        self.cmsjsons = self.retcmsjsons('dbs/cms.txt')
        #threadsNum = int(self.opts['threads'])
        #ThreadsNum = 10
        '''threads can be set in opts  '''
        #sites = self.options['sites']
        #sitesLst = retSites(sites)
        
        #ArgsLst = self.retArgs(sitesLst, self.cmsjsons)

        ArgsLst = self.retArgs(url, self.cmsjsons)
        
        #threadsDo(self.whatCMS, threadsNum, ArgsLst)
        tp = ThreadPool(global_config.infos['thread_num'])
        for Args in ArgsLst:
            #print Args
            tp.add_job(self.whatCMS, Args)
        tp.start()
        try:
            tp.wait_for_complete()
        except KeyboardInterrupt:
            tp.stop()
        print '[+]Get result:'+str(self.result)
        print 'Exp_stop...'

        #if len(self.result):
        #    logByLine(self.result,'output/%s-whatcms.txt' % currentTime("-"))


    def retArgs(self, url, cmsjsons):
        ArgsLst = []
        #for site in siteslst:
        for cmsname in cmsjsons:
            for record in cmsjsons[cmsname]:
                path = record["path"]
                ArgsLst.append((url, path,))
        return list(set(ArgsLst))


    def retcmsjsons(self, jsonfilepath="db/cms.txt"):
        with open(jsonfilepath) as f:
            cmsjsons = json.loads(f.read())
        f.close()
        return cmsjsons

    def getcmsnamefromresp(self, path, resp, cmsjsons):
        for cmsname in cmsjsons:
            for record in cmsjsons[cmsname]:

                if record["path"] == path:

                    #if record.has_key("version"):
                    #    version = record["version"]
                    #else:
                    #    version = " Version missing..."

                    if record.has_key("status_code"):
                        if resp.status_code == record["status_code"]:
                            #return (cmsname,version)
                            return cmsname

                    elif record.has_key("regex"):
                        if re.search(record["regex"], resp.content):
                            print "regex"
                            #return (cmsname,version)
                            return cmsname

                    elif record.has_key("md5"):
                        responsehash = hashlib.md5(resp.content).hexdigest()
                        if str(responsehash) == record["md5"]:
                            #return (cmsname,version)
                            return cmsname
                    else:
                        return None
                    break


    def cms_attack(self, site, cms):
        print 'Cms_attack starting....'
        #存在cms="specified"
        if cms == "specified":
            exp_plugin=__import__(exploit_path, fromlist=[exploit_path])
            hunter_exploit = getattr(exp_plugin,'hunter_exploit')
            results = hunter_exploit(site).exploit()
        else:
            results = ""
            pass

        url = site.split('//')[1].split('/')[0]
        cms_cx = sqlite3.connect(result_db_path)
        cms_cu = cms_cx.cursor()
        cms_cu.execute("update result set cms_type='"+cms +"'where url ='"+self.url+"'")
        cms_cx.commit()
        #rcx.commit()
        
        cx = sqlite3.connect("dbs/ass.db")
        cu = cx.cursor()
        cu.execute("select vuln_path from vulns where vuln_path like '%"+cms+"%'")
        tp = ThreadPool(global_config.infos['thread_num'])
        #print str(cu.fetchall())
       #线程???
        for paths in cu.fetchall():
            for path in paths:
                print str(path)
                #print str(cu.fetchall())
                print "[+]vuln_path:"+str(path)
                exp_plugin=__import__(path, fromlist=[path])
                hunter_exploit = getattr(exp_plugin,'hunter_exploit')
                #hunter_exploit.exploit(site)
                hunter_exploit = hunter_exploit(site)
                #print '-------'
                tp.add_job(hunter_exploit.exploit)
        tp.start()
        tp.wait_for_complete()
        results = tp.get_result()
        try:
            #尝试一下是否写在start后面
            #tp.wait_for_complete()
            #results = tp.get_result()


            #print "==="+str(results)
            #vuln_text = base64.encodestring(results)
            confirm_cx = sqlite3.connect(result_db_path)
            confirm_cu = confirm_cx.cursor()
            if len(results) != 0:
                #print '====='+str(url)
                #confirm_cx = sqlite3.connect(result_db_path)
                #confirm_cu = confirm_cx.cursor()
                #vuln_text = str(results)[2:-2]
                vuln_text = base64.encodestring(str(results))
                print vuln_text
                confirm_cu.execute("update result set vuln_confirm= 'y', vuln_text ='"+vuln_text+"' where url ='"+self.url+"'")
                #confirm_cu.execute("update result set vuln_confirm= 'y' where url ='"+self.url+"'")
            else:
                confirm_cu.execute("update result set vuln_confirm= 'n' where url ='"+self.url+"'")
            confirm_cx.commit()
        except Exception,e:
            #print '[x]Cms_attack error:'+str(e)
            log_record("Cms_attack error","e")
            tp.stop()
        print '[!]Vuln_confirm result has been updated!'

    def whatCMS(self, site, path):
        #没有自定义exp的话就取空值，然后将cms_type直接置为值：specified
        if exploit_path:
            self.cms_attack(site,"specified")
        else:
            pass

        try:
            checkurl = site + path
            #color.echo("[*] checking %s \r" % path[0:40].ljust(40," "),None, append=True)
            #print checkurl+'-------'
            resp = url_Get(requests, checkurl)
            result = self.getcmsnamefromresp(path, resp, self.cmsjsons)
            if result:
                if not (site, result) in self.result:
                    print site, result.split('@')[0]
                    #color.echo("[+]%s : %s ver: %s \t" % (site, result[0].split('@')[0]), result[1], GREEN)
                    print str(result.split('@')[0])
                    self.result.append((site, result))
                    self.cms_attack(site, str(result.split('@')[0]))
                    #self.result.append((site, result[0]))
                    #self.log.append((site, path, result[0], result[1]))
        except Exception,e:
            print '[x]WhatCMS error:'+str(e)
            pass
