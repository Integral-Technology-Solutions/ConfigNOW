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

import validation_helper as helper

def run(config):
    dsValid=helper.validateList(config, 'jdbc.datasources')
    mdsValid=helper.validateList(config, 'jdbc.multidatasources')
    if dsValid and mdsValid:
        if validateDataSources(config):
            return False
    else:
        return False
    return True
    
def validateDataSources(domainProperties):

    error = 0
    
    datasources = domainProperties.getProperty('jdbc.datasources')
    if not datasources is None and len(datasources)>0:
        datasourceList = datasources.split(',')
        for datasource in datasourceList:
            helper.printHeader('[VALIDATING] DataSource ' + str(datasource) + ' properties')
            if validateDataSource(domainProperties, datasource):
                error = 1
                
    multidatasources = domainProperties.getProperty('jdbc.multidatasources')
    if not multidatasources is None and len(multidatasources)>0:
        multidatasourceList = multidatasources.split(',')
        for multidatasource in multidatasourceList:
            helper.printHeader('[VALIDATING] Multi-DataSource ' + str(multidatasource) + ' properties')
            if validateMultiDataSource(domainProperties, datasources, multidatasource):
                error = 1
                
    return error
    
def validateMultiDataSource(domainProperties, datasources, multidatasource):

    error = 0

    multidatasourceName = domainProperties.getProperty('jdbc.multidatasource.' + str(multidatasource) + '.Name')
    if multidatasourceName is None or len(multidatasourceName)==0:
        error = 1
        helper.required_property_error_msg('jdbc.multidatasource.' + str(multidatasource) + '.Name')
    else:
        log.debug('Multi-DataSource [' + str(multidatasource) + '] name property [' + str(multidatasourceName) + '] is valid.')

    targetDataSources = multidatasourceName = domainProperties.getProperty('jdbc.multidatasource.' + str(multidatasource) + '.DataSources')
    if targetDataSources is None or len(targetDataSources)==0:
        error = 1
        helper.required_property_error_msg('jdbc.multidatasource.' + str(multidatasource) + '.DataSources')
    else:
        if datasources is None or len(datasources)==0:
            error = 1
            log.error('Property jdbc.multidatasource.' + str(multidatasource) + '.DataSources defined but not jdbc.datasources to reference.')
        else:
            targetDataSourceList = targetDataSources.split(',')
            for targetDataSource in targetDataSourceList:
                datasourceList = datasources.split(',')
                exist = 0
                for datasource in datasourceList:
                    if datasource==targetDataSource:
                        exist = 1
                        break
                dsName=domainProperties.getProperty('jdbc.datasource.' + targetDataSource + '.Name')
                if dsName:
                    exist = 1
                if not exist:
                    error = 1
                    log.error('Property jdbc.multidatasource.' + str(multidatasource) + '.DataSources containing datasource [' + str(targetDataSource) + '] could not find reference in jdbc.datasources.')
                else:
                    log.debug('Multi-DataSource [' + str(multidatasource) + '] target [' + str(targetDataSource) + '] property is valid.')

    multidatasourceAlgorithmType = domainProperties.getProperty('jdbc.multidatasource.' + str(multidatasource) + '.AlgorithmType')          
    if not multidatasourceAlgorithmType is None and len(multidatasourceAlgorithmType)>0:
        if not multidatasourceAlgorithmType=='Load-Balancing' and not multidatasourceAlgorithmType=='Failover':
            error = 1
            log.error('The jdbc.multidatasource.' + str(multidatasource) + '.AlgorithmType supports only [Load-Balancing,Failover].')
        else:
            log.debug('Multi-DataSource [' + str(multidatasource) + '] algorithm property [' + str(multidatasourceAlgorithmType) + '] is valid.')

    multidatasourceJNDI = domainProperties.getProperty('jdbc.multidatasource.' + str(multidatasource) + '.JNDI')
    if multidatasourceJNDI is None or len(multidatasourceJNDI)==0:
        error = 1
        helper.required_property_error_msg('jdbc.multidatasource.' + str(multidatasource) + '.JNDI')
    else:
        log.debug('Multi-DataSource [' + str(multidatasource) + '] JNDI property [' + str(multidatasourceJNDI) + '] is valid.')

    multidatasourceFailoverRequestIfBusy = domainProperties.getProperty('jdbc.multidatasource.' + multidatasource + '.FailoverRequestIfBusy')          
    if not multidatasourceFailoverRequestIfBusy is None and len(multidatasourceFailoverRequestIfBusy)>0:
        if not multidatasourceFailoverRequestIfBusy.upper()=='TRUE' and not multidatasourceFailoverRequestIfBusy.upper()=='FALSE':
            error = 1
            log.error('The jdbc.multidatasource.' + str(multidatasource) + '.FailoverRequestIfBusy supports only [true,false].')
        else:
            log.debug('Multi-DataSource [' + str(multidatasource) + '] fail-over-if-busy property [' + str(multidatasourceFailoverRequestIfBusy) + '] is valid.')

    testFrequencySecs = domainProperties.getProperty('jdbc.multidatasource.' + str(multidatasource) + '.TestFrequencySeconds')
    if not testFrequencySecs is None and len(testFrequencySecs)>0:
        try:
            int(testFrequencySecs)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.multidatasource.' + str(multidatasource) + '.TestFrequencySeconds', str(testFrequencySecs))
        else:
            if int(testFrequencySecs)<0 or int(testFrequencySecs)>2147483647:
                log.error('jdbc.multidatasource.' + str(multidatasource) + '.TestFrequencySeconds [' + str(testFrequencySecs) + '] is not in valid number range [0-2147483647].')
            else:
                log.debug('Multi-Datasource [' + str(multidatasource) + '] test frequency property [' + str(testFrequencySecs) + '] is valid.')

    if validateTargets(domainProperties, 'jdbc.multidatasource.' + str(multidatasource), 'Multi-DataSource'):
        error = 1
    
    return error
    
def validateDataSource(domainProperties, datasource):
    error = 0
    
    datasourceName = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Name')
    if datasourceName is None or len(datasourceName)==0:
        error = 1
        helper.required_property_error_msg('jdbc.datasource.' + str(datasource) + '.Name')
    else:
        log.debug('DataSource [' + str(datasource) + '] name property [' + str(datasourceName) + '] is valid.')

    datasourceJNDI = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.JNDI')
    if datasourceJNDI is None or len(datasourceJNDI)==0:
        error = 1
        helper.required_property_error_msg('jdbc.datasource.' + str(datasource) + '.JNDI')
    else:
        log.debug('DataSource [' + str(datasource) + '] JNDI property [' + str(datasourceJNDI) + '] is valid.')

    datasourceURL = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.URL')
    if datasourceURL is None or len(datasourceURL)==0:
        error = 1
        helper.required_property_error_msg('jdbc.datasource.' + str(datasource) + '.URL')
    else:
        log.debug('DataSource [' + str(datasource) + '] URL property [' + str(datasourceURL) + '] is valid.')

    datasourceDriver = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Driver')
    if datasourceDriver is None or len(datasourceDriver)==0:
        error = 1
        helper.required_property_error_msg('jdbc.datasource.' + str(datasource) + '.Driver')
    else:
        log.debug('DataSource [' + str(datasource) + '] driver property [' + str(datasourceDriver) + '] is valid.')

    datasourceUsername = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Username')
    if datasourceUsername is None or len(datasourceUsername)==0:
        error = 1
        helper.required_property_error_msg('jdbc.datasource.' + str(datasource) + '.Username')
    else:
        log.debug('DataSource [' + str(datasource) + '] username property [' + str(datasourceUsername) + '] is valid.')

    datasourcePassword = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Password')
    if datasourcePassword is None or len(datasourcePassword)==0:
        # Check if password.prompt flag is set to determine if the password should be prompted for.
        passwordPrompt = domainProperties.getProperty('password.prompt')
        if not passwordPrompt:
            error = 1
            helper.required_property_error_msg('jdbc.datasource.' + str(datasource) + '.Password')
    else:
        #log.debug('DataSource [' + str(datasource) + '] password property [' + str(datasourcePassword) + '] is valid.')
        log.debug('DataSource [' + str(datasource) + '] password property is valid.')

    initialCap = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Capacity.Initial')
    if not initialCap is None and len(initialCap)>0:
        try:
            int(initialCap)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.Capacity.Initial',str(initialCap))
        else:
            if int(initialCap)<0 or int(initialCap)>2147483647:
                log.error('jdbc.datasource.' + str(datasource) + '.Capacity.Initial [' + str(initialCap) + '] is not in valid number range [0-2147483647].')
            else:
                log.debug('Datasource [' + str(datasource) + '] initial capacity property [' + str(initialCap) + '] is valid.')

    maxCap = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Capacity.Max')
    if not maxCap is None and len(maxCap)>0:
        try:
            int(maxCap)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.Capacity.Max', str(maxCap))
        else:
            if int(maxCap)<1 or int(maxCap)>2147483647:
                log.error('jdbc.datasource.' + str(datasource) + '.Capacity.Max [' + str(maxCap) + '] is not in valid number range [1-2147483647].')
            else:
                log.debug('Datasource [' + str(datasource) + '] max capacity property [' + str(maxCap) + '] is valid.')

    incrementCap = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Capacity.Increment')
    if not incrementCap is None and len(incrementCap)>0:
        try:
            int(incrementCap)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.Capacity.Increment', str(incrementCap))
        else:
            if int(incrementCap)<1 or int(incrementCap)>2147483647:
                log.error('jdbc.datasource.' + str(datasource) + '.Capacity.Increment [' + str(incrementCap) + '] is not in valid range [1-2147483647].')
            else:
                log.debug('Datasource [' + str(datasource) + '] increment capacity property [' + str(incrementCap) + '] is valid.')

    shrinkPeriod = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Capacity.ShrinkPeriod')
    if not shrinkPeriod is None and len(shrinkPeriod)>0:
        try:
            int(shrinkPeriod)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.Capacity.ShrinkPeriod', str(shrinkPeriod))
        else:
            if int(shrinkPeriod)<0 or int(shrinkPeriod)>2147483647:
                log.error('jdbc.datasource.' + str(datasource) + '.Capacity.ShrinkPeriod [' + str(shrinkPeriod) + '] is not in valid range [0-2147483647].')
            else:
                log.debug('Datasource [' + str(datasource) + '] shrink period property [' + str(shrinkPeriod) + '] is valid.')

    loginDelay = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.LoginDelaySeconds')
    if not loginDelay is None and len(loginDelay)>0:
        try:
            int(loginDelay)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.LoginDelaySeconds', str(loginDelay))
        else:
            if int(loginDelay)<0 or int(loginDelay)>2147483647:
                log.error('jdbc.datasource.' + str(datasource) + '.LoginDelaySeconds [' + str(loginDelay) + '] is not in valid number range [0-2147483647].')
            else:
                log.debug('Datasource [' + str(datasource) + '] login delay (seconds) property [' + str(loginDelay) + '] is valid.')

    debugLevel = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.DebugLevel')
    if not debugLevel is None and len(debugLevel)>0:
        try:
            int(debugLevel)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.DebugLevel', str(debugLevel))
        else:
            if int(debugLevel)<0:
                log.error('jdbc.datasource.' + str(datasource) + '.DebugLevel [' + str(debugLevel) + '] is not in valid number range [>=0].')
            else:
                log.debug('Datasource [' + str(datasource) + '] debug level property [' + str(debugLevel) + '] is valid.')

    datasourceTestOnReserve = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.TestOnReserve')
    if not datasourceTestOnReserve is None and len(datasourceTestOnReserve)>0:
        if not datasourceTestOnReserve.upper()=='TRUE' and not datasourceTestOnReserve.upper()=='FALSE':
            error = 1
            log.error('The jdbc.datasource.' + str(datasource) + '.TestOnReserve property supports only [true,false, or leave blank to use default].')
        else:
            log.debug('DataSource [' + str(datasource) + '] test-on-reserve property [' + str(datasourceTestOnReserve) + '] is valid.')

    datasourcePinnedToThread = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.PinnedToThread')
    if not datasourcePinnedToThread is None and len(datasourcePinnedToThread)>0:
        if not datasourcePinnedToThread.upper()=='TRUE' and not datasourcePinnedToThread.upper()=='FALSE':
            error = 1
            log.error('The jdbc.datasource.' + str(datasource) + '.PinnedToThread property supports only [true,false, or leave blank to use default].')
        else:
            log.debug('DataSource [' + str(datasource) + '] Pinned-to-Thread property [' + str(datasourcePinnedToThread) + '] is valid.')

    secondsToTrustAnIdlePoolConnection = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.SecondsToTrustAnIdlePoolConnection')
    if not secondsToTrustAnIdlePoolConnection is None and len(secondsToTrustAnIdlePoolConnection)>0:
        try:
            int(secondsToTrustAnIdlePoolConnection)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.SecondsToTrustAnIdlePoolConnection', str(secondsToTrustAnIdlePoolConnection))
        else:
            if int(secondsToTrustAnIdlePoolConnection)<0 or int(secondsToTrustAnIdlePoolConnection)>2147483647:
                log.error('jdbc.datasource.' + str(datasource) + '.SecondsToTrustAnIdlePoolConnection [' + str(secondsToTrustAnIdlePoolConnection) + '] is not in valid range [0-2147483647].')
            else:
                log.debug('Datasource [' + str(datasource) + '] seconds-to-trust-idle-pool-connection property [' + str(secondsToTrustAnIdlePoolConnection) + '] is valid.')

    datasourceGlobalTransactionsProtocol = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.GlobalTransactionsProtocol')
    if not datasourceGlobalTransactionsProtocol is None and len(datasourceGlobalTransactionsProtocol)>0:
        if not datasourceGlobalTransactionsProtocol=='OnePhaseCommit' and not datasourceGlobalTransactionsProtocol=='EmulateTwoPhaseCommit' and not datasourceGlobalTransactionsProtocol=='LoggingLastResource' and not datasourceGlobalTransactionsProtocol=='None':
            error = 1
            log.error('The jdbc.datasource.' + str(datasource) + '.GlobalTransactionsProtocol property supports only [OnePhaseCommit,EmulateTwoPhaseCommit,LoggingLastResource,None, or leave blank to use default].')
        else:
            log.debug('DataSource [' + str(datasource) + '] global-transactions-protocol property [' + str(datasourceGlobalTransactionsProtocol) + '] is valid.')

    statementCacheType = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.StatementCacheType')
    if not statementCacheType is None and len(statementCacheType)>0:
        if not statementCacheType=='LRU' and not statementCacheType=='FIXED':
            error = 1
            log.error('The jdbc.datasource.' + str(datasource) + '.StatementCacheType property supports only [LRU,FIXED, or leave blank to use default].')
        else:
            log.debug('DataSource [' + str(datasource) + '] statement cache type property [' + str(statementCacheType) + '] is valid.')

    statementCacheSize = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.StatementCacheSize')
    if not statementCacheSize is None and len(statementCacheSize)>0:
        try:
            int(statementCacheSize)
        except ValueError:
            helper.invalid_property_error_msg('jdbc.datasource.' + str(datasource) + '.StatementCacheSize', str(statementCacheSize))
        else:
            if int(statementCacheSize)<0 or int(statementCacheSize)>1024:
                log.error('jdbc.datasource.' + str(datasource) + '.StatementCacheSize [' + str(statementCacheSize) + '] is not in valid number range [0-1024].')
            else:
                log.debug('Datasource [' + str(datasource) + '] statement cache size property [' + str(statementCacheSize) + '] is valid.')

    datasourceUseXaDataSourceInterface = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.UseXaDataSourceInterface')
    if not datasourceUseXaDataSourceInterface is None and len(datasourceUseXaDataSourceInterface)>0:
        if not datasourceUseXaDataSourceInterface.upper()=='TRUE' and not datasourceUseXaDataSourceInterface.upper()=='FALSE':
            error = 1
            log.error('The jdbc.datasource.' + str(datasource) + '.UseXaDataSourceInterface property supports only [true,false, or leave blank to use default].')
        else:
            log.debug('DataSource [' + str(datasource) + '] use xa dataSource interface property [' + str(datasourceUseXaDataSourceInterface) + '] is valid.')

    datasourceKeepXaConnTillTxComplete = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.KeepXaConnTillTxComplete')
    if not datasourceKeepXaConnTillTxComplete is None and len(datasourceKeepXaConnTillTxComplete)>0:
        if not datasourceKeepXaConnTillTxComplete.upper()=='TRUE' and not datasourceKeepXaConnTillTxComplete.upper()=='FALSE':
            error = 1
            log.error('The jdbc.datasource.' + str(datasource) + '.KeepXaConnTillTxComplete property supports only [true,false, or leave blank to use default].')
        else:
            log.debug('DataSource [' + str(datasource) + '] keep xa connection till tx complete property [' + str(datasourceKeepXaConnTillTxComplete) + '] is valid.')

    datasourceResourceHealthMonitoring = domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.ResourceHealthMonitoring')
    if not datasourceResourceHealthMonitoring is None and len(datasourceResourceHealthMonitoring)>0:
        if not datasourceResourceHealthMonitoring.upper()=='TRUE' and not datasourceResourceHealthMonitoring.upper()=='FALSE':
            error = 1
            log.error('The jdbc.datasource.' + str(datasource) + '.ResourceHealthMonitoring property supports only [true,false, or leave blank to use default].')
        else:
            log.debug('DataSource [' + str(datasource) + '] resource health monitoring property [' + str(datasourceResourceHealthMonitoring) + '] is valid.')
    
    if validateTargets(domainProperties, 'jdbc.datasource.' + str(datasource), 'DataSource'):
        error = 1
    
    return error
    

def validateTargets(domainProperties, prefix, type):    
    
    error = 0

    datasourceTargets = domainProperties.getProperty(prefix + '.Targets')
    datasource = domainProperties.getProperty(prefix + '.Name')

    if datasourceTargets:
        targetsList=datasourceTargets.split(',')
        for target in targetsList:
            targetType=domainProperties.getProperty(prefix + '.' + target + '.TargetType')
            if targetType is not None:
                if targetType.upper()=='CLUSTER':
                    clusters = domainProperties.getProperty('wls.clusters')
                    if not clusters is None and len(clusters)>0:
                        clusterList = clusters.split(',')
                        exist = 0
                        for cluster in clusterList:
                            if cluster==target:
                                exist = 1
                                break
                        if not exist:
                            error = 1
                            log.error('The ' + prefix + '.' + target + '.TargetType' + ' property refers to a cluster that could not be referenced from wls.clusters property.')
                        else:
                            log.debug(type + ' [' + str(datasource) + '] target [' + str(target) + '] is valid.')
                    else:
                        error = 1
                        log.error('The ' + prefix + '.' + target + '.TargetType' + ' property refers to a cluster, but wls.clusters property does not exist.')
                elif targetType.upper()=='SERVER':
                    servers = domainProperties.getProperty('wls.servers')
                    if not servers is None and len(servers)>0:
                        serverList = servers.split(',')
                        exist = 0
                        for server in serverList:
                            if server==target:
                                exist = 1
                                break
                        if not exist:
                            error = 1
                            log.error('The ' + prefix + '.' + target + '.TargetType' + ' property refers to a server that could not be referenced from wls.servers property.')
                        else:
                            log.debug(type + ' [' + str(datasource) + '] target [' + str(target) + '] is valid.')
                    else:
                        error = 1
                        log.error('The ' + prefix + '.' + target + '.TargetType' + ' property refers to a server, but wls.servers property does not exist.')

                else:
                    error = 1
                    log.error('The ' + prefix + '.' + target + '.TargetType' + ' property supports only [Cluster,Server, or leave blank to use default AdminServer].')
            else:
                error = 1
                log.error('Target ' + str(target) + ' defined in property ' + prefix + '.Targets does not have a corresponding ' + prefix + '.' + target + '.TargetType property defined.')

    return error