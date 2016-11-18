# ============================================================================
#
# Copyright (c) 2007-2010 Integral Technology Solutions Pty Ltd, 
# All Rights Reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF THIRD PARTY RIGHTS.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE BE 
# LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES, OR 
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER 
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT 
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# FOR FURTHER INFORMATION PLEASE SEE THE INTEGRAL TECHNOLOGY SOLUTIONS 
# END USER LICENSE AGREEMENT (ELUA).
#
# ============================================================================

##
## common.py
##
## This script contains functions that may be common to multiple scripts. This 
## includes configuration, connection and error functions.

from java.io import BufferedReader
from java.io import FileInputStream
from java.io import InputStreamReader
from java.security import MessageDigest
from javax.naming import AuthenticationException
from java.lang import Runtime
from java.lang import SecurityException
from org.apache.log4j import Logger, PropertyConfigurator

import sys
import os
import re
import getopt
import java.sql as jsql
import string

OS_TYPE_WINDOWS = "WindowsNT"

PROPERTY_DISABLE_PROMPTING = "confignow.noninteractive"


#=======================================================================================
# Global variables
#=======================================================================================

commonModule = '1.0.1'

try:
	scriptConfigProperties
except NameError:
	scriptConfigProperties = None

try:
	replaceFlag
except NameError:
	replaceFlag = None

try:
	log
except NameError:
	log = Logger.getLogger('ConfigNOW')

log.debug('Loading module [common.py] version [' + commonModule + ']')

	
#=======================================================================================
# Error class for script errors
#=======================================================================================

class ScriptError(Exception):
  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return repr(self.msg)


#=======================================================================================
# getUserInput
# 
# Prompt user for input
#=======================================================================================

def getUserInput(prompt, default):
	"""Reads input from the user"""
	
	if default is not None:
		prompt += ' [' + default + ']'
	
	prompt += ' : '
	
	value = raw_input(prompt)
	
	if len(value) == 0:
		return default
	else:
		return value
	
	# done with reading input


#=======================================================================================
# getPropertyFileLocation
# 
# Returns the location of the properties file being used by the script.
# @TODO - this function should be deprecated, because it assumes only ONE parameter
# being passed to the higher-level script calling this function, or at least that a
# properties file is ALWAYS the first parameter. Named parameters are safer and more
# flexible.
#=======================================================================================

def getPropertyFileLocation():
	return str(sys.argv[1])


#==============================================================================
# isUpdate
#
# Indicates if the configure domain process is being performed as
# part of an update to a freshly created domain (changed with the create 
# domain process) or as an update to a previously created domain
#==============================================================================
def isUpdateToPreviouslyCreatedDomain():
	
	isUpdate = 'false'
	
	try:
		opts, args = getopt.getopt(sys.argv[2:], "", ["domainProperties=","resourcesProperties=","update=", "managedServer="])
	except getopt.GetoptError, err:
		log.error(str(err))
		sys.exit(2)	
	for o, a in opts:
		if o == "--update":
			isUpdate = a

	return isUpdate


#==============================================================================
# getManagedServer()
#
#==============================================================================
def getManagedServer():
	
	managedServer = None
	
	try:
		opts, args = getopt.getopt(sys.argv[2:], "", ["domainProperties=", "resourcesProperties=", "update=", "managedServer="])
	except getopt.GetoptError, err:
		log.error(str(err))
		sys.exit(2)	
	for o, a in opts:
		if o == "--managedServer":
			managedServer = a

	return managedServer


#==============================================================================
# getDomainFileName
#
#==============================================================================
def getDomainFileName():
	
	domainPropFile = None
	
	try:
		opts, args = getopt.getopt(sys.argv[2:], "", ["domainProperties=","resourcesProperties=","update=", "managedServer="])
	except getopt.GetoptError, err:
		log.error(str(err))
		sys.exit(2)	
	for o, a in opts:
		if o == "--domainProperties":
			domainPropFile = a

	if domainPropFile is None:
		domainPropFile = 'domain.properties'
		
	log.debug('#################################################')
	log.debug('#################################################')
	log.debug('#################################################')
	log.debug('Using ' + str(domainPropFile))
	log.debug('#################################################')
	log.debug('#################################################')
	log.debug('#################################################')
	
	return domainPropFile

#==============================================================================
# getResourcesFileName
#
#==============================================================================
def getResourcesFileName():

	resourcesPropFile = None
	
	try:
		opts, args = getopt.getopt(sys.argv[2:], "", ["domainProperties=","resourcesProperties=","update=", "managedServer="])
	except getopt.GetoptError, err:
		log.error(str(err))
		sys.exit(2)
	for o, a in opts:
		if o == "--resourcesProperties":
			resourcesPropFile = a
	
	if resourcesPropFile is None:
		resourcesPropFile = 'resources.properties'
	
	log.debug('#################################################')
	log.debug('#################################################')
	log.debug('#################################################')
	log.debug('Using ' + str(resourcesPropFile))
	log.debug('#################################################')
	log.debug('#################################################')
	log.debug('#################################################')
	
	return resourcesPropFile

#=======================================================================================
# isReplaceRequired
# 
# Provides the user with an information message informing them that property values will
# will not be overridden when REPLACE is absent as an environment variable.
#=======================================================================================
def isReplaceRequired(replaceFlagParam):

	global replaceFlag
	
	if not replaceFlagParam:
		try:
			replaceFlag = os.environ['REPLACE']
		except KeyError, error:
			if replaceFlag is None:
				log.debug('#####################################################')
				log.debug('#The REPLACE environment variable does not exist.')
				log.debug('#If you want to override property values, ')
				log.debug('#please append [set REPLACE=true] into setenv.cmd or ')
				log.debug('#[export REPLACE=true] into setenv.sh and run the scripts again.')
				log.debug('#####################################################')
				replaceFlag = 'N'
	else:
		replaceFlag = replaceFlagParam

	if not replaceFlag is None and len(replaceFlag)>0:
		if replaceFlag.upper()=='TRUE' or replaceFlag.upper()=='YES' or replaceFlag.upper()=='Y':
			return 1
		else:
			return 0
	else:
		return 0

def __connectManagedServer(wlsHost, wlsPort, wlsUser, wlsPassword):
	#=======================================================================================
	# Load domain properties
	#=======================================================================================
	
	wlsURL='t3://' + str(wlsHost) + ':' + str(wlsPort)
	
	sleeptime = 15
	maxAttempt = 10
	attemptIdx = 1
	while 1:
		log.debug('Establishing connection to Server at URL [' + str(wlsURL) + '], attempt #' + str(attemptIdx))
		try:
			connect(wlsUser, wlsPassword, wlsURL)
			break
		except Exception, error:
			if attemptIdx<maxAttempt:
				log.debug('Establishing connection to Server failed at attempt #' + str(attemptIdx) + ': No Server running on URL [' + str(wlsURL) + '] or the server is not ready to execute WLST command. Delay ' + str(sleeptime) + ' seconds and try again.')
				Thread.currentThread().sleep(sleeptime*1000)
				attemptIdx+=1
			else:
				raise ScriptError, 'Unable to connect to Server at URL [' + str(wlsURL) + ']: ' + str(error)

#=======================================================================================
# __connectAdminServer
# 
# Connects to the admin server, as determined from the config and makes
# a series of attempts to connect to the admin server.
#=======================================================================================

def __connectAdminServer(configProperties):
    wlsAdminPort=configProperties.getProperty('wls.domain.adminPort')
    wlsAdminUser=configProperties.getProperty('wls.admin.username')
    wlsAdminPassword=configProperties.getProperty('wls.admin.password')
    if wlsAdminPort is None or len(wlsAdminPort)==0:
        wlsAdminURL='t3://' + str(configProperties.getProperty('wls.admin.listener.address')) + ':' + str(configProperties.getProperty('wls.admin.listener.port'))
    else:
        wlsAdminURL='t3s://' + str(configProperties.getProperty('wls.admin.listener.address')) + ':' + str(wlsAdminPort)
    
    sleeptime = 15
    maxAttempt = 10
    attemptIdx = 1
         
    while 1:
        log.info('Establishing connection to Admin Server at URL [' + str(wlsAdminURL) + '], attempt #' + str(attemptIdx))
        try:
            connect(wlsAdminUser, wlsAdminPassword, wlsAdminURL)
            break
        except Exception, error:
            exceptionStr = str(error)
            if (exceptionStr.count('failed to be authenticated') > 0):
                log.error('Authentication error occurred connecting to Admin Server at URL [' + str(wlsAdminURL) + ']: ' + str(error))
                raise ScriptError, 'Authentication issue connecting to Admin Server at URL [' + str(wlsAdminURL) + ']: ' + str(error)
            if attemptIdx<maxAttempt:
                log.debug('Establishing connection to Admin Server failed at attempt #' + str(attemptIdx) + ': No Admin Server running on URL [' + str(wlsAdminURL) + '] or the server is not ready to execute WLST command. Delay ' + str(sleeptime) + ' seconds and try again.')
                Thread.currentThread().sleep(sleeptime*1000)
                attemptIdx+=1
            else:
                raise ScriptError, 'Unable to connect to Admin Server at URL [' + str(wlsAdminURL) + ']: ' + str(error)

#=======================================================================================
# __setTargetsOnline
# 
# Sets targets for a particular MBean while online (connected to running domain)
#=======================================================================================

def __setTargetsOnline(bean, targets, targetType, domainProperties):
    try:
        if targets is None or len(targets)==0 or targetType is None or len(targetType)==0:
            targetNames = domainProperties.getProperty('wls.admin.name')
        else:
            targetList=targets.split(',')
            targetNames = None
            for targetKey in targetList:
                targetName = None
                if targetType.upper()=='CLUSTER':
                    targetName=domainProperties.getProperty('wls.cluster.' + str(targetKey) + '.name')
                    cd('/')
                    clusterInstance = lookup(targetName, 'Cluster')
                    bean.addTarget(clusterInstance)
                else:
                    if targetType.upper()=='SERVER':
                        targetName=domainProperties.getProperty('wls.server.' + str(targetKey) + '.name')
                        cd('/')
                        serverInstance = lookup(targetName, 'Server')
                        bean.addTarget(serverInstance)
                    else:
                        log.debug('Does not support target type [' + str(targetType) + '], skipping.')
                        
    except Exception, error:
        raise ScriptError, 'Unable to add target [' + str(targets) + ']: ' + str(error)

    
#=======================================================================================
# __setTargetsOffline
# 
# Sets targets for a bean offline (while connected to the directory structure of a 
# domain that is not running)
#=======================================================================================

def __setTargetsOffline(targets, targetType, domainProperties):
    try:
        if targets is None or len(targets)==0 or targetType is None or len(targetType)==0:
            targetNames = domainProperties.getProperty('wls.admin.name')
        else:
            targetList=targets.split(',')
            targetNames = None
            for targetKey in targetList:
                targetName = None
                if targetType.upper()=='CLUSTER':
                    targetName=domainProperties.getProperty('wls.cluster.' + str(targetKey) + '.name')
                else:
                    if targetType.upper()=='SERVER':
                        targetName=domainProperties.getProperty('wls.server.' + str(targetKey) + '.name')
                    else:
                        log.debug('Does not support target type [' + str(targetType) + '], skipping.')
                        
                if targetNames is None:
                    targetNames = targetName
                else:
                    targetNames = targetNames + ',' + targetName

        if not targetNames is None: 
            set('targets', targetNames)
        else:
            log.debug('Could not add target None to [' + str(bean.getName()) + '], skipping.')
    except Exception, error:
        raise ScriptError, 'Unable to add target [' + str(targets) + ']: ' + str(error)

       
#=======================================================================================
# setConfigProperties
# 
# Set the global script properties
#=======================================================================================

def setConfigProperties(properties):
	"""Sets the global script configuration properties"""

	global scriptConfigProperties
	
	scriptConfigProperties = properties
	
	# done setting global script config

#=======================================================================================
# getConfigProperties
# 
# Return the global script properties
#=======================================================================================

def getConfigProperties():
	"""Returns the global script configuration properties"""

	global scriptConfigProperties
	
	if scriptConfigProperties is None:
		scriptConfigProperties = Properties()
	
	return configProperties
	
	# done returning global script config

#=======================================================================================
# setComponentProperties
# 
# Set the global component properties
#=======================================================================================

def setComponentProperties(properties):
	"""Sets the global script component properties"""

	global scriptComponentProperties
	
	scriptComponentProperties = properties
	
	# done setting global script config


#=======================================================================================
# getComponentProperties
# 
# Return the global script properties
#=======================================================================================

def getComponentProperties():
	"""Returns the global script configuration properties"""

	global scriptComponentProperties
	
	if scriptComponentProperties is None:
		scriptComponentProperties = Properties()
	
	return scriptComponentProperties
	
	# done returning global script config
	


#==============================================================================
# __loadTextFile
#
# Loads contents of the text file specified, performing appropriate error-checking
#==============================================================================

def __loadTextFile(filePath):

	file = open(filePath)
	contents = file.read()
	file.close()
	return contents
	
def getServerName(serverNameInConfig, domainProperties):
	name = domainProperties.getProperty('wls.server.' + serverNameInConfig + '.name')
	replaceName = domainProperties.getProperty('wls.server.' + serverNameInConfig + '.replace.name')
	if name is None:
	        raise ScriptError, 'Could not find server name in configuration matching [' + serverNameInConfig + '].'
	if not replaceName is None:
	    	name = replaceName
	return name

def getMachineName(machineNameInConfig, domainProperties):
	name = domainProperties.getProperty('wls.domain.machine.' + machineNameInConfig + '.name')
	replaceName = domainProperties.getProperty('wls.domain.machine.' + machineNameInConfig + '.replace.name')
	if name is None:
	        raise ScriptError, 'Could not find machine name in configuration matching [' + machineNameInConfig + '].'
	if not replaceName is None:
	    	name = replaceName
	return name

#=======================================================================================
# runDbScripts
# 
# Runs all of the db script files that are specified in the dbScripts list
#=======================================================================================

def runDbScripts(dbScripts, dbURL, dbUser, dbPassword, dbDriver):

	if not dbScripts is None and not dbURL is None and not dbUser is None and not dbPassword is None:
		lang.Class.forName(dbDriver)
		con = jsql.DriverManager.getConnection(dbURL,dbUser,dbPassword)
		stmt = con.createStatement()

		scriptList = dbScripts.split(",")
		for scriptFile in scriptList:
			log.info('Executing script ' + str(scriptFile))
			file = open(scriptFile, 'r')
			script = ''
			for line in file.readlines():
			   line = line.strip()
			   if len(line) > 0:
				   try:
					   if line[len(line)-1] == ';':
						line = line[0:len(line)-1]
						script = script + line + '\n'
						stmt.executeUpdate(script)
						script = ''
					   else:
						script = script + line + '\n'
				   except Exception, error:
					   log.warn('Ignoring error: ' + str(error))
		stmt.close()
		con.close()
		
#==============================================================================
# __readBytes
#
# Reads the contents of the file specified, returning as a byte array
#==============================================================================
def __readBytes(file):
	# Returns the contents of the file in a byte array.
	inputstream = FileInputStream(file)
    
	# Get the size of the file
	length = file.length()

	# Create the byte array to hold the data
	bytes = jarray.zeros(length, "b")

	# Read in the bytes
	offset = 0
	numRead = 1
        while (offset < length) and (numRead > 0):
		numRead = inputstream.read(bytes, offset, len(bytes) - offset)
		offset += numRead

	# Ensure all the bytes have been read in
	if offset < len(bytes):
		log.warn("Could not read entire contents of '" + file.getName()) 

	# Close the input stream and return bytes
	inputstream.close()
	return bytes

#==============================================================================
# getOsType
#
# Returns a string indicating the OS type
#==============================================================================
def getOsType():

    NOT_WINDOWS = 'NOT WINDOWS'

    try:
        osNameTemp = os.getenv('OS',NOT_WINDOWS)
        if not osNameTemp == NOT_WINDOWS and string.find(osNameTemp, 'Windows') == 0:
            return OS_TYPE_WINDOWS

        # non-Windows process
        process = Runtime.getRuntime().exec("uname")
        output = process.getInputStream() # process' output is our input
        br = BufferedReader(InputStreamReader(output))
        osName = br.readLine()

    except Exception, error:
        log.error("Could not determine operating system type: " + str(error))

    return osName

