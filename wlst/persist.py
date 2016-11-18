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
## persist.py
##
## This script contains functions that manipulate persistent stores.

#=======================================================================================
# Global variables
#=======================================================================================

persistModule = '1.2.0'

log.debug('Loading module [persist.py] version [' + persistModule + ']')

#=======================================================================================
# Configure filestores
#=======================================================================================
def createFileStores(resourcesProperties, domainProperties):
    fileStores=resourcesProperties.getProperty('persistent.filestores')
    if fileStores is None or len(fileStores)==0:
        log.info('Persistent Store is not specified, skipping.')
    else:
        fileStoreList=fileStores.split(',')
        for fileStore in fileStoreList:
            __createFileStore(fileStore, resourcesProperties, domainProperties)
            
#=======================================================================================
# Configure filestore
#=======================================================================================
def __createFileStore(fileStore, resourcesProperties, domainProperties):
    fileStoreName=resourcesProperties.getProperty('persistent.filestore.' + str(fileStore) + '.Name')
    fileStoreLocation=resourcesProperties.getProperty('persistent.filestore.' + str(fileStore) + '.Location')
    tmpTarget=resourcesProperties.getProperty('persistent.filestore.' + str(fileStore) + '.Target')
    migratable=resourcesProperties.getProperty('persistent.filestore.' + str(fileStore) + '.Migratable')
    replaceFlag=resourcesProperties.getProperty('persistent.filestore.' + str(fileStore) + '.Replace')
    if replaceFlag is None:
    	replaceFlag = 'false'
    
    targetServerName = None
    
    try:
        fileStore = None
        fileStoreExist = 0
        try:
            cd('/')
            fileStore = lookup(fileStoreName, 'FileStore')
        except Exception, error:
            log.info('Unable to find filestore [' + str(fileStoreName) + '], trying to create new one.')
        
        if fileStore is None:
            cd('/')
            fileStore = create(fileStoreName, 'FileStore')
              
            if tmpTarget is None or len(tmpTarget)==0:
                targetServerName=domainProperties.getProperty('wls.admin.name')
                targetServer = lookup(targetServerName, 'Server')
            else:
                targetServerName=domainProperties.getProperty('wls.server.' + str(tmpTarget) + '.name')
                if migratable.upper()=='TRUE':
                    targetServerName = targetServerName + ' (migratable)'            
                    targetServer = lookup(targetServerName, 'MigratableTarget')
                else:
                    targetServer = lookup(targetServerName, 'Server')
            try:
                fileStore.addTarget(targetServer)
            except Exception, error:
                cancelEdit('y')
                raise ScriptError, 'Unable to add filestore  [' + str(fileStoreName) + '] to target server [' + str(targetServerName) + '] : ' + str(error)
        
        else:
            if not migratable is None and migratable.upper()=='TRUE' and isUpdateToPreviouslyCreatedDomain().upper()=='TRUE':
                targetsArray = fileStore.getTargets()
	        for i in range(0, len(targetsArray)):
		    targetName = targetsArray[i].getName()
		    # If current target is not migratable
		    if targetName.find("(migratable)") < 0:
		       newTargetName = targetName + ' (migratable)'
		       targetServer = lookup(newTargetName, 'MigratableTarget')
		       jmsServersArray = cmo.getJMSServers()
		       for j in range(0, len(jmsServersArray)):
		           currentJMSServer = jmsServersArray[j]
		           currentPersistentStore = currentJMSServer.getPersistentStore()
		           if not currentPersistentStore is None and currentPersistentStore.getName()==fileStore.getName():
		               log.info('Upgrading target [' + targetName + '] in JMS Server [' + currentJMSServer.getName() + '] to migratable')
		               currentJMSServer.setTargets(jarray.array([targetServer], weblogic.management.configuration.MigratableTargetMBean))
		       log.info('Upgrading target [' + targetName + '] to migratable for persistent store [' + str(fileStore.getName()) + ']')
		       fileStore.setTargets(jarray.array([targetServer], weblogic.management.configuration.MigratableTargetMBean))
                safAgents = cmo.getSAFAgents()
                for k in range(0, len(safAgents)):
                    safAgent = safAgents[k]
                    safAgentTargets = safAgent.getTargets()
                    newSafAgentsArray = zeros(len(safAgentTargets), weblogic.management.configuration.MigratableTargetMBean)
                    for l in range(0, len(safAgentTargets)):
                        safAgentTarget = safAgentTargets[l]
                        safAgentTargetName = safAgentTarget.getName()
                        # If current target is not migratable
                        if safAgentTargetName.find("(migratable)") < 0:
                            newSafAgentTargetName = safAgentTargetName + ' (migratable)'
                            newSafAgentTarget = lookup(newSafAgentTargetName, 'MigratableTarget')
                            log.info('Setting migratable target [' + newSafAgentTarget.getName() + '] for SAF Agent [' + safAgent.getName() + '].')
                            newSafAgentsArray[l] = newSafAgentTarget
                        else:
                            log.info('Setting migratable target [' + safAgentTarget.getName() + '] for SAF Agent [' + safAgent.getName() + '].')
                            newSafAgentsArray[l] = safAgentTarget
                    log.info('Updating migratable targets for SAF Agent [' + safAgent.getName() + '].')
                    safAgent.setTargets(newSafAgentsArray)
            fileStoreExist = 1
            log.info('FileStore [' + str(fileStoreName) + '] already exists, checking REPLACE flag.')
            
        if not fileStoreExist or isReplaceRequired(domainProperties.getProperty('REPLACE')) or replaceFlag.upper()=='TRUE':
            if fileStoreExist and isReplaceRequired(domainProperties.getProperty('REPLACE')):
                log.info('REPLACE flag is specified, start replacing FileStore [' + str(fileStoreName) + '] properties.')
            
            file = File(fileStoreLocation)
            if not file.exists():
                if file.mkdirs():
                	log.info('File store directory [' + str(fileStoreLocation) + '] has been created successfully.')
            fileStore.setDirectory(fileStoreLocation)
            
    except Exception, error:
        cancelEdit('y')
        raise ScriptError, 'Unable to create filestore [' + str(fileStoreName) + '] for target server [' + str(targetServerName) + '] : ' + str(error)
