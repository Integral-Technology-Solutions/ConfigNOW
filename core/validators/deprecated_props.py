def run(cfg):
	valid = 1
	soaDatasourceNames = cfg.getProperty('soa.db.dataSources')
	osbDatasourceNames = cfg.getProperty('osb.db.dataSources')
	wliDatasourceNames = cfg.getProperty('wli.db.dataSources')
	osrDatasourceNames = cfg.getProperty('osr.db.dataSources')
	jdbcDatasourceNames = cfg.getProperty('jdbc.datasources')
	svrs=cfg.getProperty('wls.servers')
	clrs=cfg.getProperty('wls.clusters')
	if svrs:
		serversList = svrs.split(',')
	if clrs:	
		clustersList = clrs.split(',')
	if osbDatasourceNames:
		log.error('osb.db.dataSources property is deprecated. Please update to use jdbc.datasources property')		
	if wliDatasourceNames:
		log.error('wli.db.dataSources property is deprecated. Please update to use jdbc.datasources property')	
	if osrDatasourceNames:
		log.error('osr.db.dataSources property is deprecated. Please update to use jdbc.datasources property')
	if soaDatasourceNames:
		log.warn('soa.db.dataSources property is deprecated.')
		soaDsList = soaDatasourceNames.split(",")
		if jdbcDatasourceNames:
			log.error('Cannot automatically update soa.db.dataSources to jdbc.datasources')
			valid=0
		else:
			log.info('Attempting to convert soa.db.dataSources properties to jdbc.datasources properties')
			cfg.setProperty('jdbc.datasources', soaDatasourceNames)
			for dataSource in soaDsList:
			
				dataSourceName=None
				driverName=None
				dbUser=None
				dbPassword=None
				dbURL=None
				dbCapacityInit=None
				dbCapacityMax=None
				dbCapacityInc=None
				dbCapacityTestOnReserve=None
				dbScripts=None
				dbTargets=None
				dbReplaceName=None
				dbJNDI=None
			
				dbType=cfg.getProperty('soa.db.' + str(dataSource) + '.type')
				if dbType:
					log.warn('soa.db.' + str(dataSource) + '.type property is deprecated.')
				dbName=cfg.getProperty('soa.db.' + str(dataSource) + '.name')
				if dbName:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Name',dbName)
					log.info('Converted soa.db.' + str(dataSource) + '.name to jdbc.datasource.' + str(dataSource) + '.Name')
				else:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Name',str(dataSource))
					log.info('Setting jdbc.datasource.' + str(dataSource) + '.Name to ' + str(dataSource))
				driverName=cfg.getProperty('soa.db.' + str(dataSource) + '.driver.class')
				if driverName:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Driver',driverName)
					log.info('Converted soa.db.' + str(dataSource) + '.driver.class to jdbc.datasource.' + str(dataSource) + '.Driver')
				dbUser=cfg.getProperty('soa.db.' + str(dataSource) + '.username')
				if dbUser:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Username',dbUser)
					log.info('Converted soa.db.' + str(dataSource) + '.username to jdbc.datasource.' + str(dataSource) + '.Username')
				dbPassword=cfg.getProperty('soa.db.' + str(dataSource) + '.password')
				if dbPassword:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Password', dbPassword)
					log.info('Converted soa.db.' + str(dataSource) + '.password to jdbc.datasource.' + str(dataSource) + '.Password')
				dbURL=cfg.getProperty('soa.db.' + str(dataSource) + '.url')
				if dbURL:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.URL', dbURL)
					log.info('Converted soa.db.' + str(dataSource) + '.url to jdbc.datasource.' + str(dataSource) + '.URL')
				dbCapacityInit=cfg.getProperty('soa.db.' + str(dataSource) + '.capacity.initial')
				if dbCapacityInit:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Capacity.Initial', dbCapacityInit)
					log.info('Converted soa.db.' + str(dataSource) + '.capacity.initial to jdbc.datasource.' + str(dataSource) + '.Capacity.Initial')
				dbCapacityMax=cfg.getProperty('soa.db.' + str(dataSource) + '.capacity.max')
				if dbCapacityMax:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Capacity.Max', dbCapacityMax)
					log.info('Converted soa.db.' + str(dataSource) + '.capacity.max to jdbc.datasource.' + str(dataSource) + '.Capacity.Max')
				dbCapacityInc=cfg.getProperty('soa.db.' + str(dataSource) + '.capacity.increment')
				if dbCapacityInc:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Capacity.Increment',dbCapacityInc)
					log.info('Converted soa.db.' + str(dataSource) + '.capacity.increment to jdbc.datasource.' + str(dataSource) + '.Capacity.Increment')
				dbCapacityTestOnReserve=cfg.getProperty('soa.db.' + str(dataSource) + '.testOnReserve')
				if dbCapacityTestOnReserve:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.TestOnReserve', dbCapacityTestOnReserve)
					log.info('Converted soa.db.' + str(dataSource) + '.testOnReserve to jdbc.datasource.' + str(dataSource) + '.TestOnReserve')
				dbJNDI=cfg.getProperty('soa.db.' + str(dataSource) + '.jndi')
				if dbJNDI:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.JNDI', dbJNDI)
					log.info('Converted soa.db.' + str(dataSource) + '.jndi to jdbc.datasource.' + str(dataSource) + '.JNDI')
				xaDataSource=cfg.getProperty('soa.db.' + str(dataSource) + '.xaDataSource')
				if xaDataSource:
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + 'UseXADataSourceInterface', xaDataSource)
					log.info('Converted soa.db.' + str(dataSource) + '.xaDataSource to jdbc.datasource.' + str(dataSource) + 'UseXADataSourceInterface')
					
				dbTargets=cfg.getProperty('soa.db.' + str(dataSource) + '.targets')
				dbTargetsList = dbTargets.split(',')
				
				newTargets=''
				for i in range(0, len(dbTargetsList)):
					target = dbTargetsList[i]
					log.debug('Checking for server or cluster with name ' + target)
					foundTarget=0
					if svrs:
						for server in serversList:
							if str(target)==str(cfg.getProperty('wls.server.' + str(server) + '.name')):
								newTargets=newTargets+str(server)
								if i is not (len(dbTargetsList)-1):
									newTargets=str(newTargets) + ','
								log.info('Creating property jdbc.datasource.' + str(dataSource) + '.' + str(server) + '.TargetType with value [Server]')
								cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.' + str(server) + '.TargetType', 'Server')
								foundTarget=1
					if not foundTarget and clrs:
						for cluster in clustersList:
							if str(target)==str(cfg.getProperty('wls.cluster.' + str(cluster) + '.name')):
								newTargets=newTargets+str(cluster)
								if i is not (len(dbTargetsList)-1):
									newTargets=str(newTargets) + ','
								log.info('Creating property jdbc.datasource.' + str(dataSource) + '.' + str(cluster) + '.TargetType with value [Cluster]')
								cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.' + str(cluster) + '.TargetType', 'Cluster')	
				
				if newTargets:
					log.info('Converted property soa.db.' + str(dataSource) + '.targets to jdbc.datasource.' + str(dataSource) + '.Targets with value [' + newTargets + ']')
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Targets',newTargets)
				
				dbReplaceName=cfg.getProperty('soa.db.' + str(dataSource) + '.replaceName')
				if dbReplaceName:
					cfg.setProperty('jdbc.datasources.' + str(dataSource) + '.OriginalName', dbName)
					cfg.setProperty('jdbc.datasource.' + str(dataSource) + '.Name', dbReplaceName)
					log.info('Set jdbc.datasources.' + str(dataSource) + '.OriginalName to ' + dbName)
					log.info('Set jdbc.datasources.' + str(dataSource) + '.Name to ' + dbReplaceName)
				
	return valid