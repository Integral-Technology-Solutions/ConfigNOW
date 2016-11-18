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
## jms.py
##
## This script contains functions that manipulate JMS resources.


#=======================================================================================
# Load required modules
#=======================================================================================

try:
	commonModule
except NameError:
	execfile('wlst/common.py')
try:
	jndiModule
except NameError:
    execfile('wlst/jndi.py')


#=======================================================================================
# Global variables
#=======================================================================================

jmsModule = '1.2.0'

try:
	currentJMSModule
except NameError:
	currentJMSModule = None

log.debug('Loading module [jms.py] version [' + jmsModule + ']')


#=======================================================================================
# Return the current JMS module
#=======================================================================================

def getCurrentJMSModule():
	"""Returns the current JMS module"""

	global currentJMSModule
	
	return currentJMSModule
	
	# done returning current JMS module

#=======================================================================================
# Create the JMS Servers. 
#=======================================================================================

def createJMSServers(resourceProperties, domainProperties):
	jmsServers=resourceProperties.getProperty('jmsServers')
	if jmsServers is None or len(jmsServers)==0:
		log.info('JMS Server is not specified, skipping.')
	else:
		jmsServerList = jmsServers.split(',')
		for jmsServer in jmsServerList:			
			__createJMSServer(jmsServer, resourceProperties, domainProperties)

#=======================================================================================
# Create the JMS Server. 
#=======================================================================================

def __createJMSServer(jmsServer, resourceProperties, domainProperties):
	"""Creates a JMS Server"""

	jmsServerPrefix = 'jmsServer.' + str(jmsServer) + '.'

	# load jms properties		
	jmsServerName=resourceProperties.getProperty(jmsServerPrefix + 'Name')
	tmpTarget=resourceProperties.getProperty(jmsServerPrefix + 'Target')
	persistentStore=resourceProperties.getProperty(jmsServerPrefix + 'PersistentStore')
	persistentStoreType=resourceProperties.getProperty(jmsServerPrefix + 'PersistentStoreType')	
	jmsServerTarget=domainProperties.getProperty('wls.server.' + str(tmpTarget) + '.name')
	messageBufferSize=resourceProperties.getProperty(jmsServerPrefix + 'MessageBufferSize')
	pagingDir=resourceProperties.getProperty(jmsServerPrefix + 'PagingDirectory')
	bytesMaximum=resourceProperties.getProperty(jmsServerPrefix + 'BytesMaximum')
	messagesMaximum=resourceProperties.getProperty(jmsServerPrefix + 'MessagesMaximum')
	
	if jmsServerTarget is None or len(jmsServerTarget)==0:
		log.info('Unable to look up server target available in domain property file, server [' + str(jmsServerTarget) + '] not found.' )
		log.info('Assign JMS Server Target to default admin server.')
		jmsServerTarget=domainProperties.getProperty('wls.admin.name')

	jmsServer = None
	
	try:
		jmsServer = lookup(jmsServerName, 'JMSServer')
	except WLSTException, error:
		"""Could not lookup JMS sever"""

	if jmsServer is None:
		if not jmsServerName is None:
			# Create JMS server
			log.info('Creating JMS Server [' + str(jmsServerName) + ']')
			try:
				cd('/')
				jmsServer = create(jmsServerName, 'JMSServer')
			except Exception, error:
				cancelEdit('y')
				raise ScriptError, 'Unable to create JMS server [' + str(jmsServerName) + ']: ' + str(error)	
			
			try:
				if messageBufferSize is not None and len(messageBufferSize) > 0:
					log.info('Setting message buffer size for JMS server "' + jmsServerName + '" to ' + messageBufferSize)
					jmsServer.setMessageBufferSize(long(messageBufferSize))
				if pagingDir is not None and len(pagingDir) > 0:
					log.info('Setting paging dir for JMS server "' + jmsServerName + '" to "' + pagingDir + '"')
					jmsServer.setPagingDirectory(pagingDir)
				if messageBufferSize is not None and len(messageBufferSize) > 0:
					log.info('Setting message buffer size for JMS server "' + jmsServerName + '" to ' + messageBufferSize)
					jmsServer.setMessageBufferSize(long(messageBufferSize))
				if bytesMaximum is not None and len(bytesMaximum) > 0:
					log.info('Setting maximum bytes for JMS server "' + jmsServerName + '" to retain in memory to ' + bytesMaximum)
					jmsServer.setBytesMaximum(long(bytesMaximum))
				if messagesMaximum is not None and len(messagesMaximum) > 0:
					log.info('Setting maximum # of messages for JMS server "' + jmsServerName + '" to retain in memory to ' + messagesMaximum)
					jmsServer.setMessagesMaximum(long(messagesMaximum))

				# Set persistent store & targeting
				if not persistentStoreType is None and persistentStoreType.upper()=='FILE':
					persistentStoreName=resourceProperties.getProperty('persistent.filestore.' + str(persistentStore) + '.Name')
					cd('/')
					persistentStoreBean=lookup(persistentStoreName, 'FileStore')
					if persistentStoreBean is None:
						log.info('Unable to lookup filestore [' + str(persistentStoreName) + '], skipping.')
					else:
						jmsServer.setPersistentStore(persistentStoreBean)
					
					migratable=resourceProperties.getProperty('persistent.filestore.' + str(persistentStore) + '.Migratable')
					if not migratable is None and migratable.upper()=='TRUE':
						jmsServerTarget = jmsServerTarget + ' (migratable)'
						jmsServer.addTarget(lookup(jmsServerTarget, 'MigratableTarget'))
					else: 
						log.info('Setting target [ ' + str(jmsServerTarget) + ' ].')
						jmsServer.addTarget(lookup(jmsServerTarget, 'Server'))
				else:
					log.info('Setting target [ ' + str(jmsServerTarget) + ' ].')
					jmsServer.addTarget(lookup(jmsServerTarget, 'Server'))
			except Exception, error:
				cancelEdit('y')
				raise ScriptError, 'Unable to set persistent store [' + str(persistentStoreName) + '] to JMS Server [' + str(jmsServerName) + ']: ' + str(error)
		else:
			log.info('JMS Server is not specified, skipping ')
	else:
		log.info('JMS server [' + str(jmsServerName) + '] already exists, skipping')

	# done with JMS server creation
	
#=======================================================================================
# Create JMS System resources
#=======================================================================================

def createJMSModules(resourceProperties, domainProperties):
	"""Creates all specified jms modules"""
	
	jmsModules=resourceProperties.getProperty('jmsModules')
	
	if jmsModules is None:
		log.info('JMS Module is not specified, skipping ')
	else:		
		modules = jmsModules.split(',')
		for module in modules:
			try:
				__createJMSModule('jmsModule.' + module, resourceProperties, domainProperties)
			except Exception, error:
				cancelEdit('y')
				raise ScriptError, 'Unable to create JMS module 1 [' + module + ']: ' + str(error)

	# done with JMS resources creation
	

#=======================================================================================
# Create a JMS System resource. 
#=======================================================================================

def __createJMSModule(jmsModulePrefix, resourceProperties, domainProperties):
    """Creates a JMS Module"""

    # load specific properties
    jmsModuleName=resourceProperties.getProperty(jmsModulePrefix + '.Name')
    jmsModuleTargetType=resourceProperties.getProperty(jmsModulePrefix + '.TargetType')
    jmsModuleTargets=resourceProperties.getProperty(jmsModulePrefix + '.Targets')

    currentJMSModule = None	

    try:
		currentJMSModule = lookup(jmsModuleName, 'JMSSystemResource')
    except WLSTException, error:
		log.info('Unable to lookup JMS resource [' + str(jmsModuleName) + '], trying to create new one.')
	
    if currentJMSModule is None:
        try:
            log.info('Creating JMS module [' + str(jmsModuleName) + ']')
            # Create JMS Module
            cd('/')
            currentJMSModule = create(jmsModuleName, 'JMSSystemResource')
        except Exception, error:
			cancelEdit('y')
			raise ScriptError, 'Unable to create JMS module 2 [' + str(jmsModuleName) + ']: ' + str(error)

        try:
            # add the target
            if jmsModuleTargets is None or len(jmsModuleTargets)==0:
                log.info('Unable to look up server target available in domain property file, target not specified.' )
                adminServer=domainProperties.getProperty('wls.admin.name')				
                log.info('Assign JMS Module Target to default admin server (' + adminServer + ')')
                currentJMSModule.addTarget(lookup(adminServer, 'Server'))
            else:
                jmsModuleTargetList = jmsModuleTargets.split(',')
                for tmpTarget in jmsModuleTargetList:
                    if not jmsModuleTargetType is None and jmsModuleTargetType.upper()=='CLUSTER':
                        jmsModuleTarget=domainProperties.getProperty('wls.cluster.' + tmpTarget + '.name')
                        try:
                            currentJMSModule.addTarget(lookup(jmsModuleTarget, 'Cluster'))
                        except Exception, error:
                            raise ScriptError, 'Unable to lookup cluster [' + str(jmsModuleTarget) + ']: ' + str(error)
                    else:
                        jmsModuleTarget=domainProperties.getProperty('wls.server.' + tmpTarget + '.name')
                        try:
                            currentJMSModule.addTarget(lookup(jmsModuleTarget, 'Server'))
                        except Exception, error:
                            cancelEdit('y')
                            raise ScriptError, 'Unable to lookup server [' + str(jmsModuleTarget) + ']: ' + str(error)
    					
            createSubDeployments(jmsModulePrefix, resourceProperties)
        except WLSTException, error:
            cancelEdit('y')
            raise ScriptError, 'Unable to create JMS module [' + jmsModuleName + ']: ' + str(error)
    else:
        log.info('JMS module [' + jmsModuleName + '] already exists, check SubDeployment.')
        createSubDeployments(jmsModulePrefix, resourceProperties)

	# done with JMS module creation
	
#=======================================================================================
# Create JMS SubDeployments
#=======================================================================================

def createSubDeployments(jmsModulePrefix, resourceProperties):
	"""Creates a JMS Subdeployments"""	

	jmsSubDeployments=resourceProperties.getProperty(jmsModulePrefix + '.SubDeployments')
		
	if jmsSubDeployments is None or len(jmsSubDeployments)==0:
		log.info('No SubDeployments specified for module [' + jmsModule + '], skipping.')
	else:
		subDeployments = jmsSubDeployments.split(',')
		for subDeployment in subDeployments:
			try:				
				__createSubDeployment(jmsModulePrefix, subDeployment, resourceProperties)
			except Exception, error:
				cancelEdit('y')
				raise ScriptError, 'Unable to create SubDeployment [' + subDeployment + ']: ' + str(error)
					
	# done with JMS resources creation


#=======================================================================================
# Create a JMS SubDeployment
#=======================================================================================

def __createSubDeployment(jmsModulePrefix, subDeployment, resourceProperties):
    """Creates a JMS Subdeployment"""

    jmsModuleName=resourceProperties.getProperty(jmsModulePrefix + '.Name')
	
    try:
        jmsModule =  lookup(jmsModuleName,'JMSSystemResource')
    except WLSTException, error:
        raise ScriptError, 'Unable to lookup JMS resource [' + str(jmsModuleName) + '], the JMS resource is required: ' + str(error)
	
    if not jmsModule is None:
	
        subDeploymentPrefix = jmsModulePrefix + '.SubDeployment.' + subDeployment
		
        # load specific properties
        subDeploymentName=resourceProperties.getProperty(subDeploymentPrefix + '.Name')

        currentSubDeployment = None
	
        try:
            currentSubDeployment = jmsModule.lookupSubDeployment(subDeploymentName)
        except WLSTException, error:
            log.info('Unable to lookup SubDeployment [' + str(subDeploymentName) + '], trying to create new one.')
		
        if currentSubDeployment is None:
            log.info('Creating SubDeployment [' + subDeploymentName + ']')
            try:
                currentSubDeployment = jmsModule.createSubDeployment(subDeploymentName)
            except Exception, error:
                cancelEdit('y')
                raise ScriptError, 'Unable to create SubDeployment [' + str(subDeploymentName) + ']: ' + str(error)

            subDeploymentTargets=resourceProperties.getProperty(subDeploymentPrefix + '.Targets')
            subDeploymentTargetType=resourceProperties.getProperty(subDeploymentPrefix + '.TargetType')
    
            if subDeploymentTargets is None or len(subDeploymentTargets)==0:
                log.info('Unable to look up server target available in domain property file, target not specified.' )
                log.info('Assign JMS Module Target to default admin server.')
                subDeploymentTargetName=domainProperties.getProperty('wls.admin.name')
                adminServer = lookup(subDeploymentTargetName, 'Server')
                currentSubDeployment.addTarget(adminServer)
            else:
                subDeploymentTargetList = subDeploymentTargets.split(',')
                for subDeploymentTarget in subDeploymentTargetList:
                    if subDeploymentTargetType.upper()=='JMSSERVER':
                        subDeploymentTargetName=resourceProperties.getProperty('jmsServer.' + str(subDeploymentTarget) + '.Name')
                        try:
                            jmsServer = lookup(subDeploymentTargetName, 'JMSServer')
                            currentSubDeployment.addTarget(jmsServer)
                        except Exception, error:
                            cancelEdit('y')
                            raise ScriptError, 'Unable to add target [' + str(subDeploymentTargetName) + '] to JMS Server [' + str(subDeploymentName) + ']: ' + str(error)
                    else:
                        subDeploymentTargetName=domainProperties.getProperty('wls.cluster.' + str(subDeploymentTarget) + '.name')
                        try:
                            cluster = lookup(subDeploymentTargetName, 'Cluster')
                            currentSubDeployment.addTarget(cluster)
                        except Exception, error:
                            raise ScriptError, 'Unable to add target [' + str(subDeploymentTargetName) + '] to Cluster [' + str(subDeploymentName) + ']: ' + str(error)
        else:
            log.info('SubDeployment [' + str(subDeploymentName) + '] already exists, checking resources in SubDeployment.')

        log.info('Configuring resources in SubDeployment [' + str(subDeploymentName) + '].')
        # Create connection factories
        subDeploymentConnectionFactories=resourceProperties.getProperty(subDeploymentPrefix + '.ConnectionFactories')
        if subDeploymentConnectionFactories is None or len(subDeploymentConnectionFactories)==0:
            log.info('No connection factories specified in SubDeployment [' + subDeploymentName + '], skipping.')
        else:
            connectionFactories = subDeploymentConnectionFactories.split(',')
            for connectionFactory in connectionFactories:
                __createConnectionFactory(subDeploymentPrefix + '.ConnectionFactory.' + connectionFactory, subDeploymentName, jmsModuleName, resourceProperties=resourceProperties)

        # Create queues
        subDeploymentQueues = resourceProperties.getProperty(subDeploymentPrefix + '.Queues')
        if subDeploymentQueues is None or len(subDeploymentQueues)==0:
            log.info('No queues specified in SubDeplyment [' + subDeploymentName + '], skipping.')
        else:
            queues = subDeploymentQueues.split(',')
            for queue in queues:
                __createQueue(subDeploymentPrefix + '.Queue.' + queue, subDeploymentName, jmsModuleName, resourceProperties=resourceProperties)
	
        # Create topics
        subDeploymentTopics = resourceProperties.getProperty(subDeploymentPrefix + '.Topics')
        if subDeploymentTopics is None or len(subDeploymentTopics)==0:
            log.info('No topics specified in SubDeplyment [' + subDeploymentName + '], skipping.')
        else:
            topics = subDeploymentTopics.split(',')
            for topic in topics:
                __createTopic(subDeploymentPrefix + '.Topic.' + topic, subDeploymentName, jmsModuleName, resourceProperties=resourceProperties)
	
        # Create distributed queues
        subDeploymentDistQueues = resourceProperties.getProperty(subDeploymentPrefix + '.UniformDistributedQueues')
        if subDeploymentDistQueues is None or len(subDeploymentDistQueues)==0:
            log.info('No distributed queues specified in SubDeplyment [' + subDeploymentName + '], skipping.')
        else:
            distQueues = subDeploymentDistQueues.split(',')
            for distQueue in distQueues:
                __createUniformDistributedQueue(subDeploymentPrefix + '.UniformDistributedQueue.' + distQueue, subDeploymentName, jmsModuleName, resourceProperties=resourceProperties)
		
        # Create distributed topics
        subDeploymentDistTopics = resourceProperties.getProperty(subDeploymentPrefix + '.UniformDistributedTopics')
        if subDeploymentDistTopics is None or len(subDeploymentDistTopics)==0:
            log.info('No distributed topics specified in SubDeplyment [' + subDeploymentName + '], skipping.')
        else:
            distTopics = subDeploymentDistTopics.split(',')
            for distTopic in distTopics:
                __createUniformDistributedTopic(subDeploymentPrefix + '.UniformDistributedTopic.' + distTopic, subDeploymentName, jmsModuleName, resourceProperties=resourceProperties)
			
    else:
        raise ScriptError, 'Unable to lookup JMS resource [' + str(jmsModuleName) + '], the JMS resource is required.'
	# done with SubDeployment creation
	

#=======================================================================================
# Create a JMS Connection Factory
#=======================================================================================

def __createConnectionFactory(connectionFactoryPrefix, subDeploymentName, jmsModuleName, resourceProperties):
    """Creates a JMS connection factory resource"""
	
    try:
        jmsModule =  lookup(jmsModuleName,'JMSSystemResource')
    except WLSTException, error:
        raise ScriptError, 'Unable to lookup JMS resource [' + str(jmsModuleName) + '], the JMS resource is required : ' + str(error)

    # load specific properties
    connectionFactoryName=resourceProperties.getProperty(connectionFactoryPrefix + '.Name')
    connectionFactoryJNDI=resourceProperties.getProperty(connectionFactoryPrefix + '.JNDI')
    connectionFactoryTTL=resourceProperties.getProperty(connectionFactoryPrefix + '.DefaultTimeToLive')

    subDeploymentConnectionFactory = None
    subDeploymentConnectionFactoryExist = 0
    # Create JMS resources
    jmsResource = jmsModule.getJMSResource()

    try:
        subDeploymentConnectionFactory = jmsResource.lookupConnectionFactory(connectionFactoryName)
    except WLSTException, error:
        log.info('Unable to find connection factory [' + str(connectionFactoryName) + '] in existing configuration, trying to create new one.')

	
    if subDeploymentConnectionFactory is None:		
        try:
            log.info('Creating connection factory [' + str(connectionFactoryName) + '].')

            # create and configure the connection factory
            subDeploymentConnectionFactory = jmsResource.createConnectionFactory(connectionFactoryName)
            log.info('Connection factory [' + str(connectionFactoryName) + '] has been created successfully.')
        except Exception, error:
            cancelEdit('y')
            raise ScriptError, 'Unable to create connection factory [' + str(connectionFactoryName) + ']: ' + str(error)
    else:
        subDeploymentConnectionFactoryExist = 1
        log.info('Connection factory [' + str(connectionFactoryName) + '] already exists, checking REPLACE flag.')
        
    if not subDeploymentConnectionFactoryExist or isReplaceRequired(resourceProperties.getProperty('REPLACE')):
        if subDeploymentConnectionFactoryExist and isReplaceRequired(resourceProperties.getProperty('REPLACE')):
          log.info('REPLACE flag is specified, start replacing JMS Connection Factory [' + str(connectionFactoryName) + '] properties.' )
        
        log.info('Setting JNDI [' + str(connectionFactoryJNDI) + '].')
        subDeploymentConnectionFactory.setJNDIName(connectionFactoryJNDI)
        log.info('Setting SubDeployment name [' + str(subDeploymentName) + '].')
        subDeploymentConnectionFactory.setSubDeploymentName(subDeploymentName)

	# time to live configured?
	if not connectionFactoryTTL is None and len(connectionFactoryTTL) > 0:
		log.info('Setting default time to live to \'' + connectionFactoryTTL + '\' milliseconds')
		subDeploymentConnectionFactory.getDefaultDeliveryParams().setDefaultTimeToLive(long(connectionFactoryTTL))

	# done with connection factory creation


#=======================================================================================
# Create a JMS Queue
#=======================================================================================

def __createQueue(queuePrefix, subDeploymentName, jmsModuleName, resourceProperties):
    """Creates a JMS queue resource"""

    try:
        jmsModule =  lookup(jmsModuleName,'JMSSystemResource')
    except WLSTException, error:
        raise ScriptError, 'Unable to lookup JMS resource [' + str(jmsModuleName) + '], the JMS resource is required : ' + str(error)
	
    # load specific properties
    queueName=resourceProperties.getProperty(queuePrefix + '.Name')
    queueJNDI=resourceProperties.getProperty(queuePrefix + '.JNDI')
    queueErrorDestination=resourceProperties.getProperty(queuePrefix + '.ErrorDestination')
    queueRedeliveryDelay=resourceProperties.getProperty(queuePrefix + '.RedeliveryDelay')
    queueRedeliveryLimit=resourceProperties.getProperty(queuePrefix + '.RedeliveryLimit')
    queueTTL=resourceProperties.getProperty(queuePrefix + '.DefaultTimeToLive')
    queuePersistence=resourceProperties.getProperty(queuePrefix + '.DefaultDeliveryMode')
	
    subDeploymentQueue = None
    subDeploymentQueueExist = 0
    # Create JMS resources
    jmsResource = jmsModule.getJMSResource()

    try:
        subDeploymentQueue = jmsResource.lookupQueue(queueName)
    except WLSTException, error:
        log.info('Unable to find queue [' + str(queueName) + '] in existing configuration, trying to create new one.')
	
    if subDeploymentQueue is None:
        try:
            log.info('Creating queue [' + str(queueName) + '].')
		
            # create and configure the queue
            subDeploymentQueue = jmsResource.createQueue(queueName)
            log.info('Queue [' + str(queueName) + '] has been created successfully.')
        except Exception, error:
            cancelEdit('y')
            raise ScriptError, 'Unable to create queue [' + str(queueName) + ']: ' + str(error)
    else:
        subDeploymentQueueExist = 1
        log.info('Queue [' + str(queueName) + '] already exists, skipping')

    if not subDeploymentQueueExist or isReplaceRequired(resourceProperties.getProperty('REPLACE')):
        if subDeploymentQueueExist and isReplaceRequired(resourceProperties.getProperty('REPLACE')):
            log.info('REPLACE flag is specified, start replacing JMS Queue [' + str(queueName) + '] properties.' )
        
        log.info('Setting JNDI [' + str(queueJNDI) + '].')
        subDeploymentQueue.setJNDIName(queueJNDI)
        log.info('Setting SubDeployment name [' + str(subDeploymentName) + '].')
        subDeploymentQueue.setSubDeploymentName(subDeploymentName)

	# Redelivery delay set?
	if not queueRedeliveryDelay is None and len(queueRedeliveryDelay) > 0:
		log.info('Setting redelivery delay to ' + queueRedeliveryDelay + ' milliseconds')
		subDeploymentQueue.getDeliveryParamsOverrides().setRedeliveryDelay(int(queueRedeliveryDelay))

	# Redelivery limit set?
	if not queueRedeliveryLimit is None and len(queueRedeliveryLimit) > 0:
		log.info('Setting redelivery limit to ' + queueRedeliveryLimit + ' attempts')
		subDeploymentQueue.getDeliveryFailureParams().setRedeliveryLimit(int(queueRedeliveryLimit))

	# Error destination set?
	if not queueErrorDestination is None and len(queueErrorDestination) > 0:
		log.info('Setting error destination to queue "' + queueErrorDestination + '"')
		errorQueue = jmsResource.lookupQueue(queueErrorDestination)
		if errorQueue is None:
			raise ScriptError, 'Unable to find JMS error destination "' + queueErrorDestination + '" to set as error queue for queue "' + queueName + '"'
		else:
			subDeploymentQueue.getDeliveryFailureParams().setErrorDestination(errorQueue)
	# Default time to live set?
	if not queueTTL is None and len(queueTTL) > 0:
		log.info('Setting default time to live for queue to ' + queueTTL + ' seconds')
		subDeploymentQueue.getDeliveryParamsOverrides().setTimeToLive(int(queueTTL))
	
	# Persistence mode set?
	if not queuePersistence is None and len(queuePersistence) > 0:
		log.info('Setting queue delivery mode to "' + queuePersistence + '"')
		if not ((queuePersistence == 'Persistent') or (queuePersistence == 'Non-Persistent') or (queuePersistence == 'No-Delivery')):
			raise ScriptError, '"' + queuePersistence + '" is not a valid delivery mode'
		subDeploymentQueue.getDeliveryParamsOverrides().setDeliveryMode(queuePersistence)
    else:
        if not isReplaceRequired(resourceProperties.getProperty('REPLACE')):
            log.info('Skip replacing properties for [' + str(queueName) + '].')

	# done with queue creation

#=======================================================================================
# Create a JMS Uniform Distributed Queue
#=======================================================================================

def __createUniformDistributedQueue(distQueuePrefix, subDeploymentName, jmsModuleName, resourceProperties):
    """Creates a JMS uniform distributed queue resource"""

    try:
        jmsModule =  lookup(jmsModuleName,'JMSSystemResource')
    except WLSTException, error:
        raise ScriptError, 'Unable to lookup JMS resource [' + str(jmsModuleName) + '], the JMS resource is required : ' + str(error)
	
	# load specific properties
    distQueueName=resourceProperties.getProperty(distQueuePrefix + '.Name')
    distQueueJNDI=resourceProperties.getProperty(distQueuePrefix + '.JNDI')	
    distQueueLoadBalancingPolicy=resourceProperties.getProperty(distQueuePrefix + '.LoadBalancingPolicy')
    distQueueLocalJNDI=resourceProperties.getProperty(distQueuePrefix + '.LocalJNDIName')	
    distQueueFwdDelay=resourceProperties.getProperty(distQueuePrefix + '.ForwardDelay')
    distQueueMxMsgSize=resourceProperties.getProperty(distQueuePrefix + '.MaximumMessageSize')
    distQueueMsgPerfPref=resourceProperties.getProperty(distQueuePrefix + '.MessagingPerformancePreference')
    distQueueIncompWrkExpTime=resourceProperties.getProperty(distQueuePrefix + '.IncompleteWorkExpirationTime')
    distQueueUnitOfWrkPolicy=resourceProperties.getProperty(distQueuePrefix + '.UnitOfWorkHandlingPolicy')
    distQueueDefUnitOfOrder=resourceProperties.getProperty(distQueuePrefix + '.DefaultUnitOfOrder')
    distQueueUnitOfOrderRoute=resourceProperties.getProperty(distQueuePrefix + '.UnitOfOrderRouting')
    distQueueAttachSender=resourceProperties.getProperty(distQueuePrefix + '.AttachSender')
    distQueueDestinationKeys=resourceProperties.getProperty(distQueuePrefix + '.DestinationKeys')



    subDeploymentDistQueue = None
    subDeploymentDistQueueExist = 0
    # Create JMS resources
    jmsResource = jmsModule.getJMSResource()

    try:
        subDeploymentDistQueue = jmsResource.lookupUniformDistributedQueue(distQueueName)
    except WLSTException, error:
        log.info('Unable to find uniform distributed queue [' + str(distQueueName) + '] in existing configuration, trying to create new one.')
	
    if subDeploymentDistQueue is None:
        try:
            log.info('Creating uniform distributed queue [' + str(distQueueName) + '].')
		
            # create and configure the distributed queue
            subDeploymentDistQueue = jmsResource.createUniformDistributedQueue(distQueueName)
            log.info('Uniform distributed queue [' + str(distQueueName) + '] has been created successfully.')
        except Exception, error:
            cancelEdit('y')
            raise ScriptError, 'Unable to create distributed queue [' + distQueueName + ']: ' + str(error)
    else:
        subDeploymentDistQueueExist = 1
        log.info('Uniform Distributed Queue [' + str(distQueueName) + '] already exists, checking REPLACE flag.')

    if not subDeploymentDistQueueExist or isReplaceRequired(resourceProperties.getProperty('REPLACE')):
        if subDeploymentDistQueueExist and isReplaceRequired(resourceProperties.getProperty('REPLACE')):
            log.info('REPLACE flag is specified, start replacing JMS Uniform Distributed Queue [' + str(distQueueName) + '] properties.' )
        
        subDeploymentDistQueue.setJNDIName(distQueueJNDI)            
        if not distQueueLoadBalancingPolicy is None and len(distQueueLoadBalancingPolicy)>0:
            subDeploymentDistQueue.setLoadBalancingPolicy(distQueueLoadBalancingPolicy)
        if not distQueueLocalJNDI is None and len(distQueueLocalJNDI)>0:
            subDeploymentDistQueue.setLocalJNDIName(distQueueLocalJNDI)
        if not distQueueFwdDelay is None and len(distQueueFwdDelay)>0:
            subDeploymentDistQueue.setForwardDelay(int(distQueueFwdDelay))
        if not distQueueMxMsgSize is None and len(distQueueMxMsgSize)>0:
            subDeploymentDistQueue.setMaximumMessageSize(int(distQueueMxMsgSize))
        if not distQueueMsgPerfPref is None and len(distQueueMsgPerfPref)>0:    
            subDeploymentDistQueue.setMessagingPerformancePreference(int(distQueueMsgPerfPref))            
        if not distQueueIncompWrkExpTime is None and len(distQueueIncompWrkExpTime)>0:
            subDeploymentDistQueue.setIncompleteWorkExpirationTime(int(distQueueIncompWrkExpTime))            
        if not distQueueUnitOfWrkPolicy is None and len(distQueueUnitOfWrkPolicy)>0:
            subDeploymentDistQueue.setUnitOfWorkHandlingPolicy(distQueueUnitOfWrkPolicy)    
        if not distQueueDefUnitOfOrder is None and len(distQueueDefUnitOfOrder)>0:
            if distQueueDefUnitOfOrder.upper()=='TRUE':
                subDeploymentDistQueue.setDefaultUnitOfOrder(1)
            else:
                subDeploymentDistQueue.setDefaultUnitOfOrder(0)
        if not distQueueUnitOfOrderRoute is None and len(distQueueUnitOfOrderRoute)>0:                
            subDeploymentDistQueue.setUnitOfOrderRouting(distQueueUnitOfOrderRoute)
        if not distQueueAttachSender is None and len(distQueueAttachSender)>0:
            subDeploymentDistQueue.setAttachSender(distQueueAttachSender)
        if not distQueueDestinationKeys is None and len(distQueueDestinationKeys)>0:
            destinationKeyList=distQueueDestinationKeys.split(',')
            subDeploymentDistQueue.setDestinationKeys(destinationKeyList)
            
        subDeploymentDistQueue.setSubDeploymentName(subDeploymentName)
    else:
        if not isReplaceRequired(resourceProperties.getProperty('REPLACE')):
            log.info('Skip replacing properties for [' + str(distQueueName) + '].')
	# done with distributed queue creation

#=======================================================================================
# Create a JMS Topic
#=======================================================================================

def __createTopic(topicPrefix, subDeploymentName, jmsModuleName, resourceProperties):
    """Creates a JMS topic resource"""

    try:
        jmsModule =  lookup(jmsModuleName,'JMSSystemResource')
    except WLSTException, error:
        raise ScriptError, 'Unable to lookup JMS resource [' + str(jmsModuleName) + '], the JMS resource is required : ' + str(error)
	
    # load specific properties
    log.debug("Looking for topic name at '" + topicPrefix + ".Name'")
    topicName=resourceProperties.getProperty(topicPrefix + '.Name')
    topicJNDI=resourceProperties.getProperty(topicPrefix + '.JNDI')

    subDeploymentTopic = None
    subDeploymentTopicExist = 0
    # Create JMS resources
    jmsResource = jmsModule.getJMSResource()

    try:
        subDeploymentTopic = jmsResource.lookupTopic(topicName)
    except WLSTException, error:
        log.info('Unable to find topic [' + str(topicName) + '] in existing configuration, trying to create new one.')

    if subDeploymentTopic is None:
        try:
            log.info('Creating topic [' + str(topicName) + '].')

            # create and configure the topic
            subDeploymentTopic = jmsResource.createTopic(topicName)
            log.info('Topic [' + str(topicName) + '] has been created successfully.')
        except Exception, error:
            cancelEdit('y')
            raise ScriptError, 'Unable to create topic [' + str(topicName) + ']: ' + str(error)
    else:
        subDeploymentTopicExist = 1
        log.info('Topic [' + str(topicName) + '] already exists, checking REPLACE flag.')

    if not subDeploymentTopicExist or isReplaceRequired(resourceProperties.getProperty('REPLACE')):
        if subDeploymentTopicExist and isReplaceRequired(resourceProperties.getProperty('REPLACE')):
            log.info('REPLACE flag is specified, start replacing JMS Topic [' + str(topicName) + '] properties.' )
        
        log.info('Setting JNDI [' + str(topicJNDI) + '].')
        subDeploymentTopic.setJNDIName(topicJNDI)
        log.info('Setting SubDeployment name [' + str(subDeploymentName) + '].')
        subDeploymentTopic.setSubDeploymentName(subDeploymentName)

    # done with topic creation

#=======================================================================================
# Create a JMS Distributed Topic
#=======================================================================================

def __createUniformDistributedTopic(distTopicPrefix, subDeploymentName, jmsModuleName, resourceProperties):
    """Creates a JMS uniform distributed topic resource"""

    try:
        jmsModule =  lookup(jmsModuleName,'JMSSystemResource')
    except WLSTException, error:
        raise ScriptError, 'Unable to lookup JMS resource [' + str(jmsModuleName) + '], the JMS resource is required : ' + str(error)

    # load specific properties
    distTopicName=resourceProperties.getProperty(distTopicPrefix + '.Name')
    distTopicJNDI=resourceProperties.getProperty(distTopicPrefix + '.JNDI')
    distTopicLoadBalancingPolicy=resourceProperties.getProperty(distTopicPrefix + '.LoadBalancingPolicy')
    distTopicLocalJNDI=resourceProperties.getProperty(distTopicPrefix + '.LocalJNDIName')	
    distTopicMxMsgSize=resourceProperties.getProperty(distTopicPrefix + '.MaximumMessageSize')
    distTopicMsgPerfPref=resourceProperties.getProperty(distTopicPrefix + '.MessagingPerformancePreference')
    distTopicIncompWrkExpTime=resourceProperties.getProperty(distTopicPrefix + '.IncompleteWorkExpirationTime')
    distTopicUnitOfWrkPolicy=resourceProperties.getProperty(distTopicPrefix + '.UnitOfWorkHandlingPolicy')
    distTopicDefUnitOfOrder=resourceProperties.getProperty(distTopicPrefix + '.DefaultUnitOfOrder')
    distTopicUnitOfOrderRoute=resourceProperties.getProperty(distTopicPrefix + '.UnitOfOrderRouting')
    distTopicAttachSender=resourceProperties.getProperty(distTopicPrefix + '.AttachSender')
    distTopicDestinationKeys=resourceProperties.getProperty(distTopicPrefix + '.DestinationKeys')

    subDeploymentDistTopic = None
    subDeploymentDistTopicExist = 0
    # Create JMS resources
    jmsResource = jmsModule.getJMSResource()

    try:
        subDeploymentDistTopic = jmsResource.lookupUniformDistributedTopic(distTopicName)
    except WLSTException, error:
        log.info('Unable to find uniform distribute topic [' + str(distTopicName) + '] in existing configuration, trying to create new one.')

    if subDeploymentDistTopic is None:
        try:
            log.info('Creating uniform distributed topic [' + str(distTopicName) + '].')
            # create and configure the topic
            subDeploymentDistTopic = jmsResource.createUniformDistributedTopic(distTopicName)
            log.info('Uniform distributed topic [' + str(distTopicName) + '] has been created successfully.')
        except Exception, error:
            cancelEdit('y')
            raise ScriptError, 'Unable to create topic [' + str(distTopicName) + ']: ' + str(error)
    else:
        subDeploymentDistTopicExist = 1
        log.info('Uniform Distributed Topic [' + str(distTopicName) + '] already exists, checking REPLACE flag.')

    if not subDeploymentDistTopicExist or isReplaceRequired(resourceProperties.getProperty('REPLACE')):
        if subDeploymentDistTopicExist and isReplaceRequired(resourceProperties.getProperty('REPLACE')):
            log.info('REPLACE flag is specified, start replacing JMS Uniform Distributed Topic [' + str(distTopicName) + '] properties.' )
        
        subDeploymentDistTopic.setJNDIName(distTopicJNDI)
        if not distTopicLoadBalancingPolicy is None and len(distTopicLoadBalancingPolicy)>0:
            subDeploymentDistTopic.setLoadBalancingPolicy(distTopicLoadBalancingPolicy)
        if not distTopicLocalJNDI is None and len(distTopicLocalJNDI)>0:
            subDeploymentDistTopic.setLocalJNDIName(distTopicLocalJNDI)
        if not distTopicMxMsgSize is None and len(distTopicMxMsgSize)>0:
            subDeploymentDistTopic.setMaximumMessageSize(int(distTopicMxMsgSize))
        if not distTopicMsgPerfPref is None and len(distTopicMsgPerfPref)>0:    
            subDeploymentDistTopic.setMessagingPerformancePreference(int(distTopicMsgPerfPref))            
        if not distTopicIncompWrkExpTime is None and len(distTopicIncompWrkExpTime)>0:
            subDeploymentDistTopic.setIncompleteWorkExpirationTime(int(distTopicIncompWrkExpTime))            
        if not distTopicUnitOfWrkPolicy is None and len(distTopicUnitOfWrkPolicy)>0:
            subDeploymentDistTopic.setUnitOfWorkHandlingPolicy(distTopicUnitOfWrkPolicy)    
        if not distTopicDefUnitOfOrder is None and len(distTopicDefUnitOfOrder)>0:
            if distTopicDefUnitOfOrder.upper()=='TRUE':
                subDeploymentDistTopic.setDefaultUnitOfOrder(1)
            else:
                subDeploymentDistTopic.setDefaultUnitOfOrder(0)
        if not distTopicUnitOfOrderRoute is None and len(distTopicUnitOfOrderRoute)>0:                
            subDeploymentDistTopic.setUnitOfOrderRouting(distTopicUnitOfOrderRoute)
        if not distTopicAttachSender is None and len(distTopicAttachSender)>0:
            subDeploymentDistTopic.setAttachSender(distTopicAttachSender)
        if not distTopicDestinationKeys is None and len(distTopicDestinationKeys)>0:
            destinationKeyList=distTopicDestinationKeys.split(',')
            subDeploymentDistTopic.setDestinationKeys(destinationKeyList)
            
        subDeploymentDistTopic.setSubDeploymentName(subDeploymentName)

    # done with topic creation
	
