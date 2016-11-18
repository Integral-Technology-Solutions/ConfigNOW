import os
import sys

import validation_helper as helper

from java.io import FileInputStream,FileOutputStream
from java.lang import System,String
from java.util import Properties
from java.math import BigInteger
from java.security import *
from javax.crypto import KeyGenerator,SecretKey,Cipher
from javax.crypto.spec import SecretKeySpec


from org.apache.log4j import Logger
from org.apache.commons.codec.binary import Base64

log = Logger.getLogger('password_encrypter')
kgen = KeyGenerator.getInstance("AES")
kgen.init(128)
skey = kgen.generateKey()
raw = skey.getEncoded()
rawkey=Base64.encodeBase64(raw).tostring()
skeySpec = SecretKeySpec(raw, "AES")
cipher = Cipher.getInstance("AES")

def encryptPassword(password):
    if password is not None and password is not ' ': 
        cipher.init(Cipher.ENCRYPT_MODE, skeySpec)
        encrypted =cipher.doFinal(password)
        encodeTxt = Base64.encodeBase64(encrypted)
        return encodeTxt.tostring()

def encryptAllPasswords(configfile):
    log.info("Encrypting Passwords in config file")
    if(configfile is not None and not ''):
    	if not configfile.endswith('.properties'):
    		configfile=configfile+'.properties'    
    	fileobj=open(configfile,'r')
    	proplist=fileobj.readlines()
    	       	    
    for prop in proplist:
    	propkey=prop[0:prop.find('=')].strip()
    	propvalue=prop[prop.find('=')+1:].strip()
    	if 'base'==propkey:
    		log.debug(propvalue)
    		encryptBaseFile(propvalue)
    	encryptPasswordProperty(proplist,propkey,propvalue,configfile)
    	
def encryptPasswordProperty(proplist,propkey,propvalue,configfile):
	if propkey.lower().endswith('.password') and propvalue.startswith("${"):
    		checkRefs(proplist,propkey,propvalue[propvalue.find("${")+2:propvalue.find("}")] )
    	if propkey.lower().endswith('.password') and not propvalue.startswith("{AES}") and not propvalue.startswith("${") and not propvalue.startswith("?"):
    	    encrypted=encryptPassword(propvalue)
    	    log.debug("writing back property :propkey:"+propkey+"value:"+encrypted)
    	    writeEncryptedPWDtoFile(propkey,encrypted,configfile,rawkey)
    	     
def encryptBaseFile(basefile):
	log.info("encrypting passwords in base file first: "+basefile)
	basefileobj=open(basefile,'r')
	proplist=basefileobj.readlines()
	for prop in proplist:
		propkey=prop[0:prop.find('=')].strip()
		propvalue=prop[prop.find('=')+1:].strip()
		if propkey.lower().endswith('base'):
			log.debug(propvalue)
			encryptBaseFile(propvalue)
		encryptPasswordProperty(proplist,propkey,propvalue,basefile) 
		


def checkRefs(proplist,propkey,propvalue):
	for prop in proplist:
		if prop.startswith(propvalue+"="):
		    refkey=prop[:prop.find("=")].lower()
		    if not refkey.endswith(".password"):
		        log.info("There is a password property [ "+propkey+" ]which is left unencrypted as it references a non-password property.")
		        
                           
def findconfigpath(config):
    propfilepath=config.getProperty("ConfigNOW.config_file_location")
    log.info("config file location :"+propfilepath)
    
    return propfilepath
    
def writeEncryptedPWDtoFile(propkey,encryptedpwd,configfile,rawkey):
    filehandletoread = open(configfile,"r")
    filecontent=filehandletoread.read()
    filecontentnew=''
    lines=filecontent.split('\n')
    for line in lines:
    	if propkey.lower().endswith('.password') and line.startswith(propkey+'='):
            propvalue=line.split('=')[1]
            filecontentnew=filecontent.replace(line,propkey+'='+'{AES}'+encryptedpwd+rawkey)
    filehandletoread.close()
    filehandletowrite = open(configfile,"w")
    filehandletowrite.write(filecontentnew+"\n")
    filehandletowrite.close()
    
def decryptPassword(encryptedpassword,key):
    secretKey=Base64.decodeBase64(key)
    seckeySpec = SecretKeySpec(secretKey, "AES")
    if encryptedpassword is not None and encryptedpassword is not ' ':
    	encData = Base64.decodeBase64(encryptedpassword)
    	cipher.init(Cipher.DECRYPT_MODE, seckeySpec)
        decrypted = cipher.doFinal(encData)
        originalString = decrypted.tostring()
        return originalString
        
def decryptBaseFile(basefile,domainProperties):
	log.info("decrypting passwords in base file first: "+basefile)
	basefileobj=open(basefile,'r')
	proplist=basefileobj.readlines()
	for prop in proplist:
		propkey=prop[0:prop.find('=')].strip()
		propvalue=prop[prop.find('=')+1:].strip()
		if propkey.lower() == 'base':
			decryptBaseFile(propvalue,domainProperties)
        decryptAllPasswords(basefile,domainProperties)
    		

# Now decrypts passwords in supplied properties file without going back through
# property files
def decryptAllPasswords(configfilepath,domainProperties):
    log.debug("Decrypting any Encrypted passwords in file : "+configfilepath)
    	
    #fileobj=open(configfilepath,'r')
    #proplist = fileobj.readlines()
    enum = domainProperties.keys()
    while enum.hasMoreElements():
	    propkey = enum.nextElement()
	    if String(propkey.lower()).endsWith('.password'):
			propvaluewithkey=domainProperties.getProperty(propkey)
			if(propvaluewithkey.startswith("{AES}")):
				log.debug('decrypting password for '+propkey)
				propvaluewithkey=String(propvaluewithkey).trim()
				propvalue=propvaluewithkey[5:len(propvaluewithkey)-24]
				key=propvaluewithkey[len(propvaluewithkey)-24:]
				decrypted=decryptPassword(propvalue,key)
				domainProperties.setProperty(propkey,decrypted)
			elif(propvaluewithkey.startswith("${")):
				propvaluewithkeytrimmed=propvaluewithkey[2:propvaluewithkey.find("}")]
				copyRefValues(propvaluewithkeytrimmed,proplist,domainProperties,propkey)
			else:
				log.debug('leaving unencrypted value for ' + propkey)
		

def copyRefValues(propvaluewithkey,proplist,domainProperties,propkey):
	for prop in proplist:
		if(prop.startswith(propvaluewithkey)):
		    domainProperties.setProperty(propkey,domainProperties.getProperty(propvaluewithkey))
		    
    	                  
def run(config):
	"""Encrypts all the password properties"""
        encryptAllPasswords(findconfigpath(config))
        
