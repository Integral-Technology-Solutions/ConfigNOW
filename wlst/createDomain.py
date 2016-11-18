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

from java.io import FileWriter,BufferedWriter
import getopt
import sys
import os
import time

createDomainModule = '1.0.6'

log.debug('Loading module [createDomain.py] version [' + createDomainModule + ']')

try:
	serverModule
except NameError:
	execfile('wlst/server.py')

#=======================================================================================
# Create a WLS domain
#=======================================================================================
def __createDomain(configProperties):
	
	webLogicHome=configProperties.getProperty('wls.oracle.home')
	webLogicDir=configProperties.getProperty('wls.name')
	domainPath=configProperties.getProperty('wls.domain.dir')
	domainName=configProperties.getProperty('wls.domain.name')
	domainMode=configProperties.getProperty('wls.domain.mode')
	domainJavaHome=configProperties.getProperty('wls.domain.javahome')
	domainAdminPort=configProperties.getProperty('wls.domain.adminPort')
	wlstemplate=configProperties.getProperty('wls.basic.template')
	
	adminServerName=configProperties.getProperty('wls.admin.name')
	listenAddress=configProperties.getProperty('wls.admin.listener.address')
	listenPort=configProperties.getProperty('wls.admin.listener.port')
	enableSSL=configProperties.getProperty('wls.admin.listener.enableSSL')
	sslPort=configProperties.getProperty('wls.admin.listener.sslPort')
	enableTunneling=configProperties.getProperty('wls.admin.enableTunneling')
	
	username=configProperties.getProperty('wls.admin.username')
	password=configProperties.getProperty('wls.admin.password')

	# CONFIGNOW-98
	configArchiveCount=configProperties.getProperty('wls.domain.config.archive.count')
	configurationAuditType=configProperties.getProperty('wls.domain.config.audit.type')
	version=configProperties.getProperty('wls.version')
	basicTemplate=configProperties.getProperty('wls.basic.template')

	#=======================================================================================
	# Read a domain template.
	#=======================================================================================
	log.info('Reading template')
	
	try:
		if version == '12':
			log.info("Weblogic 12c detected from 'wls.version' property... Adding basic WLS template now")
			readTemplate(str(webLogicHome) + '/' + str(webLogicDir) +'/common/templates/wls/wls.jar')
		else:
			readTemplate(str(webLogicHome) + '/' + str(webLogicDir) + '/common/templates/domains/wls.jar')
		
	except Exception, error:
		raise ScriptError, 'Unable to read template from  [' + str(webLogicHome) + '/' + str(webLogicDir) + '/common/templates/domains/wls.jar' + '] : ' + str(error)


	try:
		# set domain options
		#setOption('CreateStartMenu','false')
		setOption('ServerStartMode', str(domainMode))
		setOption('OverwriteDomain','true')
		setOption('JavaHome', domainJavaHome)
	
		if not domainAdminPort is None and len(domainAdminPort)>0:
			cd('/')
			cmo.setAdministrationPortEnabled(1)
			cmo.setAdministrationPort(int(domainAdminPort))
		else:
			cd('/')
			cmo.setAdministrationPortEnabled(0)
			
		if not configArchiveCount is None and len(configArchiveCount)>0:
			log.info("Enabling configuration archiving (retaining " + configArchiveCount + " copies)")
			cd('/')
			cmo.setConfigBackupEnabled(1);
			cmo.setArchiveConfigurationCount(int(configArchiveCount))
		else:
			cd('/')
			cmo.setConfigBackupEnabled(0)

		if not configurationAuditType is None and len(configurationAuditType)>0:
			log.info("Setting configuration audit type to '" + configurationAuditType + "'")
			cmo.setConfigurationAuditType(configurationAuditType)
			
	except Exception, error:
		raise ScriptError, 'Unable to set domain options : ' + str(error)
	

	#=======================================================================================
	# Configure admin listener address and SSL.
	#=======================================================================================
	
	try:
		cd('/Servers/AdminServer')
		cmo.setName(str(adminServerName))
		set('ListenPort', int(listenPort))
		set('ListenAddress',listenAddress)
			
		create(str(adminServerName),'SSL')
		cd('SSL/' + str(adminServerName))
		if not enableSSL is None and enableSSL.upper()=='TRUE':
			set('Enabled', 'True')
			set('ListenPort', int(sslPort))
		else:
			set('Enabled', 'False')
	except Exception, error:
		raise ScriptError, 'Unable to configure listen address and port for admin server  [' + str(adminServerName) + '] : ' + str(error)
		
	#=======================================================================================
	# Configure tunnelling.
	#=======================================================================================
	try:
		cd('/Servers/' + str(adminServerName))
		if not enableTunneling is None and enableTunneling.upper()=='TRUE':
			set('TunnelingEnabled', 'True')
		else:
			set('TunnelingEnabled', 'False')
	except Exception, error:
		raise ScriptError, 'Unable to configure tunnelling for admin server  [' + str(adminServerName) + '] : ' + str(error)
	
	#=======================================================================================
	# Configure admin server custom log file
	#=======================================================================================
	try:		
		adminCustomLog=configProperties.getProperty('wls.admin.log.custom')
		logFileName=configProperties.getProperty('wls.admin.log.filename')
		limitNumOfFile=configProperties.getProperty('wls.admin.log.limitNumOfFile')
		fileToRetain=configProperties.getProperty('wls.admin.log.fileToRetain')
		rotateOnStartup=configProperties.getProperty('wls.admin.log.rotateLogOnStartup')
		logFileSeverity=configProperties.getProperty('wls.admin.log.logFileSeverity')
		broadcastSeverity=configProperties.getProperty('wls.admin.log.broadcastSeverity')
		memoryBufferSeverity=configProperties.getProperty('wls.admin.log.memoryBufferSeverity')
		rotationType=configProperties.getProperty('wls.admin.log.rotationType')
		fileMinSize=configProperties.getProperty('wls.admin.log.fileMinSize')
		rotationTime=configProperties.getProperty('wls.admin.log.rotationTime')
		fileTimeSpan=configProperties.getProperty('wls.admin.log.fileTimeSpan')
		rotationDir=configProperties.getProperty('wls.admin.log.rotationDir')
		
		if not adminCustomLog is None and adminCustomLog.upper()=='TRUE':
			cd('/Servers/' + str(adminServerName))		
			logObj = create(adminServerName, 'Log')
			logObj.setFileName(logFileName)
			if not limitNumOfFile is None and limitNumOfFile.upper()=='TRUE':
	
				log.debug("* Limiting number of files retained...")
				logObj.setNumberOfFilesLimited(true)
				logObj.setFileCount(int(fileToRetain))
			if not rotateOnStartup is None and rotateOnStartup.upper()=='TRUE':
				log.debug("* Setting rotate log on startup")
				logObj.setRotateLogOnStartup(true)
			else:
				logObj.setRotateLogOnStartup(0)
			
			logObj.setLogFileSeverity(logFileSeverity)
			logObj.setDomainLogBroadcastSeverity(broadcastSeverity)
			logObj.setMemoryBufferSeverity(memoryBufferSeverity)
			logObj.setRotationType(rotationType)
			if rotationType.upper()=='BYTIME':
				logObj.setRotationTime(rotationTime)
				logObj.setFileTimeSpan(int(fileTimeSpan))
			else:
				if rotationType.upper()=='BYSIZE':
					logObj.setFileMinSize(int(fileMinSize))
					
			log.setLogFileRotationDir(rotationDir)
	except Exception, error:
		raise ScriptError, 'Unable to configure logging properties on admin server  [' + str(adminServerName) + '] : ' + str(error)
	
	#=======================================================================================
	# Create a new web server and configure logging for web server
	#=======================================================================================
	try:
		webserver = create(str(adminServerName), 'WebServer')
		cd('WebServer/' + str(adminServerName))
		httplog = create(str(adminServerName), 'WebServerLog')
		
		httpLogEnable=configProperties.getProperty('wls.admin.httplog.enable')
		if not httpLogEnable is None and httpLogEnable.upper()=='TRUE':
			httplog.setLoggingEnabled(1)
			
			httpLogFileName=configProperties.getProperty('wls.admin.httplog.filename')
			httpLimitNumOfFile=configProperties.getProperty('wls.admin.httplog.limitNumOfFile')
			httpFileToRetain=configProperties.getProperty('wls.admin.httplog.fileToRetain')
			httpRotateOnStartup=configProperties.getProperty('wls.admin.httplog.rotateLogOnStartup')
			httpRotationType=configProperties.getProperty('wls.admin.httplog.rotationType')
			httpFileMinSize=configProperties.getProperty('wls.admin.httplog.fileMinSize')
			httpRotationTime=configProperties.getProperty('wls.admin.httplog.rotationTime')
			httpFileTimeSpan=configProperties.getProperty('wls.admin.httplog.fileTimeSpan')
			httpRotationDir=configProperties.getProperty('wls.admin.httplog.rotationDir')
			httpFormat=configProperties.getProperty('wls.admin.httplog.format')
			
			httplog.setFileName(httpLogFileName)
			if not httpLimitNumOfFile is None and httpLimitNumOfFile.upper()=='TRUE':
				httplog.setNumberOfFilesLimited(1)
				httplog.setFileCount(int(httpFileToRetain))
			else:
				httplog.setNumberOfFilesLimited(0)
			if not httpRotateOnStartup is None and httpRotateOnStartup.upper()=='TRUE':		
				httplog.setRotateLogOnStartup(1)
			else:
				httplog.setRotateLogOnStartup(0)
				
			httplog.setELFFields(httpFormat)
			httplog.setRotationType(httpRotationType)
			if httpRotationType.upper()=='BYTIME':
				httplog.setRotationTime(httpRotationTime)
				httplog.setFileTimeSpan(int(httpFileTimeSpan))
			else:
				if httpRotationType.upper()=='BYSIZE':
					httplog.setFileMinSize(int(httpFileMinSize))
					
			httplog.setLogFileRotationDir(httpRotationDir)
		else:
			if not httpLogEnable is None and httpLogEnable.upper()=='FALSE':
				httplog.setLoggingEnabled(0)
	except Exception, error:
		raise ScriptError, 'Unable to configure http logging properties on admin server  [' + str(adminServerName) + '] : ' + str(error)

	#=======================================================================================
	# Configure domain log
	#=======================================================================================
	try:
		
		domainCustomLog='false'
		domainCustomLog=configProperties.getProperty('wls.domain.log.custom')
		domainLogFileName=configProperties.getProperty('wls.domain.log.filename')
		domainLimitNumOfFile=configProperties.getProperty('wls.domain.log.limitNumOfFile')
		domainFileToRetain=configProperties.getProperty('wls.domain.log.fileToRetain')
		domainRotateOnStartup=configProperties.getProperty('wls.domain.log.rotateLogOnStartup')
		domainLogFileSeverity=configProperties.getProperty('wls.domain.log.logFileSeverity')
		domainRotationType=configProperties.getProperty('wls.domain.log.rotationType')
		domainFileMinSize=configProperties.getProperty('wls.domain.log.fileMinSize')
		domainRotationTime=configProperties.getProperty('wls.domain.log.rotationTime')
		domainFileTimeSpan=configProperties.getProperty('wls.domain.log.fileTimeSpan')
		domainRotationDir=configProperties.getProperty('wls.domain.log.rotationDir')
		
		if not domainCustomLog is None and domainCustomLog.upper()=='TRUE':
			cd('/')
			domainLog = create(domainName, 'Log')
			domainLog.setFileName(domainLogFileName)
			if not domainLimitNumOfFile is None:
				if domainLimitNumOfFile.upper()=='TRUE':
					domainLog.setNumberOfFilesLimited(true)
					domainLog.setFileCount(int(domainFileToRetain))
				else:
					domainLog.setNumberOfFilesLimited(false)
			if not domainRotateOnStartup is None:
				if domainRotateOnStartup.upper()=='TRUE':
					domainLog.setRotateLogOnStartup(true)
				else:
					domainLog.setRotateLogOnStartup(false)
			
			domainLog.setLogFileSeverity(domainLogFileSeverity)
			domainLog.setRotationType(domainRotationType)
			if domainRotationType.upper()=='BYTIME':
				domainLog.setRotationTime(domainRotationTime)
				domainLog.setFileTimeSpan(int(domainFileTimeSpan))
			else:
				if domainRotationType.upper()=='BYSIZE':
					domainLog.setFileMinSize(int(domainFileMinSize))
					
			domainLog.setLogFileRotationDir(domainRotationDir)
	except Exception, error:
		raise ScriptError, 'Unable to configure logging properties on domain [' + str(domainName) + '] : ' + str(error)
	
	#=======================================================================================
	# Configure admin channel.
	#=======================================================================================
	channelName=configProperties.getProperty('wls.admin.channel.name')
	channelProtocol=configProperties.getProperty('wls.admin.channel.protocol')
	channelListenerAddr=configProperties.getProperty('wls.admin.channel.listener.address')
	channelListenerPort=configProperties.getProperty('wls.admin.channel.listener.port')
	channelPublicListenerAddr=configProperties.getProperty('wls.admin.channel.listener.publicAddress')
	channelPublicListenerPort=configProperties.getProperty('wls.admin.channel.listener.publicPort')
	httpEnable=configProperties.getProperty('wls.admin.channel.httpEnable')	
	
	if not channelName is None and len(channelName)>0:
		__configureChannel(adminServerName, channelName, 0, channelProtocol, channelListenerAddr, channelListenerPort, channelPublicListenerAddr, channelPublicListenerPort, httpEnable)

	#=======================================================================================
	# Define the user password for weblogic.
	#=======================================================================================
	try:
		cd('/')
		cd('Security/base_domain/User/' + username)
		cmo.setPassword(password)
	except Exception, error:
		raise ScriptError, 'Unable to set user/password : ' + str(error)

	#=======================================================================================		
	# Write the domain
	#=======================================================================================
	try:
		log.info('Writing domain')
		writeDomain(str(domainPath) + '/' + str(domainName))
		
		securityDir = File(domainPath + File.separator + domainName + File.separator + 'servers' + File.separator + str(adminServerName) + File.separator + 'security')
		if not securityDir.exists():
			securityDir.mkdirs()

		bootFile = File(securityDir.getAbsolutePath()  + File.separator + 'boot.properties')
		bootFile.createNewFile()
		fileWriter = FileWriter(bootFile)	
		bufWriter = BufferedWriter(fileWriter)
		bufWriter.write('username=' + str(username))
		bufWriter.newLine()
		bufWriter.write('password=' + str(password))
		bufWriter.close()
	except Exception, error:
		raise ScriptError, 'Unable to write domain  [' + str(domainPath) + '/' + str(domainName) + '] : ' + str(error)
	#=======================================================================================
	# Close the domain template.
	#=======================================================================================
	
	closeTemplate()

	
#==============================================================================
# __addTemplate
#
# Loops through and adds all configured templates to domain, calling 'addTemplate'
#==============================================================================
def __addTemplate(configProperties):
	
	# Accoding to Mobile TV script
	setOption('ReplaceDuplicates', 'false')
	
	webLogicHome=configProperties.getProperty('wls.oracle.home')
	webLogicDir=configProperties.getProperty('wls.name')
	
	templates = configProperties.getProperty('wls.templates')
	
	if not templates is None and len(templates) > 0:
		templateList=templates.split(',')
		
		for templateRefName in templateList:
			templateFile = configProperties.getProperty('wls.template.' + str(templateRefName) + '.file')
			propKeys = configProperties.keys()
			while propKeys.hasMoreElements():
				key = propKeys.nextElement()
				templateFile = templateFile.replace("@@" + str(key) + "@@", str(configProperties.getProperty(str(key))))
			log.info('Adding template: ' + str(templateFile))
			addTemplate(templateFile)
	
	
#==============================================================================
# __processPostDomainCreation
#
# Performs the majority of post-domain creation configuration, once the 
# domain has been physically created.
#
# @TODO - this function should be split into a number of smaller functions, as
# there are several clear delineations of functionality here.
#==============================================================================
def __processPostDomainCreation(configProperties):
	
	#libraries=configProperties.getProperty('wls.domain.applibraries')
	#appconfigs=configProperties.getProperty('wls.domain.appconfigs')
	adminMemArg = configProperties.getProperty('wls.admin.vmarguments')
	userMemArgs=configProperties.getProperty('wls.domain.vmarguments')
	extraProps=configProperties.getProperty('wls.domain.extraprops')
	domainVariables=configProperties.getProperty('wls.domain.customenvvars')
	domainPath=configProperties.getProperty('wls.domain.dir')
	domainName=configProperties.getProperty('wls.domain.name')
	adminServerName = configProperties.getProperty('wls.admin.name')
	preclasspaths = configProperties.getProperty('wls.domain.preclasspaths')
	postclasspaths = configProperties.getProperty('wls.domain.postclasspaths')
	paths = configProperties.getProperty('wls.domain.path')
	
	log.info('Starting post domain patch process')
	
	#if (not libraries is None and len(libraries)>0) or (not appconfigs is None and len(appconfigs)>0) or (not domainVariables is None and len(domainVariables)>0) or (not userMemArgs is None and len(userMemArgs)>0) or (not extraProps is None and len(extraProps)>0):
	#if (not domainVariables is None and len(domainVariables)>0) or (not userMemArgs is None and len(userMemArgs)>0) or (not extraProps is None and len(extraProps)>0):
	newline=os.linesep
	classpathSep=os.pathsep
	pathSep=os.sep
	
	if classpathSep==';':
	    domainEnvFilename='setDomainEnv.cmd'
	    customEnvFilename='setCustomEnv.cmd'
	else:
	    domainEnvFilename='setDomainEnv.sh'
	    customEnvFilename='setCustomEnv.sh'
	
	#additionalClasspath = ''
	
	#=======================================================================================
	# Populate application libraries
	#=======================================================================================    
	
	#if not libraries is None and len(libraries)>0:        
	    #libraryList=libraries.split(',')
	    #for library in libraryList:
	        #librarySource=configProperties.getProperty('wls.domain.applibrary.' + str(library) + '.source')
	        #libraryDestination=configProperties.getProperty('wls.domain.applibrary.' + str(library) + '.destination')
	
	        #srcDir = File(librarySource)
	        #fileList = srcDir.listFiles()
	        #for file in fileList:
	            #additionalClasspath += str(libraryDestination) + pathSep + str(file.getName()) + str(classpathSep)
	#else:
	    #log.debug('No application specific libraries set up, skipping.')
	
	#=======================================================================================
	# Populate application configurations
	#=======================================================================================    
	
	#if not appconfigs is None and len(appconfigs)>0:
	    #appconfigList=appconfigs.split(',')
	    #for appconfig in appconfigList:
	        #appconfigSource=configProperties.getProperty('wls.domain.appconfig.' + str(appconfig) + '.source')
	        #appconfigDestination=configProperties.getProperty('wls.domain.appconfig.' + str(appconfig) + '.destination')
	        #additionalClasspath += str(appconfigDestination) + str(classpathSep)
	 
	#=======================================================================================
	# Processing domainEnvFilename file
	#======================================================================================= 
	
	if not File(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(domainEnvFilename) + '.backup').exists():
		fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(domainEnvFilename),'r')
		contents = fdomainEnv.read()
		fdomainEnv.close()
		
		fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(domainEnvFilename) + '.backup','w')
		fdomainEnv.write(contents)
		fdomainEnv.close()
	
	if File(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename)).exists():
		os.remove(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename))
	
	if classpathSep==':':
		fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
		fdomainEnv.write('#!/bin/sh' + newline)
		fdomainEnv.close()
	
	if not paths is None and len(paths)>0:
	
	    log.debug('Setting paths up ' + str(paths))
	    fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	    additionalPath=''
	    
	    pathList=paths.split(',')
	    for path in pathList:
                additionalPath=additionalPath + path + classpathSep
	    fdomainEnv.write(newline)
	    if classpathSep==';':
	        fdomainEnv.write('set PATH=%PATH%;' + additionalPath + newline)
	    else:    
	        fdomainEnv.write('set PATH=${PATH}:' + additionalPath + newline)
	
	    fdomainEnv.close()	    

	if not preclasspaths is None and len(preclasspaths)>0:

	    fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	    additionalPreclasspath=''
	    
	    if classpathSep==';':
	    	preclasspathList=preclasspaths.split(',')
	    	for preclasspath in preclasspathList:
	    		additionalPreclasspath=additionalPreclasspath + str(domainPath) + pathSep + str(domainName) + pathSep + 'lib' + pathSep + 'redback' + pathSep  + str(preclasspath) + classpathSep
	    	fdomainEnv.write(newline)
	    	fdomainEnv.write('set EXT_PRE_CLASSPATH=' + additionalPreclasspath + newline)
	    else:
	    	preclasspathList=preclasspaths.split(',')
	    	for preclasspath in preclasspathList:
	    		additionalPreclasspath=additionalPreclasspath + str(domainPath) + pathSep + str(domainName) + pathSep + 'lib' + pathSep + 'redback' + pathSep  + str(preclasspath) + classpathSep
	    	fdomainEnv.write(newline)
	    	fdomainEnv.write('EXT_PRE_CLASSPATH="' + additionalPreclasspath + '"' + newline)
	
	    fdomainEnv.close()

	if not postclasspaths is None and len(postclasspaths)>0:
	    
	    fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	    additionalPostclasspath=''
	    
	    if classpathSep==';':
	    	postclasspathList=postclasspaths.split(',')
	    	for postclasspath in postclasspathList:
	    		additionalPostclasspath=additionalPostclasspath + str(domainPath) + pathSep + str(domainName) + pathSep + 'lib' + pathSep + 'redback' + pathSep  + str(postclasspath) + classpathSep
	    	fdomainEnv.write(newline)
	    	fdomainEnv.write('set EXT_POST_CLASSPATH=' + additionalPostclasspath + newline)
	    else:
	    	preclasspathList=postclasspaths.split(',')
	    	for postclasspath in preclasspathList:
	    		additionalPostclasspath=additionalPostclasspath + str(domainPath) + pathSep + str(domainName) + pathSep + 'lib' + pathSep + 'redback' + pathSep  + str(postclasspath) + classpathSep
	    	fdomainEnv.write(newline)
	    	fdomainEnv.write('EXT_POST_CLASSPATH="' + additionalPostclasspath + '"' + newline)	
	    	
	    fdomainEnv.close()
	
	servers=configProperties.getProperty('wls.servers')
	if not servers is None and len(servers)>0:
		serverList = servers.split(',')
		for server in serverList:
			serverName = configProperties.getProperty('wls.server.' + str(server) + '.name')
			serverCustomVars = configProperties.getProperty('wls.server.' + str(server) + '.customenvvars')
	        if not serverCustomVars is None and len(serverCustomVars)>0:
		        if classpathSep==';':
		        	expcmd = 'set'
		        else:
		        	expcmd = 'export'
		        	
		        fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	
		        serverCustomVarList = serverCustomVars.split(',')
		        for serverCustomVar in serverCustomVarList:
		        	text=configProperties.getProperty('wls.server.' + str(server) + '.customenvvar.' + str(serverCustomVar) + '.text')
		        	if text.find('=')!=-1:
		        		if classpathSep==';':
		        			fdomainEnv.write(str(newline))
		        			fdomainEnv.write('if "%SERVER_NAME%"=="' + str(serverName) + '" (' + str(newline))
		        			fdomainEnv.write('	' + expcmd + ' ' + str(text) + str(newline))
		        			fdomainEnv.write(')' + str(newline))		
		        		else:
		        			fdomainEnv.write(str(newline))
		        			fdomainEnv.write('if [ "${SERVER_NAME}" = "' + str(serverName) + '" ] ; then' + str(newline))
		        			fdomainEnv.write('	' + expcmd + ' ' + str(text) + str(newline))
		        			fdomainEnv.write('fi' + str(newline))
		        	else:
		        		log.error('Incorrect export variable declaration : expected <name>=<value> : ' + str(text))		        		
		        fdomainEnv.close()
	    
	if not domainVariables is None and len(domainVariables)>0:
	
	    fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	
	    if classpathSep==';':
	    	expcmd = 'set'
	    else:
	    	expcmd = 'export'
	    	
	    domainVarList = domainVariables.split(',')
	    for domainVar in domainVarList:
	    	text=configProperties.getProperty('wls.domain.customenvvar.' + str(domainVar) + '.text')
	    	if text.find('=')!=-1:
	    		fdomainEnv.write(str(newline))
	    		fdomainEnv.write(expcmd + ' ' + str(text) + str(newline))	        				
	    	else:
	    		log.error('Incorrect export variable declaration : expected <name>=<value> : ' + str(text))	
	    fdomainEnv.close()
	
	if (not userMemArgs is None and len(userMemArgs)>0) or (not adminMemArg is None and len(adminMemArg)>0):
	    
	    fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	
		# Use classpathsep to determine O/S, and write script contents accordingly
	    if classpathSep==';':
	    	if not userMemArgs is None and len(userMemArgs)>0:
		    	fdomainEnv.write(newline)
		    	fdomainEnv.write('if NOT "%SERVER_NAME%"=="' + str(adminServerName) + '" (' + newline)
		    	fdomainEnv.write('	if NOT "%SERVER_NAME%"=="" (' + newline)
		    	fdomainEnv.write('		set USER_MEM_ARGS=' + str(userMemArgs) + newline)
		    	fdomainEnv.write('	)' + newline)
		    	fdomainEnv.write(')' + newline)
	    	
	    	if not adminMemArg is None and len(adminMemArg)>0:
	    		fdomainEnv.write(newline)
	    		fdomainEnv.write('if "%SERVER_NAME%"=="' + str(adminServerName) + '" (' + newline)
	    		fdomainEnv.write('	set USER_MEM_ARGS=' + str(adminMemArg) + newline)
	    		fdomainEnv.write(')' + newline)
	    		fdomainEnv.write('if "%SERVER_NAME%"=="" (' + newline)
	    		fdomainEnv.write('	set USER_MEM_ARGS=' + str(adminMemArg) + newline)
	    		fdomainEnv.write(')' + newline)
	    else:
	    	if not userMemArgs is None and len(userMemArgs)>0:
		    	fdomainEnv.write(newline)
		    	fdomainEnv.write('if [ "${SERVER_NAME}" != "' + str(adminServerName) + '" ] ; then' + newline)
		    	fdomainEnv.write('	if [ "${SERVER_NAME}" = "" ] ; then' + newline)
		    	fdomainEnv.write('		USER_MEM_ARGS="' + str(userMemArgs) + '"' + newline)
		    	fdomainEnv.write('	fi' + newline)
		    	fdomainEnv.write('fi' + newline)
	    	
	    	if not adminMemArg is None and len(adminMemArg)>0:
	    		fdomainEnv.write(newline)
	    		fdomainEnv.write('if [ "${SERVER_NAME}" = "' + str(adminServerName) + '" ] || [ "${SERVER_NAME}" = "" ] ; then' + newline)
	    		fdomainEnv.write('	USER_MEM_ARGS="' + str(adminMemArg) + '"' + newline)
	    		fdomainEnv.write('fi' + newline)
	    		#fdomainEnv.write(newline)
	    		#fdomainEnv.write('if [ "${SERVER_NAME}" = "" ] ; then' + newline)
	    		#fdomainEnv.write('	USER_MEM_ARGS="' + str(adminMemArg) + '"' + newline)
	    		#fdomainEnv.write('fi' + newline)
	
	    fdomainEnv.close()
	
	servers=configProperties.getProperty('wls.servers')
	if not servers is None and len(servers)>0:
		serverList = servers.split(',')
		for server in serverList:
			serverName = configProperties.getProperty('wls.server.' + str(server) + '.name')
			memargs = configProperties.getProperty('wls.server.' + str(server) + '.memarguments')
	        if not memargs is None and len(memargs)>0:
	
		        fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
		        #fdomainEnv.seek(2)
		        if classpathSep==';':
		        	fdomainEnv.write(str(newline))
		        	fdomainEnv.write('if "%SERVER_NAME%"=="' + str(serverName) + '" (' + str(newline))
		        	fdomainEnv.write('	set USER_MEM_ARGS=' + str(memargs) + str(newline))
		        	fdomainEnv.write(')' + str(newline))
		        else:
		        	fdomainEnv.write(str(newline))
		        	fdomainEnv.write('if [ "${SERVER_NAME}" = "' + str(serverName) + '" ] ; then' + newline)
		        	fdomainEnv.write('	USER_MEM_ARGS="' + str(memargs) + '"' + newline)
		        	fdomainEnv.write('fi' + newline)
	
		        fdomainEnv.close()
		        
	if not extraProps is None and len(extraProps)>0:
	
	    log.debug('Setting extra properties')
	    fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	
	    if classpathSep==';':
	    	fdomainEnv.write(newline)
	    	fdomainEnv.write('set EXTRA_JAVA_PROPERTIES=' + str(extraProps) + newline)
	    else:
	    	fdomainEnv.write(newline)
	    	fdomainEnv.write('EXTRA_JAVA_PROPERTIES="' + str(extraProps) + '"' + newline)
	
	    fdomainEnv.close()
	    
	servers=configProperties.getProperty('wls.servers')
	if not servers is None and len(servers)>0:
		serverList = servers.split(',')
		for server in serverList:
			serverName = configProperties.getProperty('wls.server.' + str(server) + '.name')
			serverProps = configProperties.getProperty('wls.server.' + str(server) + '.extraprops')
	        if not serverProps is None and len(serverProps)>0:
		        fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(customEnvFilename),'a')
	
		        if classpathSep==';':
		        	fdomainEnv.write(newline)
		        	fdomainEnv.write('if "%SERVER_NAME%"=="' + str(serverName) + '" (' + newline)
		        	fdomainEnv.write('	set EXTRA_JAVA_PROPERTIES=' + str(serverProps) + newline)
		        	fdomainEnv.write(')' + newline)
		        else:
		        	fdomainEnv.write(newline)
		        	fdomainEnv.write('if [ "${SERVER_NAME}" = "' + str(serverName) + '" ] ; then' + newline)
		        	fdomainEnv.write('	EXTRA_JAVA_PROPERTIES="' + str(serverProps) + '"' + newline)
		        	fdomainEnv.write('fi' + newline)
	
		        fdomainEnv.close()
	
	fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(domainEnvFilename) + '.backup','r')
	lines = fdomainEnv.readlines()
	fdomainEnv.close()
	
	fdomainEnv = open(str(domainPath) + pathSep + str(domainName) + pathSep + 'bin' + pathSep + str(domainEnvFilename),'w')
	
	calledCustomEnv = False
	for line in lines:
	    if classpathSep==';':
	    	if line.find('call "%LONG_DOMAIN_HOME%/bin/' + str(customEnvFilename) + '"')==-1 and line.find('set EXTRA_JAVA_PROPERTIES=')==-1 and line.find('set USER_MEM_ARGS=')==-1 and line.find('set EXT_PRE_CLASSPATH=')==-1 and line.find('set EXT_POST_CLASSPATH=')==-1:
	    	#if line.find('call "%LONG_DOMAIN_HOME%/bin/' + str(customEnvFilename) + '"')==-1 and line.find('set EXTRA_JAVA_PROPERTIES=')==-1 and line.find('set USER_MEM_ARGS=')==-1:
	    		fdomainEnv.write(str(line))
	    	if line.find('call ')>-1:
	    		fdomainEnv.write('call "%LONG_DOMAIN_HOME%/bin/' + customEnvFilename + '"' + str(newline))

	    else:
	    	#if line.find('. $LONG_DOMAIN_HOME/bin/' + str(customEnvFilename))==-1 and line.find('EXTRA_JAVA_PROPERTIES=')==-1 and line.find('USER_MEM_ARGS=')==-1 and line.find('EXT_PRE_CLASSPATH=')==-1 and line.find('EXT_POST_CLASSPATH=')==-1:
	    	#if line.find('. $LONG_DOMAIN_HOME/bin/' + str(customEnvFilename))==-1 and line.find('EXTRA_JAVA_PROPERTIES=')==-1 and line.find('USER_MEM_ARGS=')==-1 :
	    	if line.find('. ${WL_HOME}/common/bin/commEnv.sh') > -1 and not calledCustomEnv:
	    		fdomainEnv.write('. $LONG_DOMAIN_HOME/bin/' + customEnvFilename + str(newline))
	    		calledCustomEnv = True
	    	# if line.find('export LONG_DOMAIN_HOME')>-1 or line.find('. ${DOMAIN_HOME}/bin/setSOADomainEnv.sh')>-1:
	    	fdomainEnv.write(str(line))
		
	fdomainEnv.close()
	
	###
	# Check if we're using Pointbase - if so, then we need to hack the port 
	# specified in setDomainEnv, because there is NO OTHER WAY TO DO THIS
	# AUTOMATICALLY (WHY OH WHY, ORACLE?!?!)
	###
	dbType=configProperties.getProperty('wls.db.type')
	if not dbType is None and len(dbType) > 0 and dbType == "pointbase":
		dbPort = configProperties.getProperty('wls.db.port')
		if not dbPort is None and len(dbPort) > 0:
			log.debug("Setting Pointbase port to '" + dbPort + "'")
			setPointbasePort(dbPort, domainPath, domainName, domainEnvFilename)
		else:
			log.debug("Pointbase database selected, but no port set. Assuming default port (9093)")
			
			
#==============================================================================
# setPointbasePort
#
# Sets the Pointbase port 
# domain has been physically created.
#
# @TODO - this function should be split into a number of smaller functions, as
# there are several clear delineations of functionality here.
#==============================================================================
def setPointbasePort(dbPort, domainPath, domainName, domainEnvFilename):

	pathSep=os.sep

	fileToModify = domainPath + pathSep + domainName + pathSep + 'bin' + pathSep + domainEnvFilename
	f = open(fileToModify, "r")
	textRead = f.read()
	f.close()
	# easiest just to do both substitutions
	textRead = re.sub(r'POINTBASE_PORT="9093"', 'POINTBASE_PORT="' + dbPort + '"', textRead)	
	textRead = re.sub(r'POINTBASE_PORT=9093', 'POINTBASE_PORT=' + dbPort, textRead)
	f = open(fileToModify, "w")
	f.write(textRead)
	f.close()
