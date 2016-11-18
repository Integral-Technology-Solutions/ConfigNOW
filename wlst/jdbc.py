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
## jdbc.py
##
## This script contains functions that manipulate JDBC resources.

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

jdbcModule = '1.1.1'


log.debug('Loading module [jdbc.py] version [' + jdbcModule + ']')

#=======================================================================================
# Create DataSources
#=======================================================================================

def createDataSources(resourceProperties, domainProperties):
	dataSources=resourceProperties.getProperty('jdbc.datasources')
	
	if not dataSources is None:
		dataSourceList=dataSources.split(',')
		
		for dataSource in dataSourceList:
			__createDataSource(dataSource, resourceProperties, domainProperties)
	else:
		log.info('JDBC DataSource is not specified, skipping ')
		
		
def __configureJTATimeout(domainProperties):
	try:
		jtaTimeout=domainProperties.getProperty('wls.domain.jta.timeout')
		if not jtaTimeout is None:
			cd('/JTA/'+ domainProperties.getProperty('wls.domain.name'))
			set('TimeoutSeconds',jtaTimeout)
	except Exception,error:
		log.error('unable to set JTA timeout property'+str(error))
		raise error
		
#=======================================================================================
# Create a DataSource
#=======================================================================================

def __createDataSource(datasourceName, resourceProperties, domainProperties):

	resourceName=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Name')
	jndi=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.JNDI')
	url=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.URL')
	driver=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Driver')
	username=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Username')
	password=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Password')
	initialCapacity=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Capacity.Initial')
	maxCapacity=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Capacity.Max')
	capacityIncrement=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Capacity.Increment')
	shrinkPeriodMinutes=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Capacity.ShrinkPeriod')
	testTableName=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.TestTableName')
	loginDelaySeconds=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.LoginDelaySeconds')
	debugLevel=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.DebugLevel')
	testOnReserve=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.TestOnReserve')
	driverProperties=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.DriverProperties')
	globalTxProtocol=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.GlobalTransactionProtocol')
	useXADataSource=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.UseXADataSourceInterface')
	connCreationRetrySeconds=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.ConnectionCreationRetryFrequencySeconds')
	testFreqSeconds=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.TestFrequencySeconds')
	secondsIdlePool=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.SecondsToTrustAnIdlePoolConnection')
	removeInfectedConnections=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.RemoveInfectedConnections')
	xaRetryDurationSeconds=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.XaRetryDurationSeconds')
	xaRetryIntervalSeconds=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.XaRetryIntervalSeconds')
	resourceHealthMonitoring=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.ResourceHealthMonitoring')
	statementCacheSize=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.StatementCacheSize')
	
	jdbcSystemResource = None
	jdbcSystemResourceExist = 0
	
	try:
		jdbcSystemResource = lookup(resourceName, 'JDBCSystemResource')
	except WLSTException, error:
		log.info('Unable to find JDBC DataSource [' + str(resourceName) + '], trying to create new one.')

	if jdbcSystemResource is None:
		try:
			log.info('Creating JDBC module [' + str(resourceName) + ']')
			# Create JDBC Resource Module
			cd('/')
			jdbcSystemResource = create(resourceName, 'JDBCSystemResource')
		except Exception, error:
			raise ScriptError, 'Unable to create JDBC module [' + str(resourceName) + ']: ' + str(error)
		
		tmpTargets=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.Targets')

		useDefaultTarget = 0
		if not tmpTargets is None and len(tmpTargets)>0:
			tmpTargetList=tmpTargets.split(',')
			for tmpTarget in tmpTargetList:
				dsTarget = None
				targetInstance = None

				dsTargetType=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.' + tmpTarget + '.TargetType')
				try:
					if dsTargetType.upper()=='CLUSTER':
						dsTarget=domainProperties.getProperty('wls.cluster.' + tmpTarget + '.name')
						targetInstance = lookup(dsTarget,'Cluster')
					else:
						dsTarget=domainProperties.getProperty('wls.server.' + tmpTarget + '.name')
						targetInstance = lookup(dsTarget,'Server')
					log.info('Adding resource : ' + str(resourceName) + ' to target : ' + str(dsTarget))
					jdbcSystemResource.addTarget(targetInstance)
				except Exception, error:
					raise ScriptError, 'Unable to lookup target [' + str(dsTarget) + '] for DataSource [' + str(resourceName) + ']: ' + str(error)
		else:
			# DEPRECATED
			#useDefaultTarget = 1
			useDefaultTarget = 0
		
		# DEPRECATED
		if useDefaultTarget:
			dsTarget=domainProperties.getProperty('wls.admin.name')
			targetServer = lookup(dsTarget, 'Server')
			try:
				log.info('Adding resource : ' + str(resourceName) + ' to target : ' + str(dsTarget))
				jdbcSystemResource.addTarget(targetServer)
			except Exception, error:
				raise ScriptError, 'Unable to lookup default target server [' + str(dsTarget) + '] for DataSource [' + str(resourceName) + ']: ' + str(error)
		
	else:
		jdbcSystemResourceExist = 1
		log.info('DataSource JDBC module [' + resourceName + '] already exists, checking REPLACE flag.')

	if not jdbcSystemResourceExist or isReplaceRequired(resourceProperties.getProperty('REPLACE')):
		if jdbcSystemResourceExist and isReplaceRequired(resourceProperties.getProperty('REPLACE')):
		  log.info('REPLACE flag is specified, start replacing JDBC [' + str(resourceName) + '] properties.' )

		jdbcFile = jdbcSystemResource.getDescriptorFileName()
		log.info('JDBC file name [' + str(jdbcFile) + '].')
	
		jdbcResource = jdbcSystemResource.getJDBCResource()
		jdbcResource.setName(resourceName)
	
		# Create the DataSource Params
		log.info('Creating DataSource Params' )
		dpBean = jdbcResource.getJDBCDataSourceParams()
		
		log.info('Setting JNDI [' + str(jndi) + '].')
		dpBean.setJNDINames(jndi.split(','))
		
		# Create the Driver Params
		log.info('Creating JDBC Driver Params' )
		drBean = jdbcResource.getJDBCDriverParams()
		log.info('Setting password [' + str(password) + '].')
		drBean.setPassword(password)
		log.info('Setting url [' + str(url) + '].')
		drBean.setUrl(url)
		log.info('Setting driver [' + str(driver) + ']')
		drBean.setDriverName(driver)
		if (not useXADataSource is None and useXADataSource.upper()=='TRUE') or useXADataSource is None:
			log.info('Enabling XA datasource interface. ' )
			drBean.setUseXaDataSourceInterface(true)    
		else:
			log.info('Disabling XA datasource interface. ' )
			drBean.setUseXaDataSourceInterface(false)
	
		if not globalTxProtocol is None:
			log.info('Setting Global Transactions Procotol: ' + globalTxProtocol)
			dpBean.setGlobalTransactionsProtocol(globalTxProtocol)
		
		propBean = drBean.getProperties()
		driverProps = Properties()
		log.info('Setting username [' + str(username) + '].')
		driverProps.setProperty('user',username)
		
		if not driverProperties is None and len(driverProperties)>0:
			driverPropertyList=driverProperties.split(',')
			for driverProperty in driverPropertyList:
				propName=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.DriverProperty.' + driverProperty + '.Name')
				propValue=resourceProperties.getProperty('jdbc.datasource.' + datasourceName + '.DriverProperty.' + driverProperty + '.Value')
				log.info('Setting ' + str(propName) + ' [' + str(propValue) + '].')
				driverProps.setProperty(str(propName),str(propValue))
		
		e = driverProps.propertyNames()
		while e.hasMoreElements() :
			propName = e.nextElement()

			myBean = propBean.lookupProperty(str(propName))
			if myBean is None:
				log.info('Create new property for [' + str(propName) + '].')
				myBean = propBean.createProperty(str(propName))
			log.info('Setting driver property [' + propName + '] : [' + driverProps.getProperty(propName) + ']')
			myBean.setValue(driverProps.getProperty(propName))
	
		# Create the ConnectionPool Params
		ppBean = jdbcResource.getJDBCConnectionPoolParams()
		if not initialCapacity is None:
			log.info('Setting initial capacity [' + str(initialCapacity) + '].')
			ppBean.setInitialCapacity(int(initialCapacity))
		if not maxCapacity is None:
			log.info('Setting max capacity [' + str(maxCapacity) + '].')
			ppBean.setMaxCapacity(int(maxCapacity))
		if not capacityIncrement is None:
			log.info('Setting capacity increment [' + str(capacityIncrement) + '].')
			ppBean.setCapacityIncrement(int(capacityIncrement))    
		if not debugLevel is None:
			log.info('Setting JDBC XA debug level [' + str(debugLevel) + '].')
			ppBean.setJDBCXADebugLevel(int(debugLevel))
		if not statementCacheSize is None:
			log.info('Setting statement cache size [' + str(statementCacheSize) + '].')
			ppBean.setStatementCacheSize(int(statementCacheSize))
		log.info('Setting JDBC TestConnectionOnReserve [' + str(testOnReserve) + '].')
		if not testOnReserve is None and testOnReserve.upper()=='TRUE':
			ppBean.setTestConnectionsOnReserve(1)
		else:
			ppBean.setTestConnectionsOnReserve(0)
	
		if not connCreationRetrySeconds is None:
			log.info('Setting Connection Creation Retry Frequency Seconds: ' + connCreationRetrySeconds)
			ppBean.setConnectionCreationRetryFrequencySeconds(int(connCreationRetrySeconds))
		if not testFreqSeconds is None:
			log.info('Setting Test Frequency Seconds: ' + testFreqSeconds)
			ppBean.setTestFrequencySeconds(int(testFreqSeconds))
		if not secondsIdlePool is None:
			log.info('Setting Seconds To Trust An Idle Pool Connection: ' + secondsIdlePool)
			ppBean.setSecondsToTrustAnIdlePoolConnection(int(secondsIdlePool))
			
		if not shrinkPeriodMinutes is None:
			ppBean.setShrinkFrequencySeconds(int(shrinkPeriodMinutes))
		if not testTableName == None:
			log.info('Setting TestTableName [' + str(testTableName) + '].')
			ppBean.setTestTableName(testTableName)

		if not loginDelaySeconds is None:
			log.info('Setting LoginDelaySecond [' + str(loginDelaySeconds) + '].')
			ppBean.setLoginDelaySeconds(int(loginDelaySeconds))
		if not removeInfectedConnections is None and removeInfectedConnections.upper()=='TRUE':
			ppBean.setRemoveInfectedConnections(1)
		else:
			ppBean.setRemoveInfectedConnections(0)
			
		# Adding KeepXaConnTillTxComplete to help with in-doubt transactions.
		log.info('Enabling XA params.')
		xaParams = jdbcResource.getJDBCXAParams()
		
		xaParams.setKeepXaConnTillTxComplete(true)
		
		if not xaRetryDurationSeconds is None:
			log.info('Setting XA Retry Duration Seconds [' + str(xaRetryDurationSeconds) + '].' )
			xaParams.setXaRetryDurationSeconds(int(xaRetryDurationSeconds))
		if not xaRetryIntervalSeconds is None:
			log.info('Setting XA Retry Interval Seconds [' + str(xaRetryIntervalSeconds) + '].' )
			xaParams.setXaRetryIntervalSeconds(int(xaRetryIntervalSeconds))
		if not resourceHealthMonitoring is None and resourceHealthMonitoring.upper()=='TRUE':
			xaParams.setResourceHealthMonitoring(true)
		log.debug('---------Configuring JTA timeout---------')
		__configureJTATimeout(domainProperties)
    
#=======================================================================================
# Create Multi-DataSources
#=======================================================================================

def createMultiDataSources(resourceProperties, domainProperties):
    multiDataSources=resourceProperties.getProperty('jdbc.multidatasources')

    if not multiDataSources is None:
        multiDataSourceList=multiDataSources.split(',')

        for multiDataSource in multiDataSourceList:
            __createMultiDataSource(multiDataSource, resourceProperties, domainProperties)

#=======================================================================================
# Create a Multi-DataSource
#=======================================================================================
def __createMultiDataSource(multiDataSourceName, resourceProperties, domainProperties):

    resourceName=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.Name')
    jndi=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.JNDI')	
    algorithm=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.AlgorithmType')
    failoverRequestIfBusy=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.FailoverRequestIfBusy')
    testFrequencySeconds=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.TestFrequencySeconds')
    datasources=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.DataSources')

    jdbcSystemResource = None
    jdbcSystemResourceExist = 0

    try:
        jdbcSystemResource = lookup(resourceName, 'JDBCSystemResource')
    except WLSTException, error:
        log.info('Unable to find JDBC Multi-DataSource [' + str(resourceName) + '], trying to create new one.')

    if jdbcSystemResource is None:
        try:
            log.info('Creating JDBC module [' + str(resourceName) + ']')
            # Create JDBC Resource Module
            cd('/')
            jdbcSystemResource = create(resourceName, 'JDBCSystemResource')
        except Exception, error:
            raise ScriptError, 'Unable to create JDBC module [' + str(resourceName) + ']: ' + str(error)

        tmpTargets=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.Targets')

        useDefaultTarget = 0
        if not tmpTargets is None and len(tmpTargets)>0:
		tmpTargetList=tmpTargets.split(',')
		for tmpTarget in tmpTargetList:
		    dsTarget = None
		    targetInstance = None

		    dsTargetType=resourceProperties.getProperty('jdbc.multidatasource.' + multiDataSourceName + '.' + tmpTarget + '.TargetType')
		    if dsTargetType.upper()=='CLUSTER':
			dsTarget=domainProperties.getProperty('wls.cluster.' + tmpTarget + '.name')
			targetInstance = lookup(dsTarget,'Cluster')
		    elif dsTargetType.upper()=='SERVER':
			dsTarget=domainProperties.getProperty('wls.server.' + tmpTarget + '.name')
			targetInstance = lookup(dsTarget,'Server')

		    try:
			if dsTargetType.upper()=='CLUSTER' or dsTargetType.upper()=='SERVER':
				log.info('Adding resource : ' + str(resourceName) + ' to target : ' + str(dsTarget))
				jdbcSystemResource.addTarget(targetInstance)
		    except Exception, error:
			raise ScriptError, 'Unable to lookup target [' + str(dsTarget) + '] for Multi-DataSource [' + str(resourceName) + ']: ' + str(error)
	else:
		useDefaultTarget = 1
			
        if useDefaultTarget:
            dsTarget=domainProperties.getProperty('wls.admin.name')
            targetServer = lookup(dsTarget, 'Server')
            try:
                log.info('Adding resource : ' + str(resourceName) + ' to target : ' + str(dsTarget))
                jdbcSystemResource.addTarget(targetServer)
            except Exception, error:
                raise ScriptError, 'Unable to lookup default target server [' + str(dsTarget) + '] for Multi-DataSource [' + str(resourceName) + ']: ' + str(error)

    else:
        jdbcSystemResourceExist = 1
        log.info('MultiDataSource JDBC module [' + resourceName + '] already exists, checking REPLACE flag.')

    if not jdbcSystemResourceExist or isReplaceRequired(resourceProperties.getProperty('REPLACE')):
        if jdbcSystemResourceExist and isReplaceRequired(resourceProperties.getProperty('REPLACE')):
          log.info('REPLACE flag is specified, start replacing JDBC MultiDataSource [' + str(resourceName) + '] properties.' )

        resourceFile = jdbcSystemResource.getDescriptorFileName()
		
        log.info('JDBC MultiDataSource file name [' + str(resourceFile) + '].')
        jdbcResource = jdbcSystemResource.getJDBCResource()
        jdbcResource.setName(resourceName)

        # Create the DataSource Params
        log.info('Creating DataSource Params' )
        dpBean = jdbcResource.getJDBCDataSourceParams()

        log.info('Setting JNDI [' + str(jndi) + '].')
        dpBean.setJNDINames([jndi])

        log.info('Setting Algorithm [' + str(algorithm) + '].')
        dpBean.setAlgorithmType(algorithm)
		
        log.info('Setting FailoverRequestIfBusy [' + str(failoverRequestIfBusy) + '].')
        if not failoverRequestIfBusy is None and failoverRequestIfBusy.upper()=='TRUE':
			dpBean.setFailoverRequestIfBusy(1)
        else:
            dpBean.setFailoverRequestIfBusy(0)
			
        if not testFrequencySeconds is None and len(testFrequencySeconds)>0:
            ppBean = jdbcResource.getJDBCConnectionPoolParams()
            log.info('Setting TestFrequencySeconds [' + str(testFrequencySeconds) + '].')
            ppBean.setTestFrequencySeconds(int(testFrequencySeconds))		
		
        datasourceList = datasources.split(',')
        datasourceNames = None
        for idx in xrange(0, len(datasourceList)):
            datasourceName = resourceProperties.getProperty('jdbc.datasource.' + datasourceList[idx] + '.Name')
            if datasourceNames is None:
                datasourceNames = datasourceName
            else:
                datasourceNames = datasourceNames + ',' + datasourceName
			
        log.info('Setting DataSource List [' + str(datasourceNames) + '].')
        dpBean.setDataSourceList(datasourceNames)
		
        

