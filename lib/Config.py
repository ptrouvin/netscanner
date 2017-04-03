"""
    Config.py: just a quick and simple JSON config file
    
    Author: Pascal TROUVIN
"""

import json
import sys
import logging
import os.path
import os
import time

log = logging.getLogger('Config')
# to change log level: Config.log.setLevel(logging.DEBUG)  or whatever

class Config(dict):
    def __init__(self, filename=None):
    
        dict.__init__(self)
        
        self.config={}

        self.configFN=sys.argv[0]+'.config.json'
        self.modified=False

        if filename:
            self.configFN=filename

        self.load()
        
    def load(self):
        log.info("Loading config from '%s'" % self.configFN)
        if os.path.isfile(self.configFN):
            with open(self.configFN) as data_file:
                self.config=json.load(data_file)
            sti=os.stat(self.configFN)
            self.mtime=sti[9]

            log.debug("config loaded")
        else:
            log.debug("config file '%s' does not exist" % self.configFN)
    
    def filename(self,fn=None):
        if fn:
            self.configFN=fn
            log.info("Set config filename to '%s'" % self.configFN)
            self.modified=True
        return self.configFN
        
    def isModified(self):
        return self.modified
    
    def get(self,name,default=None):
        if default!=None:
            return self.config.get(name,default)
        return self.config.get(name)
        
    def __getitem__(self,name):
        if name in ['config','configFN','modified','mtime']:
            return dict.__getattr__(self,name)
        return dict.__getitem__(self.config,name)
        
    def __setitem__(self,name,val):
        if name in ['config','configFN','modified','mtime']:
            dict.__setattr__(self,name,val)
        else:
            dict.__setattr__(self,'modified',True)
            dict.__setitem__(self.config,name,val)
        
    def __delitem__(self,name):
        dict.__setattr__(self,'modified',True)
        dict.__delitem__(self.config,name)

    def save(self):
        if self.modified:
            log.info("saving config to '%s'" % self.configFN)
            with open(self.configFN,'w') as file:
                file.write(json.dumps(self.config,indent=1))
            self.mtime=os.stat(self.configFN)
            self.modified=False
    
    def __str__(self):
        modified=''
        if self.modified:
            modified='*'
        return "Config("+self.configFN+") "+modified+' '+json.dumps(self.config,indent=1)
        
    def empty(self):
        dict.__setattr__(self,'modified',True)
        self.config={}
    
    def needReload(self):
        mt=os.stat(self.configFN)[9]
        return mt>self.mtime
        
    def reload(self):
        if self.needReload():
            self.load()
    
if __name__ == '__main__':
    import argparse

    LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}
                  
    parser = argparse.ArgumentParser(description='Config test')
    parser.add_argument('--logging-level', default='info',
            help='Logging level '+','.join(LOGGING_LEVELS.keys()))
    parser.add_argument('-f','--file', default=None,
            help="Determine the config file to work on")

    args = parser.parse_args()
    logging_level = LOGGING_LEVELS.get(args.logging_level, logging.NOTSET)
    logging.basicConfig(level=logging_level,
                      format='%(asctime)s %(levelname)s: %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')

    log.info("Starting test sequence")
    config=Config(filename=args.file)
    config['abc']=123
    
    print str(config)
    config['tbd']='to be deleted'
    print str(config)
    del config['tbd']
    print str(config)
    
    config.save()
    print str(config)
    
    config.load()
    print str(config)
    
    config['bc']={}
    print str(config)
    config['bc']['test']={'test':1}
    print str(config)
    config['bc']['test']['list']=[]
    print str(config)
    config['bc']['test']['list'].append([1,2,3])
    print str(config)
    
    config.save()
    print str(config)
    
    config.load()
    print str(config)
    
    config.empty()
    print str(config)
    config.save()
    print str(config)
    
    config.load()
    print str(config)
    
    if config.needReload():
        raise Exception("BUG needReload")
    # touch
    time.sleep(2)
    f=open(config.filename(),"a")
    f.write(' ')
    f.close()
    if not config.needReload():
        print os.stat(config.configFN)[9], ' stored:', config.mtime
        raise Exception("BUG needReload")
    config.reload()
    print str(config)
