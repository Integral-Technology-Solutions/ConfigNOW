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

#=======================================================================================
# Configure JDBC resources via WLST Offline
#=======================================================================================
def __configureDataSources(configProperties):
	try:
		datasourceNames = configProperties.getProperty('jdbc.datasources')
		requiresNameChange=0
		if not datasourceNames is None:
			dataSources = datasourceNames.split(",")
			for dataSource in dataSources:
				if __configureDataSource(configProperties, dataSource):
					requiresNameChange=1
			if requiresNameChange:
				updateDomain()
				closeDomain()
				domainPath=configProperties.getProperty('wls.domain.dir')
				domainName=configProperties.getProperty('wls.domain.name')
				readDomain(domainPath + '/' + domainName)
				for dataSource in dataSources:
					__renameDataSource(configProperties, dataSource)
	except Exception, error:
		log.error('Unable to configure data sources: ' + str(error))
		raise error
					
def __configureDataSource(configProperties, dataSource):
	
	dataSourceName=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Name')
	originalDataSourceName = configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.OriginalName')
	driverName=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Driver')
	dbUser=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Username')
	dbPassword=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Password')
	dbURL=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.URL')
	dbCapacityInit=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Capacity.Initial')
	dbCapacityMax=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Capacity.Max')
	dbCapacityInc=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Capacity.Increment')
	dbCapacityTestOnReserve=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.TestOnReserve')
	dbJNDI=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.JNDI')
	xaDataSource=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.UseXADataSourceInterface')
	dbTargets=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Targets')
	dbScripts=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Scripts')
	driverProperties=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.DriverProperties')
	delDriverProperties=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.DeleteDriverProperties')
	shrinkPeriodMinutes=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Capacity.ShrinkPeriod')
	testTableName=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.TestTableName')
	loginDelaySeconds=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.LoginDelaySeconds')
	debugLevel=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.DebugLevel')
	globalTxProtocol=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.GlobalTransactionProtocol')
	connCreationRetrySeconds=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.ConnectionCreationRetryFrequencySeconds')
	testFreqSeconds=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.TestFrequencySeconds')
	secondsIdlePool=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.SecondsToTrustAnIdlePoolConnection')
	removeInfectedConnections=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.RemoveInfectedConnections')
	xaRetryDurationSeconds=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.XaRetryDurationSeconds')
	xaRetryIntervalSeconds=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.XaRetryIntervalSeconds')
	resourceHealthMonitoring=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.ResourceHealthMonitoring')
	statementCacheSize=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.StatementCacheSize')
	
	dataSourceNotExist=0
	requiresNameChange=0
	
	try:
		cd('/JDBCSystemResources/' + dataSourceName + '/JdbcResource/' + dataSourceName + '/JDBCDriverParams/NO_NAME_0')
		ds=dataSourceName
	except Exception, error:
		try:
			if originalDataSourceName:
				log.debug(dataSourceName + ' does not exist, checking if ' + originalDataSourceName + ' exists.')
				cd('/JDBCSystemResources/' + originalDataSourceName + '/JdbcResource/' + originalDataSourceName + '/JDBCDriverParams/NO_NAME_0')
				ds=originalDataSourceName
				requiresNameChange=1
			else:
				dataSourceNotExist=1
		except Exception, error:
			dataSourceNotExist=1
	
	if dataSourceNotExist:
		ds=dataSourceName
		cd ('/')
		create(dataSourceName,'JDBCSystemResource')
		cd('/JDBCSystemResources/' + dataSourceName + '/JdbcResource/' + dataSourceName)
		create('NO_NAME_0', 'JDBCDriverParams')
		cd('JDBCDriverParams/NO_NAME_0')
		log.info('Created data source [' + str(dataSourceName) + ']')
	else:
		log.info('Configuring data source [' + str(dataSourceName) + ']')
	
	log.debug('Setting driver name: ' + driverName)
	set('DriverName',driverName)
	log.debug('Setting URL: ' + dbURL)
	set('URL',dbURL)
	set('PasswordEncrypted', dbPassword)
			
	if not xaDataSource is None and xaDataSource.upper()=='TRUE':
		log.debug('Setting use XA data source interface to true')
		set('UseXADataSourceInterface', 'true')
			
	if dataSourceNotExist:
		log.debug('Creating Properties mbean - NO_NAME_0')
		create('NO_NAME_0','Properties')
	cd('Properties/NO_NAME_0')

	if dataSourceNotExist:
		log.debug('Creating Property mbean - user')
		create('user','Property')
	cd('Property/user')
	cmo.setValue(dbUser)
	
	if driverProperties:
		dpList=driverProperties.split(',')
		for driverProp in dpList:
			dpName=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.DriverProperty.' + driverProp + '.Name')
			dpValue=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.DriverProperty.' + driverProp + '.Value')
			if dpName and dpValue:
				try:
					try:
						cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds + '/JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0/Property/' + dpName)
					except Exception, error:
						log.debug('Creating Property mbean - ' + dpName)
						cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds + '/JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0')
						create(dpName,'Property')
						cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds + '/JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0/Property/' + dpName)
					log.debug('Setting ' + dpName + ' driver property with value ' + dpValue)
					cmo.setValue(dpValue)
				except Exception, error:
					log.warn('Ignoring ' + dpName + ' driver property setting.')

	if delDriverProperties:
		delList=delDriverProperties.split(',')
		cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds + '/JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0')
		for delProp in delList:
			log.debug('Removing ' + delProp + ' driver property')
			delete(delProp,'Property')
	
	if dataSourceNotExist:
		cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds)
		log.debug('Creating JDBCConnectionPoolParams mbean - NO_NAME_0')
		create('NO_NAME_0','JDBCConnectionPoolParams')
		
	cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds + '/JDBCConnectionPoolParams/NO_NAME_0')
	
	if not dbCapacityInit is None:
		log.debug('Setting initial capacity : ' + str(dbCapacityInit))
		set('InitialCapacity',int(dbCapacityInit))
	if not dbCapacityMax is None:
		log.debug('Setting max capacity : ' + str(dbCapacityMax))
		set('MaxCapacity', int(dbCapacityMax))
	if not dbCapacityInc is None:
		log.debug('Setting capacity increment : ' + str(dbCapacityInc))
		set('CapacityIncrement', int(dbCapacityInc))    
	if not dbCapacityTestOnReserve is None:
		if dbCapacityTestOnReserve.upper()=='TRUE':
			set('TestConnectionsOnReserve','True')
		else:
			if dbCapacityTestOnReserve.upper()=='FALSE':
				set('TestConnectionsOnReserve','False')
		log.debug('Setting test connections on reserve : ' + dbCapacityTestOnReserve)
	if debugLevel:
		log.debug('Setting JDBC XA debug level : ' + str(debugLevel))
		set('JDBCXADebugLevel',int(debugLevel))
	if statementCacheSize:
		log.debug('Setting statement cache size : ' + str(statementCacheSize))
		set('StatementCacheSize',int(statementCacheSize))
	if connCreationRetrySeconds:
		log.debug('Setting connection creation retry frequency seconds: ' + connCreationRetrySeconds)
		set('ConnectionCreationRetryFrequencySeconds',int(connCreationRetrySeconds))
	if testFreqSeconds:
		log.debug('Setting test frequency seconds: ' + testFreqSeconds)
		set('TestFrequencySeconds',int(testFreqSeconds))
	if secondsIdlePool:
		log.debug('Setting seconds to trust an idle pool Connection: ' + secondsIdlePool)
		set('SecondsToTrustAnIdlePoolConnection',int(secondsIdlePool))
	if shrinkPeriodMinutes:
		log.debug('Setting shrink frequency seconds: ' + shrinkPeriodMinutes)
		set('ShrinkFrequencySeconds',int(shrinkPeriodMinutes))
	if testTableName:
		log.debug('Setting test table name : ' + str(testTableName))
		set('TestTableName',testTableName)
	if loginDelaySeconds:
		log.debug('Setting login delay second : ' + str(loginDelaySeconds))
		set('LoginDelaySeconds',int(loginDelaySeconds))
	if not removeInfectedConnections is None and removeInfectedConnections.upper()=='TRUE':
		set('RemoveInfectedConnections', 1)
	else:
		set('RemoveInfectedConnections', 0)

	if dataSourceNotExist or xaRetryDurationSeconds or xaRetryIntervalSeconds or resourceHealthMonitoring:
		cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds)
		log.debug('Creating JDBCXAParams mbean - NO_NAME_0')
		create('NO_NAME_0','JDBCXAParams')	
	
	if  xaRetryDurationSeconds or xaRetryIntervalSeconds or resourceHealthMonitoring:
		cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds + '/JDBCXAParams/NO_NAME_0')
		if xaRetryDurationSeconds:
			log.debug('Setting XA retry duration seconds : ' + str(xaRetryDurationSeconds))
			set('XaRetryDurationSeconds', int(xaRetryDurationSeconds))
		if xaRetryIntervalSeconds:
			log.debug('Setting XA retry interval seconds : ' + str(xaRetryIntervalSeconds))
			set('XaRetryIntervalSeconds', int(xaRetryIntervalSeconds))
		if not resourceHealthMonitoring is None and resourceHealthMonitoring.upper()=='TRUE':
			log.debug('Setting resource health monitoring : ' + str(resourceHealthMonitoring))
			set('ResourceHealthMonitoring', true)

	if dataSourceNotExist:
		cd('/JDBCSystemResources/' + ds + '/JdbcResource/' + ds)
		log.debug('Creating JDBCDataSourceParams mbean - NO_NAME_0')
		create('NO_NAME_0','JDBCDataSourceParams')
	
	cd('/JDBCSystemResource/' + ds + '/JdbcResource/' + ds + '/JDBCDataSourceParams/NO_NAME_0')
		
	if not dbJNDI is None:
		log.debug('Setting JNDI name: ' + dbJNDI)
		set('JNDINames',dbJNDI)
	if globalTxProtocol:
		log.debug('Setting global transactions procotol: ' + globalTxProtocol)
		set('GlobalTransactionsProtocol', globalTxProtocol)
		
	if not dbTargets is None and len(dbTargets)>0:
		dbTargetList=dbTargets.split(',')
		cd('/JDBCSystemResource/' + ds)
		
		# Unassigning targets to ensure unspecified targets are removed
		targets = get('Target')
		if not targets is None:
			for i in range(0, len(targets)):
				targetName=targets[i].getName()
				log.debug('Unassigning resource : ' + str(dataSourceName) + ' from target : ' + str(targetName))
				unassign('JDBCSystemResource', ds, 'Target', targetName)
		for tmpTarget in dbTargetList:
			try:
				targetName=None
				targetType=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.' + tmpTarget + '.TargetType')
				if targetType.upper()=='CLUSTER':
					targetName=configProperties.getProperty('wls.cluster.' + tmpTarget + '.name')
				elif targetType.upper()=='SERVER':
					if configProperties.getProperty('wls.server.' + tmpTarget + '.replace.name') is None: 
						targetName=configProperties.getProperty('wls.server.' + tmpTarget + '.name') 
					else: 
						targetName=configProperties.getProperty('wls.server.' + tmpTarget + '.replace.name') 

				if targetName:
					log.debug('Adding resource : ' + str(dataSourceName) + ' to target : ' + str(targetName))
					assign('JDBCSystemResource', ds, 'Target', targetName)
				else:
					raise ScriptError, 'Unable to lookup target [' + str(tmpTarget) + '] for DataSource [' + str(ds) + ']'
			except Exception, error:
				raise ScriptError, 'Unable to lookup target [' + str(tmpTarget) + '] for DataSource [' + str(ds) + ']: ' + str(error)
		
	if not dbScripts is None:
		runDbScripts(dbScripts, dbURL, dbUser, dbPassword, driverName)
	
	return requiresNameChange
	
def __renameDataSource(configProperties, dataSource):

	dataSourceName=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.Name')
	originalDataSourceName=configProperties.getProperty('jdbc.datasource.' + str(dataSource) + '.OriginalName')
	
	requiresNameChange=0
	
	try:
		if originalDataSourceName:
			log.debug(dataSourceName + ' does not exist, checking if ' + originalDataSourceName + ' exists.')
			cd('/JDBCSystemResources/' + originalDataSourceName + '/JdbcResource/' + originalDataSourceName + '/JDBCDriverParams/NO_NAME_0')
			ds=originalDataSourceName
			requiresNameChange=1
	except Exception, error:
		return
	
	if requiresNameChange:
		log.info('Renaming ' + originalDataSourceName + ' to ' + dataSourceName)
		cd('/JDBCSystemResource/' + originalDataSourceName)
		set('Name', dataSourceName)
		cd('JdbcResource/' + originalDataSourceName)
		set('Name', dataSourceName)