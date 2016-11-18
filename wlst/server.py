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
from jarray import array, zeros

serverModule = '1.2.1'

log.debug('Loading module [server.py] version [' + serverModule + ']')

#=======================================================================================
# Configure servers
#=======================================================================================
def configureServers(resourcesProperties, domainProperties):
    servers=domainProperties.getProperty('wls.servers')
    if not servers is None and len(servers) > 0:
        serverList = servers.split(',')
        for server in serverList:
            arguments = domainProperties.getProperty('wls.server.' + server + '.serverstart.arguments')
	    name = domainProperties.getProperty('wls.server.' + server + '.name')
	    replaceName = domainProperties.getProperty('wls.server.' + server + '.replace.name')
	    autoMigrationEnabled = domainProperties.getProperty('wls.server.' + server + '.auto.migration.enabled')
	    migrationMachine = domainProperties.getProperty('wls.server.' + server + '.migration.machine')
	    defaultStoreDir = domainProperties.getProperty('wls.server.' + server + '.default.store.dir')
	    rootDir = domainProperties.getProperty('wls.server.' + server + '.root.dir')
	    
	    if not replaceName is None:
	    	name = replaceName
	    if not arguments is None:
	    	cd ('/Servers/' + str(name) + '/ServerStart/' + str(name))
	    	log.info('Setting server start arguments for ' + str(name))
	    	set('Arguments',arguments)
	    if not rootDir is None:
	    	cd ('/Servers/' + str(name) + '/ServerStart/' + str(name))
	    	log.info('Setting root directory for ' + str(name))
	    	set('RootDirectory',rootDir)
	    if not defaultStoreDir is None:
	    	file = File(defaultStoreDir)
	    	if not file.exists():
	    		if file.mkdirs():
	    			log.info('Default store directory [' + str(defaultStoreDir) + '] has been created successfully.')
	    	log.info('Setting default store directory [' + str(defaultStoreDir) + '] for server [' + str(name) + '].')
	    	cd('/Servers/' + str(name) + '/DefaultFileStore/' + str(name))
	    	cmo.setDirectory(defaultStoreDir)
	    
#=======================================================================================
# Configure cluster
#=======================================================================================
def configureClusters(resourcesProperties, domainProperties):
    clusters=domainProperties.getProperty('wls.clusters')
    
    if not clusters is None and len(clusters) > 0:
        clusterList = clusters.split(',')
        for cluster in clusterList:
            clusterName=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.name')
            frontendHost=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.frontend.host')
            frontendHttpPort=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.frontend.http.port')
            frontendHttpsPort=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.frontend.https.port')
            
            cluster = lookup(str(clusterName), 'Cluster')
	    
            try:
                if not frontendHost is None:
                    log.info('Setting front end host [' + str(frontendHost) + '].' )
                    cluster.setFrontendHost(str(frontendHost))
                if not frontendHttpPort is None:
                    log.info('Setting front end HTTP port [' + str(frontendHttpPort) + '].' )
                    cluster.setFrontendHTTPPort(int(frontendHttpPort))
                if not frontendHttpsPort is None:
                    log.info('Setting front end HTTPS port [' + str(frontendHttpsPort) + '].' )
                    cluster.setFrontendHTTPSPort(int(frontendHttpsPort))
            except Exception, error:
                
                log.error(str(error))

#=======================================================================================
# Create managed servers if defined.
#=======================================================================================
def __createServers(online, configProperties):
    servers=configProperties.getProperty('wls.servers')
    
    if not servers is None and len(servers) > 0:
        serverList = servers.split(',')
        for server in serverList:
            __createServer(server, online, configProperties)
            
#=======================================================================================
# Create a server in domain.
#=======================================================================================

def __createServer(server, online, configProperties):

    #=======================================================================================
    # Read managed server properties.
    #=======================================================================================
    domainName=configProperties.getProperty('wls.domain.name')
    serverName=configProperties.getProperty('wls.server.' + str(server) + '.name')
    replaceName=configProperties.getProperty('wls.server.' + str(server) + '.replace.name')
    listenAddress=configProperties.getProperty('wls.server.' + str(server) + '.listener.address')
    listenPort=configProperties.getProperty('wls.server.' + str(server) + '.listener.port')
    enableSSL=configProperties.getProperty('wls.server.' + str(server) + '.listener.enableSSL')
    sslPort=configProperties.getProperty('wls.server.' + str(server) + '.listener.sslPort')
    enableTunneling=configProperties.getProperty('wls.server.' + str(server) + '.enableTunneling')
    machine=configProperties.getProperty('wls.server.' + str(server) + '.machine')
    enableHostnameVerification=configProperties.getProperty('wls.server.' + str(server) + '.enableHostnameVerification')
    autoRestartOnFailure=configProperties.getProperty('wls.server.' + str(server) + '.autoRestart')
    wlsVersion=configProperties.getProperty('wls.version')
    coherenceUnicastAddress=configProperties.getProperty('wls.server.'+str(server)+'.coherence.UnicastListenAddress')
   
    #=======================================================================================
    # Configure the Managed Server and SSL port.
    #=======================================================================================
    serverInstance = None
    serverInstanceExist = 0
    try:
        cd('/')
        log.info('Lookup server [' + str(serverName) + ']')
        if online:
            serverInstance = lookup(str(serverName), 'Server')
        else:
            try:
                cd('Servers/' + str(serverName))
                serverInstance = cmo
            except Exception, error:
                log.info('Unable to find server [' + str(serverName) + ']. The server will be created.')
    except WLSTException, error:
        log.info('Unable to find server [' + str(serverName) + ']. The server will be created.')

    #=======================================================================================
    # Assign admin server to machine.
    #=======================================================================================
    machineReplaceName = None
    if not machine is None and len(machine)>0 and configProperties.getProperty('wls.admin.name') == serverName:
        machineName=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.name')
        machineReplaceName=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.replace.name')
    if not machineReplaceName is None:
        machineName=machineReplaceName
        try:
            cd('/')
            if online:
                machineInstance = lookup(machineName, 'Machine')
                log.info('Setting machine [' + str(machineName) + '] to admin server [' + str(serverName) + '].')
                serverInstance.setMachine(machineInstance)
            else:
                log.info('Assigning machine [' + str(machineName) + '] to admin server [' + str(serverName) + '].')
                assign('Server', serverName, 'Machine', machineName)
        except Exception, error:
		raise ScriptError, 'Unable to assign server [' + str(serverName) + '] to machine [' + str(machineName) + ']: ' + str(error)
		
    if serverInstance is None:
        cd('/')
        serverInstance = create(str(serverName), 'Server')
        targetCluster=configProperties.getProperty('wls.server.' + str(server) + '.cluster')
        targetClusterName=configProperties.getProperty('wls.cluster.' + str(targetCluster) + '.name')
        __targetServerToCluster(server, serverName, online, targetCluster, targetClusterName)
    else:
        serverInstanceExist = 1
        log.info('Server [' + str(serverName) + '] already exists, checking REPLACE flag.')

    #=======================================================================================
    # Enable Auto restart functionality
    #=======================================================================================
    cd('/Servers/' + str(serverName))
    log.info('Setting Auto Restart [' + str(autoRestartOnFailure) + '].')
    if not autoRestartOnFailure is None and autoRestartOnFailure.upper()=='FALSE':
        set('AutoRestart', 'False')
    else:
        set('AutoRestart', 'True')
      
    if not serverInstanceExist or isReplaceRequired(configProperties.getProperty('REPLACE')) or (not replaceName is None and not serverName is None):
    	 
        if serverInstanceExist and isReplaceRequired(configProperties.getProperty('REPLACE')):
            log.info('REPLACE flag is specified, start replacing Server [' + str(serverName) + '] properties.')
 	
        if not replaceName is None:
            log.info('Changing ' + serverInstance.getName() + ' to ' + replaceName + '.')
            serverInstance.setName(replaceName)
            serverName = replaceName
        
        if configProperties.getProperty('wls.admin.name') != serverName:
            cd('/')
            targetCluster=configProperties.getProperty('wls.server.' + str(server) + '.cluster')
            targetClusterName=configProperties.getProperty('wls.cluster.' + str(targetCluster) + '.name')
            __targetServerToCluster(server, serverName, online, targetCluster, targetClusterName)
        
        log.info('Setting listen port [' + str(listenPort) + '].')
        if listenPort is '' or listenPort is None:
        	log.error('ListenerPort is being attempted to set to None for server \' '+str(server)+' \'. Please make sure that the proerty \'wls.server.' + str(server) + '.listener.port\' is existing and valid.' )
        	sys.exit()
        serverInstance.setListenPort(int(listenPort))
        log.info('Setting listen address [' + str(listenAddress) + '].')
        serverInstance.setListenAddress(listenAddress)

        log.info('Setting SSL enable [' + str(enableSSL) + '].')
        if not enableSSL is None and enableSSL.upper()=='TRUE':
            if online:
                ssl = serverInstance.getSSL()
            else:
                cd('/Servers/' + str(serverName))
                ssl = create(str(serverName),'SSL')
                
            ssl.setEnabled(1)
            log.info('Setting SSL port [' + str(sslPort) + '].')
            ssl.setListenPort(int(sslPort))
        else:
            if not enableSSL is None and enableSSL.upper()=='FALSE':
                if online:
                    ssl = serverInstance.getSSL()
                else:
                    cd('/Servers/' + str(serverName))
                    ssl = create(str(serverName),'SSL')
                    
                ssl.setEnabled(0)

        
        #=======================================================================================
        # Configure tunneling.
        #=======================================================================================
        cd('/Servers/' + str(serverName))
        log.info('Setting Tunneling Enabled [' + str(enableTunneling) + '].')
        if not enableTunneling is None and enableTunneling.upper()=='TRUE':
            set('TunnelingEnabled', 'True')
        else:
            set('TunnelingEnabled', 'False')
            
        #=======================================================================================
        # Configure logging properties.
        #=======================================================================================
        try:
            customLog=configProperties.getProperty('wls.server.' + str(server) + '.log.custom')
            logFileName=configProperties.getProperty('wls.server.' + str(server) + '.log.filename')
            limitNumOfFile=configProperties.getProperty('wls.server.' + str(server) + '.log.limitNumOfFile')
            fileToRetain=configProperties.getProperty('wls.server.' + str(server) + '.log.fileToRetain')
            rotateOnStartup=configProperties.getProperty('wls.server.' + str(server) + '.log.rotateLogOnStartup')
            logFileSeverity=configProperties.getProperty('wls.server.' + str(server) + '.log.logFileSeverity')
            broadcastSeverity=configProperties.getProperty('wls.server.' + str(server) + '.log.broadcastSeverity')
            memoryBufferSeverity=configProperties.getProperty('wls.server.' + str(server) + '.log.memoryBufferSeverity')
            rotationType=configProperties.getProperty('wls.server.' + str(server) + '.log.rotationType')
            fileMinSize=configProperties.getProperty('wls.server.' + str(server) + '.log.fileMinSize')
            rotationTime=configProperties.getProperty('wls.server.' + str(server) + '.log.rotationTime')
            fileTimeSpan=configProperties.getProperty('wls.server.' + str(server) + '.log.fileTimeSpan')
            rotationDir=configProperties.getProperty('wls.server.' + str(server) + '.log.rotationDir')
    
            if not customLog is None and customLog.upper()=='TRUE':
                cd('/')
                if online:
                    logObj = serverInstance.getLog()
                else:
                    cd('/Servers/' + str(serverName))
                    logObj = create(serverName, 'Log')                
                
                log.info('Setting log filename [' + str(logFileName) + '].')
                logObj.setFileName(logFileName)
                
                log.info('Setting limit number of file [' + str(limitNumOfFile) + '].')
                if not limitNumOfFile is None and limitNumOfFile.upper()=='TRUE':
                    logObj.setNumberOfFilesLimited(true)
                    log.info('Setting number of file [' + str(fileToRetain) + '].')
                    logObj.setFileCount(int(fileToRetain))
                    
                log.info('Setting rotation on startup [' + str(rotateOnStartup) + '].')
                if not rotateOnStartup is None and rotateOnStartup.upper()=='TRUE':
                    logObj.setRotateLogOnStartup(1)
                else:
                    logObj.setRotateLogOnStartup(0)
                
                log.info('Setting log file severity [' + str(logFileSeverity) + '].')
                logObj.setLogFileSeverity(logFileSeverity)
                log.info('Setting domain log broadcast severity [' + str(broadcastSeverity) + '].')
                logObj.setDomainLogBroadcastSeverity(broadcastSeverity)
                log.info('Setting memory buffer severity [' + str(memoryBufferSeverity) + '].')
                logObj.setMemoryBufferSeverity(memoryBufferSeverity)
                log.info('Setting log rotation type [' + str(rotationType) + '].')
                logObj.setRotationType(rotationType)
                if rotationType.upper()=='BYTIME':
                    logObj.setRotationTime(rotationTime)
                    logObj.setFileTimeSpan(int(fileTimeSpan))
                else:
                    if rotationType.upper()=='BYSIZE':
                        logObj.setFileMinSize(int(fileMinSize))
                        
                log.info('Setting log rotation directory [' + str(rotationDir) + '].')
                logObj.setLogFileRotationDir(rotationDir)
        except Exception, error:
            raise ScriptError, 'Unable to configure logging properties on managed server  [' + str(serverName) + '] : ' + str(error)
    
        try:
            if online:
                webserver = serverInstance.getWebServer()
                httplog = webserver.getWebServerLog()
            else:
                webserver = create(str(serverName), 'WebServer')
                cd('WebServer/' + str(serverName))
                httplog = create(str(serverName), 'WebServerLog')            
                
            httpLogEnable=configProperties.getProperty('wls.server.' + str(server) + '.httplog.enable')
            log.info('Setting http log enable [' + str(httpLogEnable) + '].')
            if not httpLogEnable is None and httpLogEnable.upper()=='TRUE':
                httplog.setLoggingEnabled(1)
                
                httpLogFileName=configProperties.getProperty('wls.server.' + str(server) + '.httplog.filename')
                httpLimitNumOfFile=configProperties.getProperty('wls.server.' + str(server) + '.httplog.limitNumOfFile')
                httpFileToRetain=configProperties.getProperty('wls.server.' + str(server) + '.httplog.fileToRetain')
                httpRotateOnStartup=configProperties.getProperty('wls.server.' + str(server) + '.httplog.rotateLogOnStartup')
                httpRotationType=configProperties.getProperty('wls.server.' + str(server) + '.httplog.rotationType')
                httpFileMinSize=configProperties.getProperty('wls.server.' + str(server) + '.httplog.fileMinSize')
                httpRotationTime=configProperties.getProperty('wls.server.' + str(server) + '.httplog.rotationTime')
                httpFileTimeSpan=configProperties.getProperty('wls.server.' + str(server) + '.httplog.fileTimeSpan')
                httpRotationDir=configProperties.getProperty('wls.server.' + str(server) + '.httplog.rotationDir')
                httpFormat=configProperties.getProperty('wls.server.' + str(server) + '.httplog.format')
                
                log.info('Setting http log filename [' + str(httpLogFileName) + '].')
                httplog.setFileName(httpLogFileName)
                log.info('Setting http limit number of file [' + str(httpLimitNumOfFile) + '].')
                if not httpLimitNumOfFile is None and httpLimitNumOfFile.upper()=='TRUE':
                    httplog.setNumberOfFilesLimited(true)
                    log.info('Setting http number of file [' + str(httpFileToRetain) + '].')
                    httplog.setFileCount(int(httpFileToRetain))
                else:
                    httplog.setNumberOfFilesLimited(false)
                log.info('Setting http log rotate on startup [' + str(httpRotateOnStartup) + '].')
                if not httpRotateOnStartup is None and httpRotateOnStartup.upper()=='TRUE':        
                    httplog.setRotateLogOnStartup(1)
                else:
                    httplog.setRotateLogOnStartup(0)
                    
                log.info('Setting http log format [' + str(httpFormat) + '].')
                httplog.setELFFields(httpFormat)
                log.info('Setting http log rotation type [' + str(httpRotationType) + '].')
                httplog.setRotationType(httpRotationType)
                if httpRotationType.upper()=='BYTIME':
                    httplog.setRotationTime(httpRotationTime)
                    log.info('Setting http log time span [' + str(httpFileTimeSpan) + '].')
                    httplog.setFileTimeSpan(int(httpFileTimeSpan))
                else:
                    if httpRotationType.upper()=='BYSIZE':
                        log.info('Setting http log min size [' + str(httpFileMinSize) + '].')
                        httplog.setFileMinSize(int(httpFileMinSize))
                        
                log.info('Setting http log rotation directory [' + str(httpRotationDir) + '].')
                httplog.setLogFileRotationDir(httpRotationDir)
            else:
                if not httpLogEnable is None and httpLogEnable.upper()=='FALSE':
                    httplog.setLoggingEnabled(0)
        except Exception, error:
            raise ScriptError, 'Unable to configure http logging properties on managed server  [' + str(serverName) + '] : ' + str(error)
        
        domainPath=configProperties.getProperty('wls.domain.dir')
        domainName=configProperties.getProperty('wls.domain.name')
        domainUsername=configProperties.getProperty('wls.admin.username')
        domainPassword=configProperties.getProperty('wls.admin.password')
    	rootDir=configProperties.getProperty('wls.server.' + str(server) + '.root.dir')
        
        securityDir = File(domainPath + File.separator + domainName + File.separator + 'servers' + File.separator + str(serverName) + File.separator + 'security')
        if not securityDir.exists() and rootDir is None:
            log.info('Creating directory ' + str(securityDir))
            securityDir.mkdirs()
        
        bootFile = File(securityDir.getAbsolutePath()  + File.separator + 'boot.properties')
        
        # TODO: Use flag no.managed.server.boot.properties=true/false instead of checking domain called osb_domain (H@CK)
        if not bootFile.exists() and rootDir is None and not domainName == 'osb_domain':
            log.info('Creating boot.properties for server [' + str(serverName) + '].')
            bootFile.createNewFile()
            fileWriter = FileWriter(bootFile)    
            bufWriter = BufferedWriter(fileWriter)
            bufWriter.write('username=' + str(domainUsername))
            bufWriter.newLine()
            bufWriter.write('password=' + str(domainPassword))
            bufWriter.close()
        else:
            log.info('Ignoring boot.properties creation for [' + str(serverName) + '].')
            
	#=======================================================================================
	# Configure additional managed server properties
	#=======================================================================================
        __configureAdditionalManagedServerProperties(serverName, enableHostnameVerification)
        __configureCoherenceManagedServerProperties(serverName,coherenceUnicastAddress,wlsVersion)
        servergroups=configProperties.getProperty('wls.server.'+str(server)+'.servergroups')
        if servergroups is not None:
            servergroupslist=servergroups.split(',')
            if servergroupslist is not None and len(servergroupslist)>0:
                __configureServerGroups(serverName,servergroupslist,wlsVersion)
        
        #=======================================================================================
        # Assign managed server to machine.
        #=======================================================================================
        if not machine is None and len(machine)>0:
            machineName=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.name')
            machineReplaceName=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.replace.name')
            if not machineReplaceName is None:
            	machineName=machineReplaceName
            try:
                cd('/')
                if online:
                    machineInstance = lookup(machineName, 'Machine')
                    log.info('Setting machine [' + str(machineName) + '] to server [' + str(serverName) + '].')
                    serverInstance.setMachine(machineInstance)
                else:
                    log.info('Assigning machine [' + str(machineName) + '] to server [' + str(serverName) + '].')
                    assign('Server', serverName, 'Machine', machineName)
            except Exception, error:
                raise ScriptError, 'Unable to assign server [' + str(serverName) + '] to machine [' + str(machineName) + ']: ' + str(error)
        	
        #=======================================================================================
        # Configure channel.
        #=======================================================================================
 
        srvName=configProperties.getProperty('wls.server.' + str(server) + '.name')
        channelName=configProperties.getProperty('wls.server.' + str(server) + '.channel.name')
        channelProtocol=configProperties.getProperty('wls.server.' + str(server) + '.channel.protocol')
        channelListenerAddr=configProperties.getProperty('wls.server.' + str(server) + '.channel.listener.address')
        channelListenerPort=configProperties.getProperty('wls.server.' + str(server) + '.channel.listener.port')
        channelPublicListenerAddr=configProperties.getProperty('wls.server.' + str(server) + '.channel.listener.publicAddress')
        channelPublicListenerPort=configProperties.getProperty('wls.server.' + str(server) + '.channel.listener.publicPort')
        httpEnable=configProperties.getProperty('wls.server.' + str(server) + '.channel.httpEnable')
        
        if not channelName is None and len(channelName)>0:
            __configureChannel(srvName, channelName, online, channelProtocol, channelListenerAddr, channelListenerPort, channelPublicListenerAddr, channelPublicListenerPort, httpEnable)

def __configureCoherenceManagedServerProperties(serverName,coherenceUnicastAddress,wlsVersion ):
    
    if wlsVersion == '12':
        log.debug("Weblogic 12c....Setting up Unicast Listen address for Coherence server")
        try:
            cd('/')
            cd('Server/'+str(serverName))
            create('member_config', 'CoherenceMemberConfig')
            cd('CoherenceMemberConfig/member_config')
            if coherenceUnicastAddress is not None and str(coherenceUnicastAddress)=="localhost":
                coherencelistenAddress="127.0.0.1"
            else:
                coherencelistenAddress=str(coherenceUnicastAddress)
            log.debug("Setting Coherence Unicast listen aaddress to"+coherencelistenAddress)
            set('UnicastListenAddress', coherencelistenAddress)
        except Exception, error:
            log.info("Coherence Property set up failed, Managed server may fail to start up with out this configuration")
            
def __configureAdditionalManagedServerProperties(serverName, enableHostnameVerification):
    #=======================================================================================
    # Configure additional managed server properties
    #=======================================================================================
    if not enableHostnameVerification is None:
        try:
            cd('/Servers/' + str(serverName))
            ssl = create('SSL','SSL')
            log.info('Setting Hostname Verification [' + str(enableHostnameVerification) + '].')
            if enableHostnameVerification.upper()=='TRUE':
                ssl.setHostnameVerificationIgnored(0)
            else:
                ssl.setHostnameVerificationIgnored(1)

        except Exception, error:
            cd('/Servers/' + str(serverName))
            ssl = create('SSL','SSL')
            log.info('Setting Hostname Verification [' + str(enableHostnameVerification) + '].')
            if enableHostnameVerification.upper()=='TRUE':
                ssl.setHostnameVerificationIgnored(0)
            else:
                ssl.setHostnameVerificationIgnored(1)
            
def __configureServerGroups(serverName,servergroupslist,wlsVersion):
    if wlsversion == '12':
        if not servergroupslist is None:
            log.debug(servergroupslist)
            try:
                log.debug("setting server groups for "+serverName)
                setServerGroups(serverName, servergroupslist)
            except Exception, error:
                log.info("setting server groups failed for "+serverName)
            

def __targetServerToCluster(server, serverName, online, targetCluster, targetClusterName):
        if not targetCluster is None and len(targetCluster)>0:
            log.info('Assigning Managed Server [' + str(serverName) + '] to Cluster [' + str(targetClusterName) + ']')
            try:
                cd('/')
                if online:
                    clusterInstance = lookup(targetClusterName, 'Cluster')
                    serverInstance.setCluster(clusterInstance)
                else:
                    cd('/Servers/' + str(serverName))
                    assign('Server', str(serverName), 'Cluster', str(targetClusterName))
                log.info('Managed Server [' + str(serverName) + '] has been assigned to Cluster [' + str(targetClusterName) + '] successfully.')
            except Exception, error:
                
                raise ScriptError, 'Unable to assign server [' + str(serverName) + '] to cluster [' + str(targetClusterName) + ']: ' + str(error)
        else:
            log.info('################################################################################')
            log.info('# WARNING: Managed Sever [' + str(serverName) + '] is not targeted to any cluster.')
            log.info('################################################################################')

#=======================================================================================
# Create machines
#=======================================================================================
    
def __createMachines(online, configProperties):
    
    domainMachines=configProperties.getProperty('wls.domain.machines')
    if not domainMachines is None and len(domainMachines)>0:
        machineList = domainMachines.split(',')
        for machine in machineList:
            __createMachine(machine, online, configProperties)
        
#=======================================================================================
# Create a machine
#=======================================================================================
    
def __createMachine(machine, online, configProperties):

    machineName=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.name')
    machineReplaceName=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.replace.name')
    command_name=configProperties.getProperty('create_domain')
    #log.info(command_name)
    machineType=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.type')
    machineBindGID=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.postBindGID')
    machineBindGIDEnable=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.postBindGIDEnabled')
    machineBindUID=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.postBindUID')
    machineBindUIDEnable=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.postBindUIDEnabled')

    nodeType=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.type')
    nodeAddress=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.address')
    nodePort=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.port')
    nodeHome=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.nodeManagerHome')
    nodeShellCmd=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.shellCommand')
    nodeDebugEnable=configProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.debugEnabled')
    #log.debug('inside __createMachine')
    
    try:
        if not machineName is None:
            machine = None
            machineExist = 0
            try:
                #log.debug('in try')
                cd('/')
                if online:
                    log.debug('in online')
                    cd('Machines')
                    machine = lookup(str(machineName), 'Machine')
                else:
                    try:
                        log.debug('in offline')
                        #Disabling mbean checks in offline mode for Oracle FMW 12.2 support
                        
                        #cd('Machines')
                        #cd(str(machineName))
                        #machine = cmo
                                            
                    except Exception, error:
                        log.info('Unable to lookup machine [' + str(machineName) + ']. The machine will be created in offline mode' )
                        pass
            except WLSTException, error:
                log.info('Unable to lookup machine [' + str(machineName) + ']. The machine will be created.')

            if machine is None:  
                if online:
                    cd('/')
                    if machineType.upper()=='UNIX':
                        machine = cmo.createUnixMachine(str(machineName))
                    else:
                        machine = create(str(machineName),'Machine')
                        
                else:
                    cd('/')
                    if machineType.upper()=='UNIX':
                        machine = create(str(machineName), 'UnixMachine')
                    else:
                        machine = create(str(machineName),'Machine')
                        log.debug('machine created  ------------'+str(machineName))
            else:
            	if not machineReplaceName is None and machineType.upper()=='UNIX':
            	    cd('/')
            	    delete(str(machineName),'Machine')
            	    machine = create(str(machineReplaceName), 'UnixMachine')
            	    oldMachineName = machineName
		    machineName = machineReplaceName
		    log.info('Removed ' + oldMachineName + ' to be replaced with ' + machineName)
                else:
                    machineExist = 1
                    log.info('Machine [' + str(machineName) + '] already exists, checking REPLACE flag.')
            
            if not machineExist or isReplaceRequired(configProperties.getProperty('REPLACE')) or not machineReplaceName is None:
                if machineExist and isReplaceRequired(configProperties.getProperty('REPLACE')):
                  log.info('REPLACE flag is specified, start replacing machine [' + str(machineName) + '] properties.' )
		if not machineReplaceName is None and not machineType.upper()=='UNIX':
		  log.info('Changing ' + machineName + ' to ' + machineReplaceName + '.')
		  oldMachineName = machineName
		  machineName = machineReplaceName
		  machine.setName(machineName)
                if machineType.upper()=='UNIX':
                    log.info('Setting Post Bind GID Enabled [' + str(machineBindGIDEnable) + '].')
                    if not machineBindGIDEnable is None and machineBindGIDEnable.upper()=='TRUE':
                        machine.setPostBindGIDEnabled(1)
                        log.info('Setting Post Bind GID [' + str(machineBindGID) + '].')
                        machine.setPostBindGID(machineBindGID)
                    else:
                        machine.setPostBindGIDEnabled(0)
    
                    log.info('Setting Post Bind UID Enabled [' + str(machineBindUIDEnable) + '].')
                    if not machineBindUIDEnable is None and machineBindUIDEnable.upper()=='TRUE':
                        machine.setPostBindUIDEnabled(1)
                        log.info('Setting Post Bind UID [' + str(machineBindUID) + '].')
                        machine.setPostBindUID(machineBindUID)
                    else:
                        machine.setPostBindGIDEnabled(0)
                    
                if not nodeType is None and len(nodeType)>0:
                    if online:
                        nodeManager = machine.getNodeManager()
                    else:
                        try:
                            cd('/Machines/' + str(machineName))
                        
                        except Exception, error:
                            try:
                                cd('AnyMachine/' + str(machineName))
                            except:
                                pass
                           
                        try:
                            log.debug("machine name " + str(machineName))
                            cd('/Machines/' + str(machineName))
                            nodeManager = create('NodeManager','NodeManager')
                            #nodeManager = cmo
                            
                        
                        except Exception, error:
                            log.info('Node manager does not exist, creating new one.')
                            try:
                                cd('/Machines/' + str(machineName))
                                nodeManager = create('NodeManager','NodeManager')
                            except Exception, error:
                                raise ScriptError, 'Unable to create node manager :' + str(error)

                    log.info('Setting node manager type [' + str(nodeType) + '].')
                    nodeManager.setNMType(nodeType)
                    log.info('Setting node manager address [' + str(nodeAddress) + '].')
                    nodeManager.setListenAddress(nodeAddress)
                    log.info('Setting node manager port [' + str(nodePort) + '].')
                    nodeManager.setListenPort(int(nodePort))
                    if not nodeHome is None and len(nodeHome)>0:
                        log.info('Setting node manager home [' + str(nodeHome) + '].')
                        nodeManager.setNodeManagerHome(nodeHome)
                    if not nodeShellCmd is None and len(nodeShellCmd)>0:
                        log.info('Setting node manager shell command [' + str(nodeShellCmd) + '].')
                        nodeManager.setShellCommand(nodeShellCmd)
                    log.info('Setting node manager debug [' + str(nodeDebugEnable) + '].')
                    if not nodeDebugEnable is None and nodeDebugEnable.upper()=='TRUE':
                        nodeManager.setDebugEnabled(1)
                    else:
                        if not nodeDebugEnable is None and nodeDebugEnable.upper()=='FALSE':
                            nodeManager.setDebugEnabled(0)
                        else:
                            log.info('Debug Enable is not specified, skipping.')
            
        else:
            log.info('Could not create machine [' + str(machineName) + '].')
    except Exception, error:
        raise ScriptError, 'Unable to create machine [' + str(machineName) + ']: ' + str(error)
    
#=======================================================================================
# Configure channel
#=======================================================================================
def __configureChannel(serverName, channelName, online, channelProtocol, channelHost, channelPort, channelPublicAddress, channelPublicPort, httpEnable):
    
    try:
        cd('/Servers/' + str(serverName))
    except WLSTException, error:
        raise ScriptError, 'Unable to find server [' + str(serverName) + '], please check ' + getDomainFileName() + ' and try again.'

    channel = None
    channelExist = 0
    try:
        if online:
            cd('/Servers/' + str(serverName))
            channel = lookup(channelName, 'NetworkAccessPoint')
        else:
            try:
                cd('/Servers/' + str(serverName) + '/NetworkAccessPoint/' + str(channelName))
            except Exception, error:
                log.info('Unable to find channel [' + str(channelName) + '], trying to create new one.')
    except WLSTException, error:
        log.info('Unable to find channel [' + str(channelName) + '], trying to create new one.')
    
    if channel is None:
        cd('/Servers/' + str(serverName))
        log.info('Creating channel [' + str(channelName) + '].')
        channel = create(channelName, 'NetworkAccessPoint')
    else:
        channelExist = 1
        log.info('Channel [' + str(channelName) + '] already exists, checking REPLACE flag.')

    if not channelExist or isReplaceRequired(configProperties.getProperty('REPLACE')):
        if channelExist and isReplaceRequired(configProperties.getProperty('REPLACE')):
          log.info('REPLACE flag is specified, start replacing Channel [' + str(channelName) + '] properties.' )
        log.info('Setting listen address [' + str(channelHost) + '].')
        channel.setListenAddress(channelHost)
        log.info('Setting listen port [' + str(channelPort) + '].')
        channel.setListenPort(int(channelPort))
        log.info('Setting protocol [' + str(channelProtocol) + '].')
        channel.setProtocol(channelProtocol)
        log.info('Setting http enable [' + str(httpEnable) + '].')
        if httpEnable.upper()=='TRUE':
            channel.setHttpEnabledForThisProtocol(1)
        log.info('Setting public address [' + str(channelPublicAddress) + '].')
        channel.setPublicAddress(channelPublicAddress)
        log.info('Setting public port [' + str(channelPublicPort) + '].')
        channel.setPublicPort(int(channelPublicPort))

#=======================================================================================
# Create clusters.
#=======================================================================================
def __createClusters(online, configProperties):

    clusters=configProperties.getProperty('wls.clusters')
    if not clusters is None and len(clusters) > 0:
        clusterList = clusters.split(',')
        for cluster in clusterList:
            __createCluster(cluster, online, configProperties)
            
#=======================================================================================
# Create a cluster in domain.
#=======================================================================================
    
def __createCluster(cluster, online, configProperties):
    
    clusterName=configProperties.getProperty('wls.cluster.' + str(cluster) + '.name')
    clusterAddress=configProperties.getProperty('wls.cluster.' + str(cluster) + '.address')
    multicastAddress=configProperties.getProperty('wls.cluster.' + str(cluster) + '.multicast.address')
    multicastPort=configProperties.getProperty('wls.cluster.' + str(cluster) + '.multicast.port')
    algorithm=configProperties.getProperty('wls.cluster.' + str(cluster) + '.defaultLoadAlgorithm')
    
    cd('/')
    clusterExist = 0
    try:
        cluster = None
        if online:
            cluster = lookup(str(clusterName), 'Cluster')
        else:
            try:
                #Disabling mbean checks in offline mode for Oracle FMW 12.2 support
                #cd('/Clusters')
                #cd(str(clusterName))
                log.debug('Unable to lookup cluster [' + str(clusterName) + ']. The cluster will be created.')
            except Exception, error:
                log.info('Unable to lookup cluster [' + str(clusterName) + ']. The cluster will be created.')
    except WLSTException, error:
        log.info('Unable to lookup cluster [' + str(clusterName) + ']. The cluster will be created.')
        
    if cluster is None:
        cd('/')
        log.info('Creating cluster [' + str(clusterName) + '].')
        cluster = create(str(clusterName), 'Cluster')
        log.info('Cluster [' + str(clusterName) + '] has been created.')
        
    else:
        clusterExist = 1
        log.info('Cluster [' + str(clusterName) + '] already exists.')

    if not clusterExist or isReplaceRequired(configProperties.getProperty('REPLACE')):
        if clusterExist and isReplaceRequired(configProperties.getProperty('REPLACE')):
          log.info('REPLACE flag is specified, start replacing cluster [' + str(clusterName) + '] properties.')
        if not clusterAddress is None:
          log.info('Setting cluster address [' + str(clusterAddress) + '].' )
          cluster.setClusterAddress(clusterAddress)
        if not multicastAddress is None:
          log.info('Setting multicast address [' + str(multicastAddress) + '].')
          cluster.setMulticastAddress(multicastAddress)
        if not multicastPort is None:
          log.info('Setting multicast port [' + str(multicastPort) + '].')
          cluster.setMulticastPort(int(multicastPort))
        if not algorithm is None:
          log.info('Setting default load algorithm [' + str(algorithm) + '].')
          cluster.setDefaultLoadAlgorithm(algorithm)

#=======================================================================================
# Assign servers to cluster.
#=======================================================================================

def __assignServersToCluster(configProperties):
    #=======================================================================================
    # Assign managed server to cluster.
    #=======================================================================================
    servers=configProperties.getProperty('wls.servers')
    if not servers is None and len(servers) > 0:
        serverList = servers.split(',')
        for server in serverList:
            serverName=configProperties.getProperty('wls.server.' + str(server) + '.name')
            targetCluster=configProperties.getProperty('wls.server.' + str(server) + '.cluster')
            targetClusterName=configProperties.getProperty('wls.cluster.' + str(targetCluster) + '.name')
            cd('/')
            serverInstance = lookup(serverName, 'Server')
            clusterInstance = serverInstance.getCluster()
            if not clusterInstance is None:
                log.info('Server [' + str(serverName) + '] already exists in cluster [' + str(targetClusterName) + '], skipping.')
            else:
                clusterInstance = lookup(targetClusterName, 'Cluster')
                try:
                    serverInstance.setCluster(clusterInstance)
                except Exception, error:
                    raise ScriptError, 'Unable to assign server [' + str(serverName) + '] to cluster [' + str(targetClusterName) + ']: ' + str(error)

