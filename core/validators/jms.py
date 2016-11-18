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
from java.io import File

def run(config):
    valid = True
    
    fsValid=helper.validateList(config, 'persistent.filestores')
    if fsValid:
        if validateFilestoresProperty(config):
            valid = False
    else:
        valid = False
        
    jsValid=helper.validateList(config, 'jmsServers')
    if jsValid:
        if validateJmsServersProperty(config):
            valid = False
    else:
        valid = False
    
    jmValid=helper.validateList(config, 'jmsModules')
    if jmValid:
        if validateJmsModulesProperty(config):
            valid = False
    else:
        valid = False
        
    return valid


def validateFilestoresProperty(domainProperties):
    error = 0
    
    filestores = domainProperties.getProperty('persistent.filestores')
    if not filestores is None and len(filestores)>0:
       
        filestoreList = filestores.split(',')
        for filestore in filestoreList:
            helper.printHeader('[VALIDATING] filestore ' + str(filestore) + ' properties')
            
            filestoreName = domainProperties.getProperty('persistent.filestore.' + str(filestore) + '.Name')
            if filestoreName is None or len(filestoreName)==0:
                error = 1
                log.error('Please verify persistent.filestore.' + str(filestore) + '.Name property if it exists in configuration.')
            else:
                log.debug('Filestore [' + str(filestore) + '] name property [' + str(filestoreName) + '] is valid.')
                
            filestoreTarget = domainProperties.getProperty('persistent.filestore.' + str(filestore) + '.Target')
            if not filestoreTarget is None and len(filestoreTarget)>0:
                servers = domainProperties.getProperty('wls.servers')
                if not servers is None and len(servers)>0:
                    serverList = servers.split(',')
                    exist = 0
                    for server in serverList:
                        if server==filestoreTarget:
                            exist = 1
                            break
                    if not exist:
                        error = 1
                        log.error('persistent.filestore.' + str(filestore) + '.Target property refers to server that does not exist within wls.servers property.')
                    else:
                        log.debug('Filestore [' + str(filestore) + '] target property [' + str(filestoreTarget) + '] is valid.')
            
                filestoreMigratable = domainProperties.getProperty('persistent.filestore.' + str(filestore) + '.Migratable')
                if not filestoreMigratable is None and len(filestoreMigratable)>0:
                    if not filestoreMigratable.upper()=='TRUE' and not filestoreMigratable.upper()=='FALSE':
                        error = 1
                        log.error('The persistent.filestore.' + str(filestore) + '.Migratable property supports only [true,false, or leave blank to use default].')
                    else:
                        log.debug('Filestore [' + str(filestore) + '] migratable property [' + str(filestoreMigratable) + '] is valid.')

            location = domainProperties.getProperty('persistent.filestore.' + str(filestore) + '.Location')
            if not location is None and len(location)>0:
                file = File(location)
                if file.isAbsolute():
                    if not file.exists():
                        log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file [' + str(location) + '].')
    return error

def validateJmsServersProperty(domainProperties):
    
    error = 0
    
    jmsservers = domainProperties.getProperty('jmsServers')
    filestores = domainProperties.getProperty('persistent.filestores')
    
    if not jmsservers is None and len(jmsservers)>0:
        jmsserverList = jmsservers.split(',')
        for jmsserver in jmsserverList:
            helper.printHeader('[VALIDATING] JMS Server ' + str(jmsserver) + ' properties')
            
            jmsserverName = domainProperties.getProperty('jmsServer.' + str(jmsserver) + '.Name')
            if jmsserverName is None or len(jmsserverName)==0:
                error = 1
                log.error('Please verify jmsServer.' + str(jmsserver) + '.Name property if it exists in configuration.')
            else:
                log.debug('JMS Server [' + str(jmsserver) + '] name property [' + str(jmsserverName) + '] is valid.')

            jmsserverTarget = domainProperties.getProperty('jmsServer.' + str(jmsserver) + '.Target')
            if not jmsserverTarget is None and len(jmsserverTarget)>0:
                servers = domainProperties.getProperty('wls.servers')
                if not servers is None and len(servers)>0:
                    serverList = servers.split(',')
                    exist = 0

                    for server in serverList:
                        if server==jmsserverTarget:
                            exist = 1
                            break
                    if not exist:
                        error = 1
                        log.error('jmsServer.' + str(jmsserver) + '.Target property refers to a server that does not exist within wls.servers.')
                    else:
                        log.debug('JMS Server [' + str(jmsserver) + '] target property [' + str(jmsserverTarget) + '] is valid.')

            jmsserverPersistStoreType = domainProperties.getProperty('jmsServer.' + str(jmsserver) + '.PersistentStoreType')
            if not jmsserverPersistStoreType is None:
                if jmsserverPersistStoreType.upper()=='FILE':
                    jmsserverPersistStore = domainProperties.getProperty('jmsServer.' + str(jmsserver) + '.PersistentStore')
                    if not filestores is None and len(filestores)>0:
                        filestoreList = filestores.split(',')
                        exist = 0
    
                        for filestore in filestoreList:
                            if filestore==jmsserverPersistStore:
                                exist = 1
                                break
                        if not exist:
                            error = 1
                            log.error('Please verify jmsServer.' + str(jmsserver) + '.PersistentStore property and persistent.filestores if they are configured properly.')
                        else:
                            log.debug('JMS Server [' + str(jmsserver) + '] persistent store property [' + str(jmsserverPersistStoreType) + '] is valid.')
                    else:
                        error = 1
                        log.error('Filestore configuration is missing, please verify jmsServer.' + str(jmsserver) + '.PersistentStoreType property and persistent.filestores if they are configured properly.')
                else:
                    error = 1
                    log.error('The persistent filestore type is likely incorrect, please verify jmsServer.' + str(jmsserver) + '.PersistentStoreType if they are configured properly.')

            jmsserverStoreEnabled = domainProperties.getProperty('jmsServer.' + str(jmsserver) + '.StoreEnabled')
            if not jmsserverStoreEnabled is None and len(jmsserverStoreEnabled)>0:
                if not jmsserverStoreEnabled.upper()=='TRUE' and not jmsserverStoreEnabled.upper()=='FALSE':
                    error = 1
                    log.error('The jmsServer.' + str(jmsserver) + '.StoreEnabled property supports only [true,false, or leave blank to use default].')
                else:
                    log.debug('JMS Server [' + str(jmsserver) + '] store-enabled property [' + str(jmsserverStoreEnabled) + '] is valid.')

    return error


def validateJmsModulesProperty(domainProperties):
    
    error = 0

    jmsModules = domainProperties.getProperty('jmsModules')
    jmsservers = domainProperties.getProperty('jmsServers')
    
    if not jmsModules is None and len(jmsModules)>0:
        jmsModuleList = jmsModules.split(',')
        for jmsModule in jmsModuleList:
            helper.printHeader('[VALIDATING] JMS Module ' + str(jmsModule) + ' properties')
            
            jmsModuleName = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.Name')
            if jmsModuleName is None or len(jmsModuleName)==0:
                error = 1
                log.error('Please verify jmsModule.' + str(jmsModule) + '.Name property if it exists in configuration.')
            else:
                log.debug('JMS Module [' + str(jmsModule) + '] name property [' + str(jmsModuleName) + '] is valid.')
                            
            jmsModuleTargetType = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.TargetType')
            if not jmsModuleTargetType is None and len(jmsModuleTargetType)>0:
                if not jmsModuleTargetType.upper()=='CLUSTER' and not jmsModuleTargetType.upper()=='SERVER':
                    error = 1
                    log.error('The jmsModule.' + str(jmsModule) + '.TargetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                else:
                    log.debug('JMS Module [' + str(jmsModule) + '] target type property [' + str(jmsModuleTargetType) + '] is valid.')
                    
                    jmsModuleTargets = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.Targets')
                    if jmsModuleTargets is None or len(jmsModuleTargets)==0:
                        error = 1
                        log.error('Please verify jmsModule.' + str(jmsModule) + '.Targets property if it exists in configuration.')
                    else:
                        clusters = domainProperties.getProperty('wls.clusters')
                        servers = domainProperties.getProperty('wls.servers')
                        jmsModuleTargetList = jmsModuleTargets.split(',')
                        for jmsModuleTarget in jmsModuleTargetList:
                            if jmsModuleTargetType.upper()=='SERVER':
                                if not servers is None and len(servers)>0:
                                    serverList = servers.split(',')
                                    exist = 0
                                    for server in serverList:
                                        if server==jmsModuleTarget:
                                            exist = 1
                                            break
                                    if not exist:
                                        error = 1
                                        log.error('jmsModule.' + str(jmsModule) + '.Targets refers to server [' + str(jmsModuleTarget) + '] that does not exist within wls.servers.')
                                    else:
                                        log.debug('JMS Module [' + str(jmsModule) + '] target [' + str(jmsModuleTarget) + '] is valid.')
                            else:
                                if jmsModuleTargetType.upper()=='CLUSTER':
                                    if not clusters is None and len(clusters)>0:
                                        clusterList = clusters.split(',')
                                        exist = 0
                                        for cluster in clusterList:
                                            if cluster==jmsModuleTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('jmsModule.' + str(jmsModule) + '.Targets property refers to cluster [' + str(jmsModuleTarget) + '] that does not exist within wls.clusters.')
                                        else:
                                            log.debug('JMS Module [' + str(jmsModule) + '] target [' + str(jmsModuleTarget) + '] is valid.')

            jmsModuleSubDeployments = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployments')
            if not jmsModuleSubDeployments is None and len(jmsModuleSubDeployments)>0:
                jmsModuleSubDeploymentList = jmsModuleSubDeployments.split(',')
                for jmsModuleSubDeployment in jmsModuleSubDeploymentList:
                    helper.printHeader('[VALIDATING] JMS SubDeployment ' + str(jmsModuleSubDeployment) + ' of JMS Module ' + str(jmsModule) + ' properties')
                    
                    jmsModuleSubDeploymentName = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Name')
                    if jmsModuleSubDeploymentName is None or len(jmsModuleSubDeploymentName)==0:
                        error = 1
                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Name property if it exists in configuration.')
                    else:
                        log.debug('JMS SubDeployment [' + str(jmsModuleSubDeployment) + '] name [' + str(jmsModuleSubDeploymentName) + '] is valid.')
                                            
                    jmsModuleSubDeploymentTargetType = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.TargetType')
                    if not jmsModuleSubDeploymentTargetType is None and len(jmsModuleSubDeploymentTargetType)>0:
                        if not jmsModuleSubDeploymentTargetType.upper()=='JMSSERVER' and not jmsModuleSubDeploymentTargetType.upper()=='CLUSTER':
                            error = 1
                            log.error('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.TargetType property is not valid. Valid target types are JMSServer and Cluster')
                        else:
                            log.debug('JMS SubDeployment [' + str(jmsModuleSubDeployment) + '] target type [' + str(jmsModuleSubDeploymentTargetType) + '] is valid.')
                            
                            jmsModuleSubDeploymentTargets = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Targets')
                            if jmsModuleSubDeploymentTargets is None or len(jmsModuleSubDeploymentTargets)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + jmsModule + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Targets property if it exists in configuration.')
                            else:
                                if jmsModuleSubDeploymentTargetType.upper()=='JMSSERVER':
                                    if not jmsservers is None and len(jmsservers)>0:
                                        jmsModuleSubDeploymentTargetList = jmsModuleSubDeploymentTargets.split(',')
                                        for jmsModuleSubDeploymentTarget in jmsModuleSubDeploymentTargetList:
                                            jmsserverList = jmsservers.split(',')
                                            exist = 0
                                            for jmsserver in jmsserverList:
                                                if jmsserver==jmsModuleSubDeploymentTarget:
                                                    exist = 1
                                                    break
                                            if not exist:
                                                error = 1
                                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Targets property at target jms server [' + str(jmsModuleSubDeploymentTarget) + '] and jmsServers property if they are configured properly.')
                                            else:
                                                log.debug('JMS SubDeployment [' + str(jmsModuleSubDeployment) + '] target [' + str(jmsModuleSubDeploymentTarget) + '] is valid.')
                                    else:
                                        error = 1
                                        log.error('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Targets property refers to a JMSServer but the jmsServers property does not exist.')
                                else:
                                    if jmsModuleSubDeploymentTargetType.upper()=='CLUSTER':
                                        clusters = domainProperties.getProperty('wls.clusters')
                                        if not clusters is None and len(clusters)>0:
                                            jmsModuleSubDeploymentTargetList = jmsModuleSubDeploymentTargets.split(',')
                                            for jmsModuleSubDeploymentTarget in jmsModuleSubDeploymentTargetList:
                                                clusterList = clusters.split(',')
                                                exist = 0
                                                for cluster in clusterList:
                                                    if cluster==jmsModuleSubDeploymentTarget:
                                                        exist = 1
                                                        break
                                                if not exist:
                                                    error = 1
                                                    log.error('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Targets property contains cluster [' + str(jmsModuleSubDeploymentTarget) + '] that does not exist within wls.cluster property.')
                                                else:
                                                    log.debug('JMS SubDeployment [' + str(jmsModuleSubDeployment) + '] target [' + str(jmsModuleSubDeploymentTarget) + '] is valid.')
                                        else:
                                            error = 1
                                            log.error('jmsModule.' + str(jmsModule) + '.Targets property is targeted to a cluster but no clusters are defined in wls.clusters property.')

                    jmsModuleSubDeploymentConnectionFactories = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactories')
                    if not jmsModuleSubDeploymentConnectionFactories is None and len(jmsModuleSubDeploymentConnectionFactories)>0:
                        jmsModuleSubDeploymentConnectionFactoryList = jmsModuleSubDeploymentConnectionFactories.split(',')
                        for jmsModuleSubDeploymentConnectionFactory in jmsModuleSubDeploymentConnectionFactoryList:
                            jmsConnectionFactoryName = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.Name')
                            if jmsConnectionFactoryName is None or len(jmsConnectionFactoryName)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.Name property if it exists in configuration.')
                            else:
                                log.debug('Connection factory [' + str(jmsModuleSubDeploymentConnectionFactory) + '] name property [' + str(jmsConnectionFactoryName) + '] is valid.')

                            jmsConnectionFactoryJNDI = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.JNDI')
                            if jmsConnectionFactoryJNDI is None or len(jmsConnectionFactoryJNDI)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.JNDI property if it exists in configuration.')
                            else:
                                log.debug('Connection factory [' + str(jmsModuleSubDeploymentConnectionFactory) + '] JNDI property [' + str(jmsConnectionFactoryJNDI) + '] is valid.')

                            jmsConnectionFactoryReconnectPolicy = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.ReconnectPolicy')
                            if not jmsConnectionFactoryReconnectPolicy is None and len(jmsConnectionFactoryReconnectPolicy)>0:
                                if not jmsConnectionFactoryReconnectPolicy=='all' and not jmsConnectionFactoryReconnectPolicy=='producer' and not jmsConnectionFactoryReconnectPolicy=='all':
                                    error = 1
                                    log.error('The jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.ReconnectPolicy property supports only [all,producer,none].')
                                else:
                                    log.debug('Connection factory [' + str(jmsModuleSubDeploymentConnectionFactory) + '] reconnection policy property [' + str(jmsConnectionFactoryReconnectPolicy) + '] is valid.')


                            jmsConnectionFactoryServerAffinityEnabled = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.ServerAffinityEnabled')
                            if not jmsConnectionFactoryServerAffinityEnabled is None and len(jmsConnectionFactoryServerAffinityEnabled)>0:
                                if not jmsConnectionFactoryServerAffinityEnabled.upper()=='TRUE' and not jmsConnectionFactoryServerAffinityEnabled.upper()=='FALSE':
                                    error = 1
                                    log.error('The jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.ServerAffinityEnabled property supports only [true,false, or leave blank to use default].')
                                else:
                                    log.debug('Connection factory [' + str(jmsModuleSubDeploymentConnectionFactory) + '] server affinity enabled property [' + str(jmsConnectionFactoryServerAffinityEnabled) + '] is valid.')

                            jmsConnectionFactoryDefaultDeliveryMode = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.DefaultDeliveryMode')
                            if not jmsConnectionFactoryDefaultDeliveryMode is None and len(jmsConnectionFactoryDefaultDeliveryMode)>0:
                                if not jmsConnectionFactoryDefaultDeliveryMode=='Persistent' and not jmsConnectionFactoryDefaultDeliveryMode=='Non-persistent':
                                    error = 1
                                    log.error('The jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.ConnectionFactory.' + str(jmsModuleSubDeploymentConnectionFactory) + '.DefaultDeliveryMode property supports only [Persistent,Non-persistent, or leave blank to use default].')
                                else:
                                    log.debug('Connection factory [' + str(jmsModuleSubDeploymentConnectionFactory) + '] default delivery mode property [' + str(jmsConnectionFactoryDefaultDeliveryMode) + '] is valid.')

                    jmsModuleSubDeploymentQueues = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Queues')
                    if not jmsModuleSubDeploymentQueues is None and len(jmsModuleSubDeploymentQueues)>0:
                        jmsModuleSubDeploymentQueueList = jmsModuleSubDeploymentQueues.split(',')
                        for jmsModuleSubDeploymentQueue in jmsModuleSubDeploymentQueueList:
                            jmsQueueName = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Queue.' + str(jmsModuleSubDeploymentQueue) + '.Name')
                            if jmsQueueName is None or len(jmsQueueName)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Queue.' + str(jmsModuleSubDeploymentQueue) + '.Name property if it exists in configuration.')
                            else:
                                log.debug('Queue [' + str(jmsModuleSubDeploymentQueue) + '] name property [' + str(jmsQueueName) + '] is valid.')

                            jmsQueueJNDI = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Queue.' + str(jmsModuleSubDeploymentQueue) + '.JNDI')
                            if jmsQueueJNDI is None or len(jmsQueueJNDI)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Queue.' + str(jmsModuleSubDeploymentQueue) + '.JNDI property if it exists in configuration.')
                            else:
                                log.debug('Queue [' + str(jmsModuleSubDeploymentQueue) + '] JNDI property [' + str(jmsQueueJNDI) + '] is valid.')

                    jmsModuleSubDeploymentUniQueues = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueues')
                    if not jmsModuleSubDeploymentUniQueues is None and len(jmsModuleSubDeploymentUniQueues)>0:
                        jmsModuleSubDeploymentUniQueueList = jmsModuleSubDeploymentUniQueues.split(',')
                        for jmsModuleSubDeploymentUniQueue in jmsModuleSubDeploymentUniQueueList:
                            jmsUniQueueName = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.Name')
                            if jmsUniQueueName is None or len(jmsUniQueueName)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.Name property if it exists in configuration.')
                            else:
                                log.debug('Uniform Distributed Queue [' + str(jmsModuleSubDeploymentUniQueue) + '] name property [' + str(jmsUniQueueName) + '] is valid.')
                                
                            jmsUniQueueJNDI = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.JNDI')
                            if jmsUniQueueJNDI is None or len(jmsUniQueueJNDI)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.JNDI property if it exists in configuration.')
                            else:
                                log.debug('Uniform Distributed Queue [' + str(jmsModuleSubDeploymentUniQueue) + '] JNDI property [' + str(jmsUniQueueJNDI) + '] is valid.')

                            jmsUniQueueLBPolicy = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.LoadBalancingPolicy')
                            if not jmsUniQueueLBPolicy is None and len(jmsUniQueueLBPolicy)>0:
                                if not jmsUniQueueLBPolicy=='Round-Robin' and not jmsUniQueueLBPolicy=='Random':
                                    error = 1
                                    log.error('The jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.LoadBalancingPolicy property supports only [Round-Robin,Random].')
                                else:
                                    log.debug('Uniform Distributed Queue [' + str(jmsModuleSubDeploymentUniQueue) + '] load balacing policy property [' + str(jmsUniQueueLBPolicy) + '] is valid.')

                            jmsUniQueueFwdDelay = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.ForwardDelay')
                            if not jmsUniQueueFwdDelay is None and len(jmsUniQueueFwdDelay)>0:
                                try:
                                    int(jmsUniQueueFwdDelay)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.ForwardDelay [' + str(jmsUniQueueFwdDelay) + '] property.')
                                else:
                                    if int(jmsUniQueueFwdDelay)<-1:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.ForwardDelay [' + str(jmsUniQueueFwdDelay) + '] property, number is not in valid range [>=-1].')
                                    else:
                                        log.debug('Uniform Distributed Queue [' + str(jmsModuleSubDeploymentUniQueue) + '] forward delay [' + str(jmsUniQueueFwdDelay) + '] is valid.')

                            jmsUniQueueMaximumMessageSize = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.MaximumMessageSize')
                            if not jmsUniQueueMaximumMessageSize is None and len(jmsUniQueueMaximumMessageSize)>0:
                                try:
                                    int(jmsUniQueueMaximumMessageSize)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.MaximumMessageSize [' + str(jmsUniQueueMaximumMessageSize) + '] property.')
                                else:
                                    if int(jmsUniQueueMaximumMessageSize)<0 or int(jmsUniQueueMaximumMessageSize)>2147483647:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.MaximumMessageSize [' + str(jmsUniQueueMaximumMessageSize) + '] property, number is not in valid range [0-2147483647].')
                                    else:
                                        log.debug('Uniform Distributed Queue [' + str(jmsModuleSubDeploymentUniQueue) + '] max-message-size [' + str(jmsUniQueueMaximumMessageSize) + '] is valid.')

                            jmsUniQueueMsgPerfPref = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.MessagingPerformancePreference')
                            if not jmsUniQueueMsgPerfPref is None and len(jmsUniQueueMsgPerfPref)>0:
                                try:
                                    int(jmsUniQueueMsgPerfPref)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.MessagingPerformancePreference [' + str(jmsUniQueueMsgPerfPref) + '] property.')
                                else:
                                    if int(jmsUniQueueMsgPerfPref)<0 or int(jmsUniQueueMsgPerfPref)>100:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.MessagingPerformancePreference [' + str(jmsUniQueueMsgPerfPref) + '] property, number is not in valid range [0-100].')
                                    else:
                                        log.debug('Uniform Distributed Queue [' + str(jmsModuleSubDeploymentUniQueue) + '] message-performance-preference [' + str(jmsUniQueueMsgPerfPref) + '] is valid.')

                            jmsUniQueueIncompleteWorkExpTime = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.IncompleteWorkExpirationTime')
                            if not jmsUniQueueIncompleteWorkExpTime is None and len(jmsUniQueueIncompleteWorkExpTime)>0:
                                try:
                                    int(jmsUniQueueIncompleteWorkExpTime)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.IncompleteWorkExpirationTime [' + str(jmsUniQueueIncompleteWorkExpTime) + '] property.')
                                else:
                                    if int(jmsUniQueueIncompleteWorkExpTime)<-1:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedQueue.' + str(jmsModuleSubDeploymentUniQueue) + '.IncompleteWorkExpirationTime [' + str(jmsUniQueueIncompleteWorkExpTime) + '] property, number is not in valid range [>=-1].')
                                    else:
                                        log.debug('Uniform Distributed Queue [' + str(jmsModuleSubDeploymentUniQueue) + '] incomplete-work-expiration-time [' + str(jmsUniQueueIncompleteWorkExpTime) + '] is valid.')

                    jmsModuleSubDeploymentTopics = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Topics')
                    if not jmsModuleSubDeploymentTopics is None and len(jmsModuleSubDeploymentTopics)>0:
                        jmsModuleSubDeploymentTopicList = jmsModuleSubDeploymentTopics.split(',')
                        for jmsModuleSubDeploymentTopic in jmsModuleSubDeploymentTopicList:
                            jmsTopicName = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Topic.' + str(jmsModuleSubDeploymentTopic) + '.Name')
                            if jmsTopicName is None or len(jmsTopicName)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Topic.' + str(jmsModuleSubDeploymentTopic) + '.Name property if it exists in configuration.')
                            else:
                                log.debug('Topic [' + str(jmsModuleSubDeploymentTopic) + '] name property [' + str(jmsTopicName) + '] is valid.')

                            jmsTopicJNDI = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Topic.' + str(jmsModuleSubDeploymentTopic) + '.JNDI')
                            if jmsTopicJNDI is None or len(jmsTopicJNDI)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.Topic.' + str(jmsModuleSubDeploymentTopic) + '.JNDI property if it exists in configuration.')
                            else:
                                log.debug('Topic [' + str(jmsModuleSubDeploymentTopic) + '] JNDI property [' + str(jmsTopicJNDI) + '] is valid.')
                                
                    jmsModuleSubDeploymentUniTopics = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopics')
                    if not jmsModuleSubDeploymentUniTopics is None and len(jmsModuleSubDeploymentUniTopics)>0:
                        jmsModuleSubDeploymentUniTopicList = jmsModuleSubDeploymentUniTopics.split(',')
                        for jmsModuleSubDeploymentUniTopic in jmsModuleSubDeploymentUniTopicList:
                            jmsUniTopicName = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.Name')
                            if jmsUniTopicName is None or len(jmsUniTopicName)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.Name property if it exists in configuration.')
                            else:
                                log.debug('Uniform Distributed Topic [' + str(jmsModuleSubDeploymentUniTopic) + '] name property [' + str(jmsUniTopicName) + '] is valid.')

                            jmsUniTopicJNDI = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.JNDI')
                            if jmsUniTopicJNDI is None or len(jmsUniTopicJNDI)==0:
                                error = 1
                                log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.JNDI property if it exists in configuration.')
                            else:
                                log.debug('Uniform Distributed Topic [' + str(jmsModuleSubDeploymentUniTopic) + '] JNDI property [' + str(jmsUniTopicJNDI) + '] is valid.')

                            jmsUniTopicLBPolicy = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.LoadBalancingPolicy')
                            if not jmsUniTopicLBPolicy is None and len(jmsUniTopicLBPolicy)>0:
                                if not jmsUniTopicLBPolicy=='Round-Robin' and not jmsUniTopicLBPolicy=='Random':
                                    error = 1
                                    log.error('The jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.LoadBalancingPolicy property supports only [Round-Robin,Random].')
                                else:
                                    log.debug('Uniform Distributed Topic [' + str(jmsModuleSubDeploymentUniTopic) + '] load balancing policy property [' + str(jmsUniTopicLBPolicy) + '] is valid.')

                            jmsUniTopicFwdDelay = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.ForwardDelay')
                            if not jmsUniTopicFwdDelay is None and len(jmsUniTopicFwdDelay)>0:
                                try:
                                    int(jmsUniTopicFwdDelay)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.ForwardDelay [' + str(jmsUniTopicFwdDelay) + '] property.')
                                else:
                                    if int(jmsUniTopicFwdDelay)<-1:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.ForwardDelay [' + str(jmsUniTopicFwdDelay) + '] property, number is not in valid range [>=-1].')
                                    else:
                                        log.debug('Uniform Distributed Topic [' + str(jmsModuleSubDeploymentUniTopic) + '] forward delay [' + str(jmsUniTopicFwdDelay) + '] is valid.')

                            jmsUniTopicMaximumMessageSize = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.MaximumMessageSize')
                            if not jmsUniTopicMaximumMessageSize is None and len(jmsUniTopicMaximumMessageSize)>0:
                                try:
                                    int(jmsUniTopicMaximumMessageSize)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.MaximumMessageSize [' + str(jmsUniTopicMaximumMessageSize) + '] property.')
                                else:
                                    if int(jmsUniTopicMaximumMessageSize)<0 or int(jmsUniTopicMaximumMessageSize)>2147483647:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.MaximumMessageSize [' + str(jmsUniTopicMaximumMessageSize) + '] property, number is not in valid range [0-2147483647].')
                                    else:
                                        log.debug('Uniform Distributed Topic [' + str(jmsModuleSubDeploymentUniTopic) + '] max-message-size [' + str(jmsUniTopicMaximumMessageSize) + '] is valid.')

                            jmsUniTopicMsgPerfPref = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.MessagingPerformancePreference')
                            if not jmsUniTopicMsgPerfPref is None and len(jmsUniTopicMsgPerfPref)>0:
                                try:
                                    int(jmsUniTopicMsgPerfPref)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.MessagingPerformancePreference [' + str(jmsUniTopicMsgPerfPref) + '] property.')
                                else:
                                    if int(jmsUniTopicMsgPerfPref)<0 or int(jmsUniTopicMsgPerfPref)>100:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.MessagingPerformancePreference [' + str(jmsUniTopicMsgPerfPref) + '] property, number is not in valid range [0-100].')
                                    else:
                                        log.debug('Uniform Distributed Topic [' + str(jmsModuleSubDeploymentUniTopic) + '] message-performance-preference [' + str(jmsUniTopicMsgPerfPref) + '] is valid.')

                            jmsUniTopicIncompleteWorkExpTime = domainProperties.getProperty('jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.IncompleteWorkExpirationTime')
                            if not jmsUniTopicIncompleteWorkExpTime is None and len(jmsUniTopicIncompleteWorkExpTime)>0:
                                try:
                                    int(jmsUniTopicIncompleteWorkExpTime)
                                except ValueError:
                                    log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.IncompleteWorkExpirationTime [' + str(jmsUniTopicIncompleteWorkExpTime) + '] property.')
                                else:
                                    if int(jmsUniTopicIncompleteWorkExpTime)<-1:
                                        log.error('Please verify jmsModule.' + str(jmsModule) + '.SubDeployment.' + str(jmsModuleSubDeployment) + '.UniformDistributedTopic.' + str(jmsModuleSubDeploymentUniTopic) + '.IncompleteWorkExpirationTime [' + str(jmsUniTopicIncompleteWorkExpTime) + '] property, number is not in valid range [>=-1].')
                                    else:
                                        log.debug('Uniform Distributed Topic [' + str(jmsModuleSubDeploymentUniTopic) + '] incomplete-work-expiration-time [' + str(jmsUniTopicIncompleteWorkExpTime) + '] is valid.')

    return error