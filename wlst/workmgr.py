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
## workmgr.py
##
## This script contains functions that manipulate work manager.

#=======================================================================================
# Import common library
#=======================================================================================

try:
    commonModule
except NameError:
    execfile('wlst/common.py')
    
#=======================================================================================
# Global variables
#=======================================================================================
    
workManagerModule = '1.1.0'

log.debug('Loading module [workmgr.py] version [' + workManagerModule + ']')

def __createWorkManagers(online, domainProperties):
    workManagers=domainProperties.getProperty('wls.workManagers')
    if workManagers is None or len(workManagers)==0:
        log.info('WorkManager(s) is not specified, skipping.')
    else:
        cd('/')
        workManagerList=workManagers.split(',')
        for workManager in workManagerList:
            __createWorkManager(workManager, online, domainProperties)
            
def __createWorkManager(workManager, online, domainProperties):
        
    domainName=domainProperties.getProperty('wls.domain.name')
    workManagerName=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.name')
    
    try:
        manager = None
        managerExists = 0
        try:
            selftuningPath = '/SelfTuning/' + str(domainName)
            if online:
                cd(selftuningPath)
            else:
                cd('/')
                log.info('Creating SelfTuning [' + str(domainName) + '].')
                tuning = create(str(domainName), 'SelfTuning')
                cd(selftuningPath)
        except Exception, error:
            raise ScriptError, 'Unable to create or access SelfTuning :' + str(error)
            
        try:
            cd(selftuningPath + '/WorkManagers/' + str(workManagerName))
            manager = cmo
        except Exception, error:
            log.info('Unable to find WorkManager [' + str(workManagerName) + '], trying to create new one.')
            
        if manager is None:
            cd(selftuningPath)
            log.info('Creating WorkManager [' + str(workManagerName) + '].')
            manager = create(str(workManagerName), 'WorkManager')
            targets=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.targets')
            targetType=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.targetType')
            
            if online:
                __setTargetsOnline(manager, targets, targetType, domainProperties)
            else:
                cd('WorkManager/' + str(workManagerName))
                __setTargetsOffline(targets, targetType, domainProperties)
                
            log.info('WorkManager [' + str(workManagerName) + '] has been created successfully.')
        else:
            managerExists = 1
            log.info('WorkManager [' + str(workManagerName) + '] already exists, checking REPLACE flag.')
            
        if not managerExists or isReplaceRequired(domainProperties.getProperty('REPLACE')):
            if managerExists and isReplaceRequired(domainProperties.getProperty('REPLACE')):
                log.info('REPLACE flag is specified, start replacing WorkManager [' + str(workManagerName) + '] properties.')
            ignoreStuckThreads=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.ignoreStuckThreads')
            if not ignoreStuckThreads is None:
                if ignoreStuckThreads.upper()=='TRUE':
                    manager.setIgnoreStuckThreads(1)
                else:
                    if ignoreStuckThreads.upper()=='FALSE':
                        manager.setIgnoreStuckThreads(0)
                    else:
                        log.info('Does not support ignoreStuckThreads value [' + str(ignoreStuckThreads) + '], skipping.')

    except Exception, error:
        raise ScriptError, 'Unable to create WorkManager [' + str(workManagerName) + ']: ' + str(error)
    
    try:
        minThreadsConstraintName=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.name')
        if not minThreadsConstraintName is None and len(minThreadsConstraintName)>0:
            minThreadsConstraintCount=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.count')
            minThreadsConstraintTargets=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.targets')
            minThreadsConstraintTargetType=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.minThreadsConstraint.targetType')
            
            cd(selftuningPath)
            minThreadConstraint = None
            if online:
                minThreadConstraint = cmo.lookupMinThreadsConstraint(str(minThreadsConstraintName))
            else:
                try:
                    cd('MinThreadsConstraint')
                    cd(str(minThreadsConstraintName))
                    minThreadConstraint = cmo
                except Exception, error:
                    log.info('Unable to find MinThreadsConstraint [' + str(minThreadsConstraintName) + ']. The constraint will be created.')

            if minThreadConstraint is None:
                cd(selftuningPath)
                log.info('Creating MinThreadsConstraint [' + str(minThreadsConstraintName) + '].')
                minThreadConstraint = create(str(minThreadsConstraintName), 'MinThreadsConstraint')
                minThreadConstraint.setCount(int(minThreadsConstraintCount))
 
                if online:
                    __setTargetsOnline(minThreadConstraint, targets, targetType, domainProperties)
                else:
                    cd('MinThreadsConstraint/' + minThreadsConstraintName)
                    __setTargetsOffline(targets, targetType, domainProperties)  
                manager.setMinThreadsConstraint(minThreadConstraint)
                log.info('MinThreadsConstraint [' + str(minThreadsConstraintName) + '] has been created successfully and assigned to WorkManager [' + str(workManagerName) + '].')
            else:
                if isReplaceRequired(domainProperties.getProperty('REPLACE')):
                    minThreadConstraint.setCount(int(minThreadsConstraintCount))
                else:
                    log.info('MinThreadsConstraint [' + str(minThreadsConstraintName) + '] already exist, skipping.')
    except Exception, error:
        raise ScriptError, 'Unable to create MinThreadsConstraint [' + str(minThreadsConstraintName) + ']: ' + str(error)
        
    try:
        maxThreadsConstraintName=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.name')
        if not maxThreadsConstraintName is None and len(maxThreadsConstraintName)>0:
            maxThreadsConstraintCount=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.count')
            maxThreadsConstraintTargets=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targets')
            maxThreadsConstraintTargetType=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.maxThreadsConstraint.targetType')
            
            cd(selftuningPath)
            maxThreadConstraint = None
            if online:
                maxThreadConstraint = cmo.lookupMaxThreadsConstraint(str(maxThreadsConstraintName))
            else:
                try:
                    cd('MaxThreadsConstraint')
                    cd(str(maxThreadsConstraintName))
                    maxThreadConstraint = cmo
                except Exception, error:
                    log.info('Unable to find MaxThreadsConstraint [' + str(maxThreadsConstraintName) + ']. The constraint will be created.')

            if maxThreadConstraint is None:
                cd(selftuningPath)
                log.info('Creating MaxThreadsConstraint [' + str(maxThreadsConstraintName) + '].')
                maxThreadConstraint = create(maxThreadsConstraintName, 'MaxThreadsConstraint')
                maxThreadConstraint.setCount(int(maxThreadsConstraintCount))
                if online:
                    __setTargetsOnline(maxThreadConstraint, targets, targetType, domainProperties)
                else:
                    cd('MaxThreadsConstraint/' + maxThreadsConstraintName)
                    __setTargetsOffline(targets, targetType, domainProperties)   
                manager.setMaxThreadsConstraint(maxThreadConstraint)
                log.info('MaxThreadsConstraint [' + str(maxThreadsConstraintName) + '] has been created successfully and assigned to WorkManager [' + str(workManagerName) + '].')
            else:
                if isReplaceRequired(domainProperties.getProperty('REPLACE')):
                    maxThreadConstraint.setCount(int(maxThreadsConstraintCount))
                else:
                    log.info('MaxThreadsConstraint [' + str(maxThreadsConstraintName) + '] already exist, skipping.')
    except Exception, error:
        raise ScriptError, 'Unable to create MaxThreadsConstraint [' + str(maxThreadsConstraintName) + ']: ' + str(error)
    
    try:
        fairShareRequestClassName=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.name')
        if not fairShareRequestClassName is None and len(fairShareRequestClassName)>0:
            fairShareRequestClassFairShare=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.fairShare')
            fairShareRequestClassTargets=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.targets')
            fairShareRequestClassTargetType=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.fairShareRequestClass.targetType')
            
            cd(selftuningPath)
            fairShareRequestClass = None
            if online:
                fairShareRequestClass = cmo.lookupFairShareRequestClass(str(fairShareRequestClassName))
            else:
                try:
                    cd('FairShareRequestClass')
                    cd(str(fairShareRequestClassName))
                    fairShareRequestClass = cmo
                except Exception, error:
                    log.info('Unable to find FairShareRequestClass [' + str(fairShareRequestClassName) + ']. The constraint will be created.')

            if fairShareRequestClass is None:
                cd(selftuningPath)
                log.info('Creating FairShareRequestClass [' + str(fairShareRequestClassName) + '].')
                fairShareRequestClass = create(fairShareRequestClassName, 'FairShareRequestClass')
                fairShareRequestClass.setFairShare(int(fairShareRequestClassFairShare))
                if online:
                    __setTargetsOnline(fairShareRequestClass, targets, targetType, domainProperties)
                else:
                    cd('FairShareRequestClass/' + fairShareRequestClassName)
                    __setTargetsOffline(targets, targetType, domainProperties)  
                manager.setFairShareRequestClass(fairShareRequestClass)
                log.info('FairShareRequestClass [' + str(fairShareRequestClassName) + '] has been created successfully and assigned to WorkManager [' + str(workManagerName) + '].')
            else:
                if isReplaceRequired(domainProperties.getProperty('REPLACE')):
                    fairShareRequestClass.setFairShare(int(fairShareRequestClassFairShare))
                else:
                    log.info('FairShareRequestClass [' + str(fairShareRequestClassName) + '] already exist, skipping.')
    except Exception, error:
        raise ScriptError, 'Unable to create FairShareRequestClass [' + str(fairShareRequestClassName) + ']: ' + str(error)

    try:        
        responseTimeRequestClassName=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.responseTimeRequestClass.name')
        if not responseTimeRequestClassName is None and len(responseTimeRequestClassName)>0:
            responseTimeRequestClassGoal=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.responseTimeRequestClass.goalMs')
            responseTimeRequestClassTargets=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targets')
            responseTimeRequestClassTargetType=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.responseTimeRequestClass.targetType')
            
            cd(selftuningPath)
            responseTimeRequestClass = None
            if online:
                responseTimeRequestClass = cmo.lookupResponseTimeRequestClass(str(responseTimeRequestClassName))
            else:
                try:
                    cd('ResponseTimeRequestClass')
                    cd(str(responseTimeRequestClassName))
                    responseTimeRequestClass = cmo
                except Exception, error:
                    log.info('Unable to find ResponseTimeRequestClass [' + str(responseTimeRequestClassName) + ']. The constraint will be created.')

            if responseTimeRequestClass is None:
                cd(selftuningPath)
                log.info('Creating ResponseTimeRequestClass [' + str(responseTimeRequestClassName) + '].')
                responseTimeRequestClass = create(responseTimeRequestClassName, 'ResponseTimeRequestClass')
                responseTimeRequestClass.setGoalMs(int(responseTimeRequestClassGoal))
                if online:
                    __setTargetsOnline(responseTimeRequestClass, targets, targetType, domainProperties)
                else:
                    cd('ResponseTimeRequestClass/' + responseTimeRequestClassName)
                    __setTargetsOffline(targets, targetType, domainProperties)  
                manager.setResponseTimeRequestClass(responseTimeRequestClass)
                log.info('ResponseTimeRequestClass [' + str(responseTimeRequestClassName) + '] has been created successfully and assigned to WorkManager [' + str(workManagerName) + '].')
            else:
                if isReplaceRequired(domainProperties.getProperty('REPLACE')):
                    responseTimeRequestClass.setGoalMs(int(responseTimeRequestClassGoal))
                else:
                    log.info('ResponseTimeRequestClass [' + str(responseTimeRequestClassName) + '] already exist, skipping.')
    except Exception, error:
        raise ScriptError, 'Unable to create ResponseTimeRequestClass [' + str(responseTimeRequestClassName) + ']: ' + str(error)

    try:
        contextRequestClassName=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.contextRequestClass.name')
        if not contextRequestClassName is None and len(contextRequestClassName)>0:
            contextRequestClassTargets=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.contextRequestClass.targets')
            contextRequestClassTargetType=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.contextRequestClass.targetType')
            
            cd(selftuningPath)
            contextRequestClass = None
            if online:
                contextRequestClass = cmo.lookupContextRequestClass(str(contextRequestClassName))
            else:
                try:
                    cd('ContextRequestClass')
                    cd(str(contextRequestClassName))
                    contextRequestClass = cmo
                except Exception, error:
                    log.info('Unable to find ContextRequestClass [' + str(contextRequestClassName) + ']. The constraint will be created.')

            if contextRequestClass is None:
                cd(selftuningPath)
                log.info('Creating ContextRequestClass [' + str(contextRequestClassName) + '].')
                contextRequestClass = create(contextRequestClassName, 'ContextRequestClass')
                if online:
                    __setTargetsOnline(contextRequestClass, targets, targetType, domainProperties)
                else:
                    cd('ContextRequestClass/' + contextRequestClassName)
                    __setTargetsOffline(targets, targetType, domainProperties)
                manager.setContextRequestClass(contextRequestClass)
                log.info('ContextRequestClass [' + str(contextRequestClassName) + '] has been created successfully and assigned to WorkManager [' + str(workManagerName) + '].')
            else:
                log.info('ContextRequestClass [' + str(contextRequestClassName) + '] already exist.')
    except Exception, error:
        raise ScriptError, 'Unable to create ContextRequestClass [' + str(contextRequestClassName) + ']: ' + str(error)
       
    try:
        capacityConstraintName=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.name')
        if not capacityConstraintName is None and len(capacityConstraintName)>0:
            capacityConstraintCount=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.count')
            capacityConstraintTargets=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.targets')
            capacityConstraintTargetType=domainProperties.getProperty('wls.workManager.' + str(workManager) + '.capacityConstraint.targetType')
            
            cd(selftuningPath)
            capacityConstraint = None
            if online:
                capacityConstraint = cmo.lookupCapacity(str(capacityConstraintName))
            else:
                try:
                    cd('Capacity')
                    cd(str(capacityConstraintName))
                    capacityConstraint = cmo
                except Exception, error:
                    log.info('Unable to find Capacity [' + str(capacityConstraintName) + ']. The constraint will be created.')

            if capacityConstraint is None:
                cd(selftuningPath)
                log.info('Creating Capacity [' + str(capacityConstraintName) + '].')
                capacityConstraint = create(capacityConstraintName, 'Capacity')
                capacityConstraint.setCount(int(capacityConstraintCount))
                if online:
                    __setTargetsOnline(capacityConstraint, targets, targetType, domainProperties)
                else:
                    cd('Capacity/' + capacityConstraintName)
                    __setTargetsOffline(targets, targetType, domainProperties)
                manager.setCapacity(capacityConstraint)
                log.info('Capacity [' + str(capacityConstraintName) + '] has been created successfully and assigned to WorkManager [' + str(workManagerName) + '].')
            else:
                if isReplaceRequired(domainProperties.getProperty('REPLACE')):
                    capacityConstraint.setCount(int(capacityConstraintCount))
                else:
                    log.info('Capacity [' + str(capacityConstraintName) + '] already exist, skipping.')

    except Exception, error:
        raise ScriptError, 'Unable to create Capacity [' + str(capacityConstraintName) + ']: ' + str(error)

