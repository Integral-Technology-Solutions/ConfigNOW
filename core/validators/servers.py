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
    serversValid=helper.validateList(config, 'wls.servers')
    if serversValid:
        if validateServerProperty(config):
            return False
    else:
        return False
    return True

def validateServerProperty(domainProperties):
    error = 0
    
    machines = domainProperties.getProperty('wls.domain.machines')
    clusters = domainProperties.getProperty('wls.clusters')
    servers = domainProperties.getProperty('wls.servers')
    if not servers is None and len(servers)>0:
        serverList = servers.split(',')
        for server in serverList:
            helper.printHeader('[VALIDATING] server ' + str(server) + ' properties')
    
            serverName = domainProperties.getProperty('wls.server.' + str(server) + '.name')
            if serverName is None or len(serverName)==0:
                error = 1
                log.error('Please verify wls.server.' + str(server) + '.name property if it exists in configuration.')
            else:
                log.debug('Server [' + str(server) + '] name property [' + str(serverName) + '] is valid.')

            targetCluster = domainProperties.getProperty('wls.server.' + str(server) + '.cluster')
            if targetCluster:
                if not clusters is None and len(clusters)>0:
                    clusterList = clusters.split(',')
                    exist = 0
                    for cluster in clusterList:
                        clusterName = domainProperties.getProperty('wls.cluster.' + str(cluster) + '.name')
                        if cluster==targetCluster:
                            exist = 1
                            break
                    if not exist:
                        error = 1
                        log.error('wls.server.' + str(server) + '.cluster property refers to a cluster [' + targetCluster + '] that does not exist within wls.clusters property.')
                    else:
                        log.debug('Server [' + str(server) + '] cluster property [' + str(clusterName) + '] is valid.')

            serverHost = domainProperties.getProperty('wls.server.' + str(server) + '.listener.address')
            if serverHost is None or len(serverHost)==0:
                serverHost = 'localhost'
            
            serverPort = domainProperties.getProperty('wls.server.' + str(server) + '.listener.port')
            if not serverPort is None and len(serverPort)>0:
                try:
                    int(serverPort)
                except ValueError:
                    log.error('Please verify wls.server.' + str(server) + '.listener.port [' + str(serverPort) + '] property.')
                else:
                    if int(serverPort)<0 or int(serverPort)>65535:
                        log.error('Please verify wls.server.' + str(server) + '.listener.port property, port number is not in valid range [0-65535].')
                    else:
                        log.debug('Server [' + str(server) + '] server port property [' + str(serverPort) + '] is valid.')
        
            enableSSL = domainProperties.getProperty('wls.server.' + str(server) + '.listener.enableSSL')
            if not enableSSL is None and len(enableSSL)>0:
                if not enableSSL.upper()=='TRUE' and not enableSSL.upper()=='FALSE':
                    error = 1
                    log.error('The wls.server.' + str(server) + '.listener.enableSSL property supports only [true,false].')
                else:
                    log.debug('Server [' + str(server) + '] ssl enable property [' + str(enableSSL) + '] is valid.')
                    
                    if enableSSL.upper()=='TRUE':
                        sslPort = domainProperties.getProperty('wls.server.' + str(server) + '.listener.sslPort')
                        if not sslPort is None and len(sslPort)>0:
                            try:
                                int(sslPort)
                            except ValueError:
                                log.error('Please verify wls.server.' + str(server) + '.listener.sslPort [' + str(sslPort) + '] property.')
                            else:
                                if int(sslPort)<0 or int(sslPort)>65535:
                                    log.error('Please verify wls.server.' + str(server) + '.listener.sslPort property, port number is not in valid range [0-65535].')
                                else:
                                    log.debug('Server [' + str(server) + '] ssl port property [' + str(sslPort) + '] is valid.')

            customvars = domainProperties.getProperty('wls.server.' + str(server) + '.customenvvars')
            if not customvars is None and len(customvars)>0:
                customvarList = customvars.split(',')
                for customvar in customvarList:
                    helper.printHeader('[VALIDATING] Custom environment variable ' + str(customvar) + ' properties')
                    
                    customvarText = domainProperties.getProperty('wls.server.' + str(server) + '.customenvvar.' + str(customvar) + '.text')
                    if customvarText is None or len(customvarText)==0:
                        error = 1
                        log.error('Please verify wls.server.' + str(server) + '.customenvvar.' + str(customvar) + '.text property if it exists in configuration.')
                    else:
                        if customvarText.find('=')!=-1:
                            log.debug('Custome environment variable [' + str(customvar) + '] text property [' + str(customvarText) + '] is valid.')
                        else:
                            error = 1
                            log.error('Please verify wls.server.' + str(server) + '.customenvvar.' + str(customvar) + '.text property, this is applicable only for key-value pairs format [<name>=<value>].')

            serverChannelName = domainProperties.getProperty('wls.server.' + str(server) + '.channel.name')
            if not serverChannelName is None and len(serverChannelName)>0:
            
                serverChannelProtocol = domainProperties.getProperty('wls.server.' + str(server) + '.channel.protocol')
                if not serverChannelProtocol=='t3' and not serverChannelProtocol=='t3s' and not serverChannelProtocol=='http' and not serverChannelProtocol=='https' and not serverChannelProtocol=='iiop' and not serverChannelProtocol=='iiops' and not serverChannelProtocol=='ldap' and not serverChannelProtocol=='ldaps' and not serverChannelProtocol=='admin':
                    error = 1
                    log.error('The wls.server.' + str(server) + '.channel.protocol property supports only [t3,t3s,http,https,iiop,iiops,ldap,ldaps,admin].')
                else:
                    log.debug('Server [' + str(server) + '] channel protocol property [' + str(serverChannelProtocol) + '] is valid.')
                    
            serverChannelPort = domainProperties.getProperty('wls.server.' + str(server) + '.channel.listener.port')
            if not serverChannelPort is None and len(serverChannelPort)>0:
                try:
                    int(serverChannelPort)
                except ValueError:
                    log.error('Please verify wls.server.' + str(server) + '.channel.listener.port [' + str(serverChannelPort) + '] property.')
                else:
                    if int(serverChannelPort)<0 or int(serverChannelPort)>65535:
                        log.error('Please verify wls.server.' + str(server) + '.channel.listener.port property, port number is not in valid range [0-65535].')
                    else:
                        log.debug('Server [' + str(server) + '] channel port [' + str(serverChannelPort) + '] is valid.')
        
            serverChannelPublicPort = domainProperties.getProperty('wls.server.' + str(server) + '.channel.listener.publicPort')
            if not serverChannelPublicPort is None and len(serverChannelPublicPort)>0:
                try:
                    int(serverChannelPublicPort)
                except ValueError:
                    log.error('Please verify wls.server.' + str(server) + '.channel.listener.publicPort [' + str(serverChannelPublicPort) + '] property.')
                else:
                    if int(serverChannelPublicPort)<0 or int(serverChannelPublicPort)>65535:
                        log.error('Please verify wls.server.' + str(server) + '.channel.listener.publicPort property, port number is not in valid range [0-65535].')
                    else:
                        log.debug('Server [' + str(server) + '] channel public port [' + str(serverChannelPublicPort) + '] is valid.')
        
            httpEnable = domainProperties.getProperty('wls.server.' + str(server) + '.channel.httpEnable')
            if not httpEnable is None and len(httpEnable)>0:
                if not httpEnable.upper()=='TRUE' and not httpEnable.upper()=='FALSE':
                    error = 1
                    log.error('The wls.server.' + str(server) + '.channel.httpEnable property supports only [true,false].')
                else:
                    log.debug('Server [' + str(server) + '] http channel enable property [' + str(httpEnable) + '] is valid.')
        
            enableTunneling = domainProperties.getProperty('wls.server.' + str(server) + '.enableTunneling')
            if not enableTunneling is None and len(enableTunneling)>0:
                if not enableTunneling.upper()=='TRUE' and not enableTunneling.upper()=='FALSE':
                    error = 1
                    log.error('The wls.server.' + str(server) + '.enableTunneling property supports only [true,false].')
                else:
                    log.debug('Server [' + str(server) + '] tunnelling enable property [' + str(enableTunneling) + '] is valid.')
            
            targetMachine = domainProperties.getProperty('wls.server.' + str(server) + '.machine')
            if not targetMachine is None and len(targetMachine)>0:

                if not machines is None and len(machines)>0:
                    machineList = machines.split(',')
                    exist = 0
                    for machine in machineList:
                        machineName = domainProperties.getProperty('wls.domain.machine.' + str(machine) + '.name')
                        if machine==targetMachine:
                            exist = 1
                            break
                    if not exist:
                        error = 1
                        log.error('wls.server.' + str(server) + '.machine property refers to a machine that does not exist within the wls.domain.machines property list.')
                    else:
                        log.debug('Server [' + str(server) + '] machine property [' + str(targetMachine) + '] is valid.')
                        
            servercustomlog = domainProperties.getProperty('wls.server.' + str(server) + '.log.custom')
            if not servercustomlog is None and len(servercustomlog)>0:
               
                if not servercustomlog.upper()=='TRUE' and not servercustomlog.upper()=='FALSE':
                    error = 1
                    log.error('The wls.server.' + str(server) + '.log.custom property supports only [true,false].')
                else:
                    log.debug('Server [' + str(server) + '] custom log enable property [' + str(servercustomlog) + '] is valid.')
                    if servercustomlog.upper()=='TRUE':
                        filename = domainProperties.getProperty('wls.server.' + str(server) + '.log.filename')
                        if not filename is None and len(filename)>0:
                            file = File(filename)
                            if file.isAbsolute():
                                if not file.exists():
                                    log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file [' + str(filename) + '] on host [' + str(serverHost) + '].')

                        limitNumberOfFile = domainProperties.getProperty('wls.server.' + str(server) + '.log.limitNumOfFile')
                        if not limitNumberOfFile is None and len(limitNumberOfFile)>0:
                            if not limitNumberOfFile.upper()=='TRUE' and not limitNumberOfFile.upper()=='FALSE':
                                error = 1
                                log.error('The wls.admin.log.limitNumOfFile property supports only [true,false].')
                            else:
                                log.debug('Server [' + str(server) + '] log limit number of file property [' + str(limitNumberOfFile) + '] is valid.')
        
                        fileToRetain = domainProperties.getProperty('wls.server.' + str(server) + '.log.fileToRetain')
                        if not fileToRetain is None and len(fileToRetain)>0:
                            if not fileToRetain is None and len(fileToRetain)>0:
                                try:
                                    int(fileToRetain)
                                except ValueError:
                                    log.error('Please verify wls.server.' + str(server) + '.log.fileToRetain [' + str(fileToRetain) + '] property.')
                                else:
                                    if int(fileToRetain)<1 or int(fileToRetain)>99999:
                                        log.error('Please verify wls.server.' + str(server) + '.log.fileToRetain property, number is not in valid range [1-99999].')
                                    else:
                                        log.debug('Server [' + str(server) + '] log file to retain [' + str(fileToRetain) + '] is valid.')
        
                        logRotateOnStartup = domainProperties.getProperty('wls.server.' + str(server) + '.log.rotateLogOnStartup')
                        if not logRotateOnStartup is None and len(logRotateOnStartup)>0:
                            if not logRotateOnStartup.upper()=='TRUE' and not logRotateOnStartup.upper()=='FALSE':
                                error = 1
                                log.error('The wls.server.' + str(server) + '.log.rotateLogOnStartup property supports only [true,false].')
                            else:
                                log.debug('Server [' + str(server) + '] log rotate on startup property [' + str(logRotateOnStartup) + '] is valid.')

                        rotationType = domainProperties.getProperty('wls.server.' + str(server) + '.log.rotationType')
                        if not rotationType is None and len(rotationType)>0:
                            if not rotationType == 'bySize' and not rotationType == 'byTime':
                                error = 1
                                log.error('The wls.server.' + str(server) + '.log.rotationType property supports only [bySize,byTime].')
                            else:
                                log.debug('Server [' + str(server) + '] log rotation type property [' + str(rotationType) + '] is valid.')

                            if rotationType == 'bySize':
                                fileMinSize = domainProperties.getProperty('wls.server.' + str(server) + '.log.fileMinSize')
                                if not fileMinSize is None and len(fileMinSize)>0:
                                    try:
                                        int(fileMinSize)
                                    except ValueError:
                                        log.error('Please verify wls.server.' + str(server) + '.log.fileMinSize [' + str(fileMinSize) + '] property.')
                                    else:
                                        if int(fileMinSize)<0 or int(fileMinSize)>65535:
                                            log.error('Please verify wls.server.' + str(server) + '.log.fileMinSize [' + str(fileMinSize) + '] property, number is not in valid range [0-65535].')
                                        else:
                                            log.debug('Server [' + str(server) + '] log file min size [' + str(fileMinSize) + '] is valid.')
                                
                            if rotationType == 'byTime':
                                rotationTime = domainProperties.getProperty('wls.server.' + str(server) + '.log.rotationTime')
                                if not rotationTime is None and len(rotationTime)>0:
                                    if rotationTime.find(':')==-1:
                                        error = 1
                                        log.error('Please verify wls.server.' + str(server) + '.log.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                                    else:
                                        if len(rotationTime)<4 or len(rotationTime)>5:
                                            error = 1
                                            log.error('The wls.server.' + str(server) + '.log.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                                        else:
                                            log.debug('Server [' + str(server) + '] log rotation time [' + str(rotationTime) + '] is valid.')
                                
                                fileTimespan = domainProperties.getProperty('wls.server.' + str(server) + '.log.fileTimeSpan')
                                if not fileTimespan is None and len(fileTimespan)>0:
                                    try:
                                        int(fileTimespan)
                                    except ValueError:
                                        log.error('Please verify wls.server.' + str(server) + '.log.fileTimeSpan [' + str(fileTimespan) + '] property.')
                                    else:
                                        if int(fileTimespan)<1:
                                            log.error('Please verify wls.server.' + str(server) + '.log.fileTimeSpan [' + str(fileTimespan) + '] property, number is not in valid range [<=1].')
                                        else:
                                            log.debug('Server [' + str(server) + '] log file timespan [' + str(fileTimespan) + '] is valid.')
         
                        rotationDir = domainProperties.getProperty('wls.server.' + str(server) + '.log.rotationDir')
                        if not rotationDir is None and len(rotationDir)>0:
                            file = File(rotationDir)
                            if file.isAbsolute():
                                if not file.exists():
                                    log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file [' + str(rotationDir) + '] on host [' + str(serverHost) + '].')

                        fileSeverity = domainProperties.getProperty('wls.server.' + str(server) + '.log.logFileSeverity')
                        if not fileSeverity is None and len(fileSeverity)>0:
                            if not fileSeverity == 'Debug' and not fileSeverity == 'Info' and not fileSeverity == 'Warning':
                                error = 1
                                log.error('The wls.server.' + str(server) + '.log.logFileSeverity property supports only [Debug,Info,Warning].')
                            else:
                                log.debug('Server [' + str(server) + '] log file severity property [' + str(fileSeverity) + '] is valid.')
                                
                        broadcastSeverity = domainProperties.getProperty('wls.server.' + str(server) + '.log.broadcastSeverity')
                        if not broadcastSeverity is None and len(broadcastSeverity)>0:
                            if not broadcastSeverity == 'Trace' and not broadcastSeverity == 'Debug' and not broadcastSeverity == 'Info' and not broadcastSeverity == 'Notice' and not broadcastSeverity == 'Warning' and not broadcastSeverity == 'Error' and not broadcastSeverity == 'Critical' and not broadcastSeverity == 'Alert' and not broadcastSeverity == 'Emergency' and not broadcastSeverity == 'Off':
                                error = 1
                                log.error('The wls.server.' + str(server) + '.log.broadcastSeverity property supports only [Trace,Debug,Info,Notice,Warning,Error,Critical,Alert,Emergency,Off].')
                            else:
                                log.debug('Server [' + str(server) + '] broadcast severity log property [' + str(broadcastSeverity) + '] is valid.')
                                
                        memoryBufferSeverity = domainProperties.getProperty('wls.server.' + str(server) + '.log.memoryBufferSeverity')
                        if not memoryBufferSeverity is None and len(memoryBufferSeverity)>0:
                            if not memoryBufferSeverity == 'Trace' and not memoryBufferSeverity == 'Debug' and not fileSeverity == 'Info' and not fileSeverity == 'Notice' and not fileSeverity == 'Warning' and not fileSeverity == 'Error' and not fileSeverity == 'Critical' and not fileSeverity == 'Alert' and not fileSeverity == 'Emergency' and not fileSeverity == 'Off':
                                error = 1
                                log.error('The wls.server.' + str(server) + '.log.memoryBufferSeverity property supports only [Trace,Debug,Info,Notice,Warning,Error,Critical,Alert,Emergency,Off].')
                            else:
                                log.debug('Server [' + str(server) + '] memory buffer severity log property [' + str(memoryBufferSeverity) + '] is valid.')
    
            serverhttpcustomlog = domainProperties.getProperty('wls.server.' + str(server) + '.httplog.enable')
            if not serverhttpcustomlog is None and len(serverhttpcustomlog)>0:
                if not serverhttpcustomlog.upper()=='TRUE' and not serverhttpcustomlog.upper()=='FALSE':
                    error = 1
                    log.error('The wls.server.' + str(server) + '.httplog.enable property supports only [true,false].')
                else:
                    log.debug('Server [' + str(server) + '] http custom log enable property [' + str(serverhttpcustomlog) + '] is valid.')
                    
                    if serverhttpcustomlog.upper()=='TRUE':
                        filename = domainProperties.getProperty('wls.server.' + str(server) + '.httplog.filename')
                        if not filename is None and len(filename)>0:
                            file = File(filename)
                            if file.isAbsolute():
                                if not file.exists():
                                    log.debug('[NOTE] Please make sure the user running this script has permission to create directories and directory and file [' + str(filename) + '] on host [' + str(serverHost) + '].')

                        rotationType = domainProperties.getProperty('wls.server.' + str(server) + '.httplog.rotationType')
                        if not rotationType is None and len(rotationType)>0:
                            if not rotationType == 'bySize' and not rotationType == 'byTime':
                                error = 1
                                log.error('The wls.server.' + str(server) + '.httplog.rotationType property supports only [bySize,byTime].')
                            else:
                                log.debug('Server [' + str(server) + '] http log rotation type property [' + str(rotationType) + '] is valid.')

                            if rotationType == 'bySize':
                                fileMinSize = domainProperties.getProperty('wls.server.' + str(server) + '.httplog.fileMinSize')
                                if not fileMinSize is None and len(fileMinSize)>0:
                                    try:
                                        int(fileMinSize)
                                    except ValueError:
                                        log.error('Please verify wls.server.' + str(server) + '.httplog.fileMinSize [' + str(fileMinSize) + '] property.')
                                    else:
                                        if int(fileMinSize)<0 or int(fileMinSize)>65535:
                                            log.error('Please verify wls.server.' + str(server) + '.httplog.fileMinSize [' + str(fileMinSize) + '] property, number is not in valid range [0-65535].')
                                        else:
                                            log.debug('Server [' + str(server) + '] http log file min size [' + str(fileMinSize) + '] is valid.')
                                
                            if rotationType == 'byTime':
                                rotationTime = domainProperties.getProperty('wls.server.' + str(server) + '.httplog.rotationTime')
                                if not rotationTime is None and len(rotationTime)>0:
                                    if rotationTime.find(':')==-1:
                                        error = 1
                                        log.error('Please verify wls.server.' + str(server) + '.httplog.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                                    else:
                                        if len(rotationTime)<4 or len(rotationTime)>5:
                                            error = 1
                                            log.error('The wls.server.' + str(server) + '.httplog.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                                        else:
                                            log.debug('Server [' + str(server) + '] http log rotation time [' + str(rotationTime) + '] is valid.')
                                
                                fileTimespan = domainProperties.getProperty('wls.server.' + str(server) + '.httplog.fileTimeSpan')
                                if not fileTimespan is None and len(fileTimespan)>0:
                                    try:
                                        int(fileTimespan)
                                    except ValueError:
                                        log.error('Please verify wls.server.' + str(server) + '.httplog.fileTimeSpan [' + str(fileTimespan) + '] property.')
                                    else:
                                        if int(fileTimespan)<1:
                                            log.error('Please verify wls.server.' + str(server) + '.httplog.fileTimeSpan [' + str(fileTimespan) + '] property, number is not in valid range [>=1].')
                                        else:
                                            log.debug('Server [' + str(server) + '] log file timespan [' + str(fileTimespan) + '] is valid.')
        
                        rotationDir = domainProperties.getProperty('wls.server.' + str(server) + '.httplog.rotationDir')
                        if not rotationDir is None and len(rotationDir)>0:
                            file = File(rotationDir)
                            if file.isAbsolute():
                                if not file.exists():
                                    log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file [' + str(rotationDir) + '] on host [' + str(serverHost) + '].')

    return error