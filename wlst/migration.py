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

from jarray import array, zeros

#=======================================================================================
# Import common library
#=======================================================================================

try:
	commonModule
except NameError:
	execfile('common/common.py')

serverModule = '1.0.0'

log.debug('Loading module [migration.py] version [' + serverModule + ']')

#=======================================================================================
# Configure Migration Server Components
#=======================================================================================
def configureMigrationServerComponents(resourcesProperties, domainProperties):
    servers=domainProperties.getProperty('wls.servers')
    if not servers is None and len(servers) > 0:
        serverList = servers.split(',')
        for server in serverList:
            name = getServerName(server, domainProperties)
	    autoMigrationEnabled = domainProperties.getProperty('wls.server.' + server + '.auto.migration.enabled')
	    migrationMachine = domainProperties.getProperty('wls.server.' + server + '.migration.machine')
	    jmsMigrationServers = domainProperties.getProperty('wls.server.' + server + '.jms.migration.servers')
	    jtaMigrationServers = domainProperties.getProperty('wls.server.' + server + '.jta.migration.servers')
	    numRestartAttempts = domainProperties.getProperty('wls.server.' + server + '.jms.migration.numRestartAttempts')
	    restartOnFailure = domainProperties.getProperty('wls.server.' + server + '.jms.migration.restartOnFailure')
	    secondsBetweenRestarts = domainProperties.getProperty('wls.server.' + server + '.jms.migration.secondsBetweenRestarts')
	    jmsMigrationPolicy = domainProperties.getProperty('wls.server.' + server + '.jms.migration.policy')
            jtaMigrationPolicy = domainProperties.getProperty('wls.server.' + server + '.jta.migration.policy')

	    if not autoMigrationEnabled is None and autoMigrationEnabled.upper()=='TRUE':
		log.info('Setting auto migration to true for ' + str(name))
		cd ('/Servers/' + str(name))
		set('AutoMigrationEnabled','True')
	    else:
	    	cd ('/Servers/' + str(name))
		set('AutoMigrationEnabled','False')
            if not migrationMachine is None:
                actualMachineName = getMachineName(migrationMachine, domainProperties)
                log.info('Setting migration machine (candidate machine) [' + actualMachineName + '] for server [' + str(name) + '].')
                cd ('/Servers/' + str(name))
                set('CandidateMachines',jarray.array([ObjectName('com.bea:Name=' + actualMachineName + ',Type=Machine')], ObjectName))
	    if not jmsMigrationServers is None:
	    	log.info('Setting JMS migration servers (constrained candidate servers) for server [' + str(name) + '].')
	        jmsMigrationServersList = jmsMigrationServers.split(",")
	        numOfJmsMigrationServers = jmsMigrationServersList.__len__()
		jmsMigrationServersArray = zeros(numOfJmsMigrationServers, ObjectName)
		i = 0
		for jmsMigrationServer in jmsMigrationServersList:
		    jmsMigrationServerName = getServerName(jmsMigrationServer, domainProperties)
		    try:
	                cd('/MigratableTargets/' + jmsMigrationServerName + ' (migratable)')
	            except Exception, error:
		        raise ScriptError, 'Could not find migratable target matching [' + jmsMigrationServerName + '].'
	            log.info('Setting JMS migration server [' + jmsMigrationServerName + '] for server [' + str(name) + '].')
	            jmsMigrationServersArray[i] = ObjectName('com.bea:Name=' + jmsMigrationServerName + ',Type=Server')
	            i = i + 1
	        set('ConstrainedCandidateServers',jmsMigrationServersArray)
	    if not restartOnFailure is None and restartOnFailure.upper()=='TRUE':
	        log.info('Setting restart on failure flag for JMS migration server [' + name + '].')
	        cd('/MigratableTargets/' + name + ' (migratable)')
	        cmo.setRestartOnFailure(true)
	    if not numRestartAttempts is None:      
	        log.info('Setting number of restart attempts to [' + str(numRestartAttempts) + '] for JMS migration server [' + name + '].')
	        cd('/MigratableTargets/' + name + ' (migratable)')
	        cmo.setNumberOfRestartAttempts(int(numRestartAttempts))
	        cmo.setRestartOnFailure(true)
	    if not secondsBetweenRestarts is None:
	        log.info('Setting number of seconds between restarts to [' + str(secondsBetweenRestarts) + '] for JMS migration server [' + name + '].')
	        cd('/MigratableTargets/' + name + ' (migratable)')
	        cmo.setSecondsBetweenRestarts(30)
	        cmo.setRestartOnFailure(true)
	    if not jmsMigrationPolicy is None:
	        cd('/MigratableTargets/' + name + ' (migratable)')
	        if jmsMigrationPolicy=='manual':
		    log.info('Setting migration policy to [Manual] for JMS migration server [' + name + '].')
		    cmo.setMigrationPolicy('manual')
	        elif jmsMigrationPolicy=='exactly-once':
		    log.info('Setting migration policy to [Auto-Migrate Exactly Once] for JMS migration server [' + name + '].')
		    cmo.setMigrationPolicy('exactly-once')
	        elif jmsMigrationPolicy=='failure-recovery':
		    log.info('Setting migration policy to [Auto-Migrate Failure Recovery] for JMS migration server [' + name + '].')
		    cmo.setMigrationPolicy('failure-recovery')
	        else:
		    raise ScriptError, 'Invalid migration policy [' + migrationPolicy + '] for JMS migration server [' + name + '].'
	    if not jtaMigrationServers is None:
	    	log.info('Setting JTA migration servers (constrained candidate servers) for server [' + str(name) + '].')
	        jtaMigrationServersList = jtaMigrationServers.split(",")
	        numOfJtaMigrationServers = jtaMigrationServersList.__len__()
		jtaMigrationServersArray = zeros(numOfJtaMigrationServers, ObjectName)
		i = 0
		for jtaMigrationServer in jtaMigrationServersList:
		    try:
		        jtaMigrationServerName = getServerName(jtaMigrationServer, domainProperties)
		        cd('/Servers/' + jtaMigrationServerName + '/JTAMigratableTarget/' + jtaMigrationServerName)
		    except Exception, error:
		        raise ScriptError, 'Could not find migratable target matching [' + getServerName(jtaMigrationServer, domainProperties) + '].'
	        log.info('Setting JTA migration server [' + jtaMigrationServerName + '] for server [' + str(name) + '].')
	        jtaMigrationServersArray[i] = ObjectName('com.bea:Name=' + jtaMigrationServerName + ',Type=Server')
	        i = i + 1
	        set('ConstrainedCandidateServers',jtaMigrationServersArray)
	        
            if not jtaMigrationPolicy is None:
                cd('/Servers/' + name + '/JTAMigratableTarget/' + name)
	        if jtaMigrationPolicy=='manual':
	            log.info('Setting migration policy to [Manual] for JTA migration server [' + name + '].')
		    cmo.setMigrationPolicy('manual')
	        elif jtaMigrationPolicy=='failure-recovery':
		    log.info('Setting migration policy to [Auto-Migrate Failure Recovery] for JTA migration server [' + name + '].')
		    cmo.setMigrationPolicy('failure-recovery')
	        else:
		    raise ScriptError, 'Invalid migration policy [' + jtaMigrationPolicy + '] for JTA migration server [' + name + '].'

#=======================================================================================
# Configure Migration Cluster Components
#=======================================================================================
def configureMigrationClusterComponents(resourcesProperties, domainProperties):
    
    clusters=domainProperties.getProperty('wls.clusters')
    if not clusters is None and len(clusters) > 0:
        clusterList = clusters.split(',')
        for cluster in clusterList:
            clusterName=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.name')
            migrationBasis=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.migration.basis')
            migrationTableName=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.migration.table.name')
            migrationDataSource=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.migration.data.source')
            migrationMachines=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.migration.machines')
            migrationAdditionalAttempts=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.migration.additional.attempts')
            migrationSleep=domainProperties.getProperty('wls.cluster.' + str(cluster) + '.migration.sleep')
            
            cd ('/')
            cluster = lookup(str(clusterName), 'Cluster')
	    
            try:
                if not migrationBasis is None:
                    log.info('Setting migration basis [' + str(migrationBasis) + '] for [' + str(clusterName) + '].')
                    cluster.setMigrationBasis(migrationBasis)
                if not migrationTableName is None:
                    log.info('Setting migration table name [' + str(migrationTableName) + '] for [' + str(clusterName) + '].')
                    cluster.setAutoMigrationTableName(migrationTableName)
                if not migrationDataSource is None:
                    log.info('Setting migration data source [' + str(migrationDataSource) + '].' )
                    cluster.setDataSourceForAutomaticMigration(getMBean('/SystemResources/' + migrationDataSource))
                if not migrationMachines is None:
                    cd ('/Clusters/' + str(clusterName))
                    machinesList = migrationMachines.split(',')
                    machineArray = jarray.zeros(len(machinesList), ObjectName)
                    position = 0
                    for machine in machinesList:
                        log.info('Setting migration machine [' + str(machine) + '] to cluster [' + str(clusterName) + '].')
                        machineArray[position] = ObjectName('com.bea:Name=' + str(machine) + ',Type=Machine')
                        position = position + 1
                    set('CandidateMachinesForMigratableServers',machineArray)
                if not migrationAdditionalAttempts is None:
                    log.info('Setting migration additional attempts [' + str(migrationAdditionalAttempts) + '] for [' + str(clusterName) + '].')
                    cluster.setAdditionalAutoMigrationAttempts(int(migrationAdditionalAttempts))
                if not migrationSleep is None:
                    log.info('Setting miliseconds to sleep between auto migration attempts [' + str(migrationSleep) + '] for [' + str(clusterName) + '].')
                    cluster.setMillisToSleepBetweenAutoMigrationAttempts(int(migrationSleep))
            except Exception, error:
                dumpStack()
                log.error(str(error))
                raise ScriptError, 'Could not configure migration at the cluster level [' + error + '].'
	    
#=======================================================================================
# Configure Migration
#=======================================================================================
def configureMigration(resourcesProperties, domainProperties):
    configureMigrationClusterComponents(resourcesProperties, domainProperties)
    configureMigrationServerComponents(resourcesProperties, domainProperties)