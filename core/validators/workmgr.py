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
    if validateWorkManagerProperty(config):
        return False
    return True

def validateWorkManagerProperty(domainProperties):

    error = 0
    
    workManagers = domainProperties.getProperty('wls.workManagers')
    if not workManagers is None and len(workManagers)>0:
        workManagerList = workManagers.split(',')
        for workManager in workManagerList:
            helper.printHeader('[VALIDATING] workmanager ' + str(workManager) + ' properties')
            
            workManagerName = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.name')
            if workManagerName is None or len(workManagerName)==0:
                error = 1
                log.error('Please verify wls.workManager.' + str(workManager) + '.name property if it exists in configuration.')
            else:
                log.debug('Workmanager [' + str(workManager) + '] name property [' + str(workManagerName) + '] is valid.')

            workManagerTargetType = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.targetType')
            if not workManagerTargetType is None and len(workManagerTargetType)>0:
                if not workManagerTargetType.upper()=='CLUSTER' and not workManagerTargetType.upper()=='SERVER':
                    error = 1
                    log.error('The wls.workManager.' + str(workManager) + '.targetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                else:
                    log.debug('Workmanager [' + str(workManager) + '] target type property [' + str(workManagerTargetType) + '] is valid.')
                    
                    workManagerTargets = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.targets')
                    if workManagerTargets is None or len(workManagerTargets)==0:
                        error = 1
                        log.error('Please verify wls.workManager.' + str(workManager) + '.targets property if it exists in configuration.')
                    else:
                        clusters = domainProperties.getProperty('wls.clusters')
                        servers = domainProperties.getProperty('wls.servers')
                        workManagerTargetList = workManagerTargets.split(',')
                        for workManagerTarget in workManagerTargetList:
                            if workManagerTargetType.upper()=='SERVER':
                                if not servers is None and len(servers)>0:
                                    serverList = servers.split(',')
                                    exist = 0
                                    for server in serverList:
                                        if server==workManagerTarget:
                                            exist = 1
                                            break
                                    if not exist:
                                        error = 1
                                        log.error('Please verify wls.workManager.' + str(workManager) + '.targets property at server [' + str(workManagerTarget) + '] and wls.servers if they are configured properly.')
                                    else:
                                        log.debug('Workmanager [' + str(workManager) + '] target [' + str(workManagerTarget) + '] is valid.')
                            else:
                                if workManagerTargetType.upper()=='CLUSTER':
                                    if not clusters is None and len(clusters)>0:
                                        clusterList = clusters.split(',')
                                        exist = 0
                                        for cluster in clusterList:
                                            if cluster==workManagerTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('Please verify wls.workManager.' + str(workManager) + '.targets property at cluster [' + str(workManagerTarget) + '] and wls.clusters if they are configured properly.')
                                        else:
                                            log.debug('Workmanager [' + str(workManager) + '] target [' + str(workManagerTarget) + '] is valid.')

            minThreadsConstraintName = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.name')
            if not minThreadsConstraintName is None and len(minThreadsConstraintName)>0:
                log.debug('Workmanager [' + str(workManager) + '] min-thread constraint name property [' + str(minThreadsConstraintName) + '] is valid.')
                
                minThreadsConstraintCount = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.count')
                if not minThreadsConstraintCount is None and len(minThreadsConstraintCount)>0:
                    try:
                        int(minThreadsConstraintCount)
                    except ValueError:
                        log.error('Please verify wls.workManager.' + str(workManager) + '.minThreadsConstraint.count [' + str(minThreadsConstraintCount) + '] property.')
                    else:
                        if int(minThreadsConstraintCount)<0 or int(minThreadsConstraintCount)>65535:
                            log.error('Please verify wls.workManager.' + str(workManager) + '.minThreadsConstraint.count [' + str(minThreadsConstraintCount) + '] property, the number is not in valid range [0-65535].')
                        else:
                            log.debug('Workmanager [' + str(workManager) + '] min-thread constraint count property [' + str(minThreadsConstraintCount) + '] is valid.')
                    
                constraintTargetType = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.targetType')
                if not constraintTargetType is None and len(constraintTargetType)>0:
                    if not constraintTargetType.upper()=='CLUSTER' and not constraintTargetType.upper()=='SERVER':
                        error = 1
                        log.error('The wls.workManager.' + str(workManager) + '.minThreadsConstraint.targetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                    else:
                        log.debug('Workmanager [' + str(workManager) + '] min-thread constraint target type property [' + str(constraintTargetType) + '] is valid.')
                        
                        constraintTargets = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.targets')
                        if constraintTargets is None or len(constraintTargets)==0:
                            error = 1
                            log.error('Please verify wls.workManager.' + str(workManager) + '.minThreadsConstraint.targets property if it exists in configuration.')
                        else:
                            clusters = domainProperties.getProperty('wls.clusters')
                            servers = domainProperties.getProperty('wls.servers')
                            constraintTargetList = constraintTargets.split(',')
                            for constraintTarget in constraintTargetList:
                                if constraintTargetType.upper()=='SERVER':
                                    if not servers is None and len(servers)>0:
                                        serverList = servers.split(',')
                                        exist = 0
                                        for server in serverList:
                                            if server==constraintTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('Please verify wls.workManager.' + str(workManager) + '.minThreadsConstraint.targets property at server [' + str(constraintTarget) + '] and wls.servers if they are configured properly.')
                                        else:
                                            log.debug('Workmanager [' + str(workManager) + '] min-thread constraint target [' + str(constraintTarget) + '] is valid.')
                                else:
                                    if constraintTargetType.upper()=='CLUSTER':
                                        if not clusters is None and len(clusters)>0:
                                            clusterList = clusters.split(',')
                                            exist = 0
                                            for cluster in clusterList:
                                                if cluster==constraintTarget:
                                                    exist = 1
                                                    break
                                            if not exist:
                                                error = 1
                                                log.error('Please verify wls.workManager.' + str(workManager) + '.minThreadsConstraint.targets property at cluster [' + str(constraintTarget) + '] and wls.clusters if they are configured properly.')
                                            else:
                                                log.debug('Workmanager [' + str(workManager) + '] min-thread constraint target [' + str(constraintTarget) + '] is valid.')

            maxThreadsConstraintName = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.name')
            if not maxThreadsConstraintName is None and len(maxThreadsConstraintName)>0:
                log.debug('Workmanager [' + str(workManager) + '] max-thread constraint name property [' + str(maxThreadsConstraintName) + '] is valid.')
                
                maxThreadsConstraintCount = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.count')
                if not maxThreadsConstraintCount is None and len(maxThreadsConstraintCount)>0:
                    try:
                        int(maxThreadsConstraintCount)
                    except ValueError:
                        log.error('Please verify wls.workManager.' + str(workManager) + '.maxThreadsConstraint.count [' + str(maxThreadsConstraintCount) + '] property.')
                    else:
                        if int(maxThreadsConstraintCount)<0 or int(maxThreadsConstraintCount)>65535:
                            log.error('Please verify wls.workManager.' + str(workManager) + '.maxThreadsConstraint.count [' + str(maxThreadsConstraintCount) + '] property, the number is not in valid range [0-65535].')
                        else:
                            log.debug('Workmanager [' + str(workManager) + '] max-thread constraint count property [' + str(maxThreadsConstraintCount) + '] is valid.')
                    
                constraintTargetType = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targetType')
                if not constraintTargetType is None and len(constraintTargetType)>0:
                    if not constraintTargetType.upper()=='CLUSTER' and not constraintTargetType.upper()=='SERVER':
                        error = 1
                        log.error('The wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                    else:
                        log.debug('Workmanager [' + str(workManager) + '] max-thread constraint target type property [' + str(constraintTargetType) + '] is valid.')
                        
                        constraintTargets = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targets')
                        if constraintTargets is None or len(constraintTargets)==0:
                            error = 1
                            log.error('Please verify wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targets property if it exists in configuration.')
                        else:
                            clusters = domainProperties.getProperty('wls.clusters')
                            servers = domainProperties.getProperty('wls.servers')
                            constraintTargetList = constraintTargets.split(',')
                            for constraintTarget in constraintTargetList:
                                if constraintTargetType.upper()=='SERVER':
                                    if not servers is None and len(servers)>0:
                                        serverList = servers.split(',')
                                        exist = 0
                                        for server in serverList:
                                            if server==constraintTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('Please verify wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targets property at server [' + str(constraintTarget) + '] and wls.servers if they are configured properly.')
                                        else:
                                            log.debug('Workmanager [' + str(workManager) + '] max-thread constraint target [' + str(constraintTarget) + '] is valid.')
                                else:
                                    if constraintTargetType.upper()=='CLUSTER':
                                        if not clusters is None and len(clusters)>0:
                                            clusterList = clusters.split(',')
                                            exist = 0
                                            for cluster in clusterList:
                                                if cluster==constraintTarget:
                                                    exist = 1
                                                    break
                                            if not exist:
                                                error = 1
                                                log.error('Please verify wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targets property at cluster [' + str(constraintTarget) + '] and wls.clusters if they are configured properly.')
                                            else:
                                                log.debug('Workmanager [' + str(workManager) + '] max-thread constraint target [' + str(constraintTarget) + '] is valid.')

            classCount=0
            fairShareRequestClassName = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.name')
            if not fairShareRequestClassName is None and len(fairShareRequestClassName)>0:
                log.debug('Workmanager [' + str(workManager) + '] fairshare constraint name property [' + str(fairShareRequestClassName) + '] is valid.')
                classCount=classCount+1
                
                fairShareRequestClassFairShare = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.fairShare')
                if not fairShareRequestClassFairShare is None and len(fairShareRequestClassFairShare)>0:
                    try:
                        int(fairShareRequestClassFairShare)
                    except ValueError:
                        log.error('Please verify wls.workManager.' + str(workManager) + '.fairShareRequestClass.fairShare [' + str(fairShareRequestClassFairShare) + '] property.')
                    else:
                        if int(fairShareRequestClassFairShare)<1 or int(fairShareRequestClassFairShare)>1000:
                            log.error('Please verify wls.workManager.' + str(workManager) + '.fairShareRequestClass.fairShare [' + str(fairShareRequestClassFairShare) + '] property, the number is not in valid range [1-1000].')
                        else:
                            log.debug('Workmanager [' + str(workManager) + '] fairshare constraint property [' + str(fairShareRequestClassFairShare) + '] is valid.')
                    
                constraintTargetType = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.targetType')
                if not constraintTargetType is None and len(constraintTargetType)>0:
                    if not constraintTargetType.upper()=='CLUSTER' and not constraintTargetType.upper()=='SERVER':
                        error = 1
                        log.error('The wls.workManager.' + str(workManager) + '.fairShareRequestClass.targetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                    else:
                        log.debug('Workmanager [' + str(workManager) + '] fairshare constraint target type property [' + str(constraintTargetType) + '] is valid.')
                        
                        constraintTargets = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.targets')
                        if constraintTargets is None or len(constraintTargets)==0:
                            error = 1
                            log.error('Please verify wls.workManager.' + str(workManager) + '.fairShareRequestClass.targets property if it exists in configuration.')
                        else:
                            clusters = domainProperties.getProperty('wls.clusters')
                            servers = domainProperties.getProperty('wls.servers')
                            constraintTargetList = constraintTargets.split(',')
                            for constraintTarget in constraintTargetList:
                                if constraintTargetType.upper()=='SERVER':
                                    if not servers is None and len(servers)>0:
                                        serverList = servers.split(',')
                                        exist = 0
                                        for server in serverList:
                                            if server==constraintTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('Please verify wls.workManager.' + str(workManager) + '.fairShareRequestClass.targets property at server [' + str(constraintTarget) + '] and wls.servers if they are configured properly.')
                                        else:
                                            log.debug('Workmanager [' + str(workManager) + '] fairshare constraint target [' + str(constraintTarget) + '] is valid.')
                                else:
                                    if constraintTargetType.upper()=='CLUSTER':
                                        if not clusters is None and len(clusters)>0:
                                            clusterList = clusters.split(',')
                                            exist = 0
                                            for cluster in clusterList:
                                                if cluster==constraintTarget:
                                                    exist = 1
                                                    break
                                            if not exist:
                                                error = 1
                                                log.error('Please verify wls.workManager.' + str(workManager) + '.fairShareRequestClass.targets property at cluster [' + str(constraintTarget) + '] and wls.clusters if they are configured properly.')
                                            else:
                                                log.debug('Workmanager [' + str(workManager) + '] fairshare constraint target [' + str(constraintTarget) + '] is valid.')

            responseTimeRequestClassName = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.responseTimeRequestClass.name')
            if not responseTimeRequestClassName is None and len(responseTimeRequestClassName)>0:
                log.debug('Workmanager [' + str(workManager) + '] response-time constraint name property [' + str(responseTimeRequestClassName) + '] is valid.')
                classCount=classCount+1
                
                responseTimeRequestClassGoal = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.fairShare')
                if not responseTimeRequestClassGoal is None and len(responseTimeRequestClassGoal)>0:
                    try:
                        int(responseTimeRequestClassGoal)
                    except ValueError:
                        log.error('Please verify wls.workManager.' + str(workManager) + '.responseTimeRequestClass.goalMs [' + str(responseTimeRequestClassGoal) + '] property.')
                    else:
                        if int(responseTimeRequestClassGoal)<0 or int(responseTimeRequestClassGoal)>65535:
                            log.error('Please verify wls.workManager.' + str(workManager) + '.responseTimeRequestClass.goalMs [' + str(responseTimeRequestClassGoal) + '] property, the number is not in valid range [0-65535].')
                        else:
                            log.debug('Workmanager [' + str(workManager) + '] response-time constraint goal property [' + str(responseTimeRequestClassGoal) + '] is valid.')
                    
                constraintTargetType = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targetType')
                if not constraintTargetType is None and len(constraintTargetType)>0:
                    if not constraintTargetType.upper()=='CLUSTER' and not constraintTargetType.upper()=='SERVER':
                        error = 1
                        log.error('The wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                    else:
                        log.debug('Workmanager [' + str(workManager) + '] response-time constraint target type property [' + str(constraintTargetType) + '] is valid.')
                        
                        constraintTargets = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targets')
                        if constraintTargets is None or len(constraintTargets)==0:
                            error = 1
                            log.error('Please verify wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targets property if it exists in configuration.')
                        else:
                            clusters = domainProperties.getProperty('wls.clusters')
                            servers = domainProperties.getProperty('wls.servers')
                            constraintTargetList = constraintTargets.split(',')
                            for constraintTarget in constraintTargetList:
                                if constraintTargetType.upper()=='SERVER':
                                    if not servers is None and len(servers)>0:
                                        serverList = servers.split(',')
                                        exist = 0
                                        for server in serverList:
                                            if server==constraintTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('Please verify wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targets property at server [' + str(constraintTarget) + '] and wls.servers if they are configured properly.')
                                        else:
                                            log.debug('Workmanager [' + str(workManager) + '] response-time constraint target [' + str(constraintTarget) + '] is valid.')
                                else:
                                    if constraintTargetType.upper()=='CLUSTER':
                                        if not clusters is None and len(clusters)>0:
                                            clusterList = clusters.split(',')
                                            exist = 0
                                            for cluster in clusterList:
                                                if cluster==constraintTarget:
                                                    exist = 1
                                                    break
                                            if not exist:
                                                error = 1
                                                log.error('Please verify wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targets property at cluster [' + str(constraintTarget) + '] and wls.clusters if they are configured properly.')
                                            else:
                                                log.debug('Workmanager [' + str(workManager) + '] response-time constraint target [' + str(constraintTarget) + '] is valid.')

            contextRequestClassName = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.contextRequestClass.name')
            if not contextRequestClassName is None and len(contextRequestClassName)>0:
                log.debug('Workmanager [' + str(workManager) + '] context-request constraint name property [' + str(contextRequestClassName) + '] is valid.')
                classCount=classCount+1
                
                constraintTargetType = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.contextRequestClass.targetType')
                if not constraintTargetType is None and len(constraintTargetType)>0:
                    if not constraintTargetType.upper()=='CLUSTER' and not constraintTargetType.upper()=='SERVER':
                        error = 1
                        log.error('The wls.workManager.' + str(workManager) + '.contextRequestClass.targetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                    else:
                        log.debug('Workmanager [' + str(workManager) + '] context-request constraint target type property [' + str(constraintTargetType) + '] is valid.')
                        
                        constraintTargets = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.contextRequestClass.targets')
                        if constraintTargets is None or len(constraintTargets)==0:
                            error = 1
                            log.error('Please verify wls.workManager.' + str(workManager) + '.contextRequestClass.targets property if it exists in configuration.')
                        else:
                            clusters = domainProperties.getProperty('wls.clusters')
                            servers = domainProperties.getProperty('wls.servers')
                            constraintTargetList = constraintTargets.split(',')
                            for constraintTarget in constraintTargetList:
                                if constraintTargetType.upper()=='SERVER':
                                    if not servers is None and len(servers)>0:
                                        serverList = servers.split(',')
                                        exist = 0
                                        for server in serverList:
                                            if server==constraintTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('Please verify wls.workManager.' + str(workManager) + '.contextRequestClass.targets property at server [' + str(constraintTarget) + '] and wls.servers if they are configured properly.')
                                        else:
                                            log.debug('Workmanager [' + str(workManager) + '] context-request constraint target [' + str(constraintTarget) + '] is valid.')
                                else:
                                    if constraintTargetType.upper()=='CLUSTER':
                                        if not clusters is None and len(clusters)>0:
                                            clusterList = clusters.split(',')
                                            exist = 0
                                            for cluster in clusterList:
                                                if cluster==constraintTarget:
                                                    exist = 1
                                                    break
                                            if not exist:
                                                error = 1
                                                log.error('Please verify wls.workManager.' + str(workManager) + '.contextRequestClass.targets property at cluster [' + str(constraintTarget) + '] and wls.clusters if they are configured properly.')
                                            else:
                                                log.debug('Workmanager [' + str(workManager) + '] context-request constraint target [' + str(constraintTarget) + '] is valid.')
            
            if classCount>1:
                log.error('Please verify wls.workManager.' + str(workManager) + '.fairShareRequestClass.name and wls.workManager.' + str(workManager) + '.responseTimeRequestClass.name and wls.workManager.' + str(workManager) + '.contextRequestClass.name in configuration. If more than one exist, please select only one of them and comment out the rest.')

            capacityConstraintName = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.name')
            if not capacityConstraintName is None and len(capacityConstraintName)>0:
                log.debug('Workmanager [' + str(workManager) + '] capacity constraint name property [' + str(capacityConstraintName) + '] is valid.')
                
                capacityConstraintCount = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.count')
                if not capacityConstraintCount is None and len(capacityConstraintCount)>0:
                    try:
                        int(capacityConstraintCount)
                    except ValueError:
                        log.error('Please verify wls.workManager.' + str(workManager) + '.capacityConstraint.count [' + str(capacityConstraintCount) + '] property.')
                    else:
                        if int(capacityConstraintCount)<0 or int(capacityConstraintCount)>65535:
                            log.error('Please verify wls.workManager.' + str(workManager) + '.capacityConstraint.count [' + str(capacityConstraintCount) + '] property, the number is not in valid range [0-65535].')
                        else:
                            log.debug('Workmanager [' + str(workManager) + '] capacity constraint count property [' + str(capacityConstraintCount) + '] is valid.')
                    
                constraintTargetType = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.targetType')
                if not constraintTargetType is None and len(constraintTargetType)>0:
                    if not constraintTargetType.upper()=='CLUSTER' and not constraintTargetType.upper()=='SERVER':
                        error = 1
                        log.error('The wls.workManager.' + str(workManager) + '.capacityConstraint.targetType property supports only [Cluster,Server, or leave blank to target to AdminServer].')
                    else:
                        log.debug('Workmanager [' + str(workManager) + '] capacity constraint target type property [' + str(constraintTargetType) + '] is valid.')
                        
                        constraintTargets = domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.targets')
                        if constraintTargets is None or len(constraintTargets)==0:
                            error = 1
                            log.error('Please verify wls.workManager.' + str(workManager) + '.capacityConstraint.targets property if it exists in configuration.')
                        else:
                            clusters = domainProperties.getProperty('wls.clusters')
                            servers = domainProperties.getProperty('wls.servers')
                            constraintTargetList = constraintTargets.split(',')
                            for constraintTarget in constraintTargetList:
                                if constraintTargetType.upper()=='SERVER':
                                    if not servers is None and len(servers)>0:
                                        serverList = servers.split(',')
                                        exist = 0
                                        for server in serverList:
                                            if server==constraintTarget:
                                                exist = 1
                                                break
                                        if not exist:
                                            error = 1
                                            log.error('Please verify wls.workManager.' + str(workManager) + '.capacityConstraint.targets property at server [' + str(constraintTarget) + '] and wls.servers if they are configured properly.')
                                        else:
                                            log.debug('Workmanager [' + str(workManager) + '] capacity constraint target [' + str(constraintTarget) + '] is valid.')
                                else:
                                    if constraintTargetType.upper()=='CLUSTER':
                                        if not clusters is None and len(clusters)>0:
                                            clusterList = clusters.split(',')
                                            exist = 0
                                            for cluster in clusterList:
                                                if cluster==constraintTarget:
                                                    exist = 1
                                                    break
                                            if not exist:
                                                error = 1
                                                log.error('Please verify wls.workManager.' + str(workManager) + '.capacityConstraint.targets property at cluster [' + str(constraintTarget) + '] and wls.clusters if they are configured properly.')
                                            else:
                                                log.debug('Workmanager [' + str(workManager) + '] capacity constraint target [' + str(constraintTarget) + '] is valid.')


    return error