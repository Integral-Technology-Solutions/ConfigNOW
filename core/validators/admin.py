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
    if validateAdminServerProperty(config):
        return False
    return True
    
def validateAdminServerProperty(domainProperties):
    error = 0
    
    helper.printHeader('[VALIDATING] admin server properties')
         
    adminPort = domainProperties.getProperty('wls.admin.listener.port')
    if not adminPort is None and len(adminPort)>0:
        try:
            int(adminPort)
        except ValueError:
            log.error('Please verify wls.admin.listener.port [' + str(adminPort) + '] property.')
        else:
            if int(adminPort)<0 or int(adminPort)>65535:
                log.error('Please verify wls.admin.listener.port property, port number is not in valid range [0-65535].')
            else:
                log.debug('Admin server port [' + str(adminPort) + '] is valid.')

    enableSSL = domainProperties.getProperty('wls.admin.listener.enableSSL')
    if not enableSSL is None and len(enableSSL)>0:
        if not enableSSL.upper()=='TRUE' and not enableSSL.upper()=='FALSE':
            error = 1
            log.error('The wls.admin.listener.enableSSL property supports only [true,false].')
        else:
            log.debug('Admin server ssl enable property [' + str(enableSSL) + '] is valid.')
            
            if enableSSL.upper()=='TRUE':
                sslPort = domainProperties.getProperty('wls.admin.listener.sslPort')
                if not sslPort is None and len(sslPort)>0:
                    try:
                        int(sslPort)
                    except ValueError:
                        log.error('Please verify wls.admin.listener.sslPort [' + str(sslPort) + '] property.')
                    else:
                        if int(sslPort)<0 or int(sslPort)>65535:
                            log.error('Please verify wls.admin.listener.sslPort property, port number is not in valid range [0-65535].')
                        else:
                            log.debug('Admin server ssl port [' + str(sslPort) + '] is valid.')
           
    adminchprotocol = domainProperties.getProperty('wls.admin.channel.protocol')
    if not adminchprotocol is None and len(adminchprotocol)>0:
        if not adminchprotocol=='t3' and not adminchprotocol=='t3s' and not adminchprotocol=='http' and not adminchprotocol=='https' and not adminchprotocol=='iiop' and not adminchprotocol=='iiops' and not adminchprotocol=='ldap' and not adminchprotocol=='ldaps' and not adminchprotocol=='admin':
            error = 1
            log.error('The wls.admin.channel.protocol property supports only [t3,t3s,http,https,iiop,iiops,ldap,ldaps,admin].')
        else:
            log.debug('Admin channel protocol property [' + str(adminchprotocol) + '] is valid.')

    adminChannelPort = domainProperties.getProperty('wls.admin.channel.listener.port')
    if not adminChannelPort is None and len(adminChannelPort)>0:
        try:
            int(adminChannelPort)
        except ValueError:
            log.error('Please verify wls.admin.channel.listener.port [' + str(adminChannelPort) + '] property.')
        else:
            if int(adminChannelPort)<0 or int(adminChannelPort)>65535:
                log.error('Please verify wls.admin.channel.listener.port property, port number is not in valid range [0-65535].')
            else:
                log.debug('Admin channel port [' + str(adminChannelPort) + '] is valid.')

    adminChannelPublicPort = domainProperties.getProperty('wls.admin.channel.listener.publicPort')
    if not adminChannelPublicPort is None and len(adminChannelPublicPort)>0:
        try:
            int(adminChannelPublicPort)
        except ValueError:
            log.error('Please verify wls.admin.channel.listener.publicPort [' + str(adminChannelPublicPort) + '] property.')
        else:
            if int(adminChannelPublicPort)<0 or int(adminChannelPublicPort)>65535:
                log.error('Please verify wls.admin.channel.listener.publicPort property, port number is not in valid range [0-65535].')
            else:
                log.debug('Admin channel public port [' + str(adminChannelPublicPort) + '] is valid.')

    httpEnable = domainProperties.getProperty('wls.admin.channel.httpEnable')
    if not httpEnable is None and len(httpEnable)>0:
        if not httpEnable.upper()=='TRUE' and not httpEnable.upper()=='FALSE':
            error = 1
            log.error('The wls.admin.channel.httpEnable property supports only [true,false].')
        else:
            log.debug('Admin http channel enable property [' + str(httpEnable) + '] is valid.')

    enableTunneling = domainProperties.getProperty('wls.admin.enableTunneling')
    if not enableTunneling is None and len(enableTunneling)>0:
        if not enableTunneling.upper()=='TRUE' and not enableTunneling.upper()=='FALSE':
            error = 1
            log.error('The wls.admin.enableTunneling property supports only [true,false].')
        else:
            log.debug('Admin tunnelling enable property [' + str(enableTunneling) + '] is valid.')

    admincustomlog = domainProperties.getProperty('wls.admin.log.custom')
    if not admincustomlog is None and len(admincustomlog)>0:
        if not admincustomlog.upper()=='TRUE' and not admincustomlog.upper()=='FALSE':
            error = 1
            log.error('The wls.admin.log.custom property supports only [true,false].')
        else:
            log.debug('Admin custom log enable property [' + str(admincustomlog) + '] is valid.')
            
            if admincustomlog.upper()=='TRUE':                
                filename = domainProperties.getProperty('wls.admin.log.filename')
                if not filename is None and len(filename)>0:
                    file = File(filename)
                    if file.isAbsolute():
                        if not file.exists():
                            log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file [' + str(filename) + '].')

                limitNumberOfFile = domainProperties.getProperty('wls.admin.log.limitNumOfFile')
                if not limitNumberOfFile is None and len(limitNumberOfFile)>0:
                    if not limitNumberOfFile.upper()=='TRUE' and not limitNumberOfFile.upper()=='FALSE':
                        error = 1
                        log.error('The wls.admin.log.limitNumOfFile property supports only [true,false].')
                    else:
                        log.debug('Admin log limit number of file property [' + str(limitNumberOfFile) + '] is valid.')

                fileToRetain = domainProperties.getProperty('wls.admin.log.fileToRetain')
                if not fileToRetain is None and len(fileToRetain)>0:
                    if not fileToRetain is None and len(fileToRetain)>0:
                        try:
                            int(fileToRetain)
                        except ValueError:
                            log.error('Please verify wls.admin.log.fileToRetain [' + str(fileToRetain) + '] property.')
                        else:
                            if int(fileToRetain)<1 or int(fileToRetain)>99999:
                                log.error('Please verify wls.admin.log.fileToRetain property, number is not in valid range [1-99999].')
                            else:
                                log.debug('Admin log file to retain [' + str(fileToRetain) + '] is valid.')

                logRotateOnStartup = domainProperties.getProperty('wls.admin.log.rotateLogOnStartup')
                if not logRotateOnStartup is None and len(logRotateOnStartup)>0:
                    if not logRotateOnStartup.upper()=='TRUE' and not logRotateOnStartup.upper()=='FALSE':
                        error = 1
                        log.error('The wls.admin.log.rotateLogOnStartup property supports only [true,false].')
                    else:
                        log.debug('Admin log rotate on startup property [' + str(logRotateOnStartup) + '] is valid.')

                rotationType = domainProperties.getProperty('wls.admin.log.rotationType')
                if not rotationType is None and len(rotationType)>0:
                    if not rotationType == 'bySize' and not rotationType == 'byTime':
                        error = 1
                        log.error('The wls.admin.log.rotationType property supports only [bySize,byTime].')
                    else:
                        log.debug('Admin log rotation type property [' + str(rotationType) + '] is valid.')

                    if rotationType == 'bySize':
                        fileMinSize = domainProperties.getProperty('wls.admin.log.fileMinSize')
                        if not fileMinSize is None and len(fileMinSize)>0:
                            try:
                                int(fileMinSize)
                            except ValueError:
                                log.error('Please verify wls.admin.log.fileMinSize [' + str(fileMinSize) + '] property.')
                            else:
                                if int(fileMinSize)<0 or int(fileMinSize)>65535:
                                    log.error('Please verify wls.admin.log.fileMinSize [' + str(fileMinSize) + '] property, number is not in valid range [0-65535].')
                                else:
                                    log.debug('Admin log file min size [' + str(fileMinSize) + '] is valid.')
                        
                    if rotationType == 'byTime':
                        rotationTime = domainProperties.getProperty('wls.admin.log.rotationTime')
                        if not rotationTime is None and len(rotationTime)>0:
                            if rotationTime.find(':')==-1:
                                error = 1
                                log.error('Please verify wls.admin.log.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                            else:
                                if len(rotationTime)<4 or len(rotationTime)>5:
                                    error = 1
                                    log.error('The wls.admin.log.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                                else:
                                    log.debug('Admin log rotation time [' + str(rotationTime) + '] is valid.')
                        
                        fileTimespan = domainProperties.getProperty('wls.admin.log.fileTimeSpan')
                        if not fileTimespan is None and len(fileTimespan)>0:
                            try:
                                int(fileTimespan)
                            except ValueError:
                                log.error('Please verify wls.admin.log.fileTimeSpan [' + str(fileTimespan) + '] property.')
                            else:
                                if int(fileTimespan)<1:
                                    log.error('Please verify wls.admin.log.fileTimeSpan [' + str(fileTimespan) + '] property, number is not in valid range [>=1].')
                                else:
                                    log.debug('Admin log file timespan [' + str(fileTimespan) + '] is valid.')
 
                rotationDir = domainProperties.getProperty('wls.admin.log.rotationDir')
                if not rotationDir is None and len(rotationDir)>0:
                    file = File(rotationDir)
                    if file.isAbsolute():
                        if not file.exists():
                            log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file [' + str(rotationDir) + '].')

                fileSeverity = domainProperties.getProperty('wls.admin.log.logFileSeverity')
                if not fileSeverity is None and len(fileSeverity)>0:
                    if not fileSeverity == 'Debug' and not fileSeverity == 'Info' and not fileSeverity == 'Warning':
                        error = 1
                        log.error('The wls.admin.log.logFileSeverity property supports only [Debug,Info,Warning].')
                    else:
                        log.debug('Admin log file severity property [' + str(fileSeverity) + '] is valid.')
                        
                broadcastSeverity = domainProperties.getProperty('wls.admin.log.broadcastSeverity')
                if not broadcastSeverity is None and len(broadcastSeverity)>0:
                    if not broadcastSeverity == 'Trace' and not broadcastSeverity == 'Debug' and not broadcastSeverity == 'Info' and not broadcastSeverity == 'Notice' and not broadcastSeverity == 'Warning' and not broadcastSeverity == 'Error' and not broadcastSeverity == 'Critical' and not broadcastSeverity == 'Alert' and not broadcastSeverity == 'Emergency' and not broadcastSeverity == 'Off':
                        error = 1
                        log.error('The wls.admin.log.broadcastSeverity property supports only [Trace,Debug,Info,Notice,Warning,Error,Critical,Alert,Emergency,Off].')
                    else:
                        log.debug('Admin broadcast severity property [' + str(broadcastSeverity) + '] is valid.')
                        
                memoryBufferSeverity = domainProperties.getProperty('wls.admin.log.memoryBufferSeverity')
                if not memoryBufferSeverity is None and len(memoryBufferSeverity)>0:
                    if not memoryBufferSeverity == 'Trace' and not memoryBufferSeverity == 'Debug' and not fileSeverity == 'Info' and not fileSeverity == 'Notice' and not fileSeverity == 'Warning' and not fileSeverity == 'Error' and not fileSeverity == 'Critical' and not fileSeverity == 'Alert' and not fileSeverity == 'Emergency' and not fileSeverity == 'Off':
                        error = 1
                        log.error('The wls.admin.log.memoryBufferSeverity property supports only [Trace,Debug,Info,Notice,Warning,Error,Critical,Alert,Emergency,Off].')
                    else:
                        log.debug('Admin memory buffer severity property [' + str(memoryBufferSeverity) + '] is valid.')

    adminhttpcustomlog = domainProperties.getProperty('wls.admin.httplog.enable')
    if not adminhttpcustomlog is None and len(adminhttpcustomlog)>0:
        if not adminhttpcustomlog.upper()=='TRUE' and not adminhttpcustomlog.upper()=='FALSE':
            error = 1
            log.error('The wls.admin.httplog.enable property supports only [true,false].')
        else:
            log.debug('Admin http custom log enable property [' + str(adminhttpcustomlog) + '] is valid.')
            
            if adminhttpcustomlog.upper()=='TRUE':
                filename = domainProperties.getProperty('wls.admin.httplog.filename')
                if not filename is None and len(filename)>0:
                    file = File(filename)
                    if file.isAbsolute():
                        if not file.exists():
                            log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file for [' + str(filename) + '].')
                
                limitNumberOfFile = domainProperties.getProperty('wls.admin.httplog.limitNumOfFile')
                if not limitNumberOfFile is None and len(limitNumberOfFile)>0:
                    if not limitNumberOfFile.upper()=='TRUE' and not limitNumberOfFile.upper()=='FALSE':
                        error = 1
                        log.error('The wls.admin.httplog.limitNumOfFile property supports only [true,false].')
                    else:
                        log.debug('Admin http log limit number of file property [' + str(limitNumberOfFile) + '] is valid.')

                fileToRetain = domainProperties.getProperty('wls.admin.httplog.fileToRetain')
                if not fileToRetain is None and len(fileToRetain)>0:
                    if not fileToRetain is None and len(fileToRetain)>0:
                        try:
                            int(fileToRetain)
                        except ValueError:
                            log.error('Please verify wls.admin.httplog.fileToRetain [' + str(fileToRetain) + '] property.')
                        else:
                            if int(fileToRetain)<1 or int(fileToRetain)>99999:
                                log.error('Please verify wls.admin.httplog.fileToRetain property, number is not in valid range [1-99999].')
                            else:
                                log.debug('Admin http log file to retain [' + str(fileToRetain) + '] is valid.')

                logRotateOnStartup = domainProperties.getProperty('wls.admin.httplog.rotateLogOnStartup')
                if not logRotateOnStartup is None and len(logRotateOnStartup)>0:
                    if not logRotateOnStartup.upper()=='TRUE' and not logRotateOnStartup.upper()=='FALSE':
                        error = 1
                        log.error('The wls.admin.httplog.rotateLogOnStartup property supports only [true,false].')
                    else:
                        log.debug('Admin http log rotate on startup property [' + str(logRotateOnStartup) + '] is valid.')

                rotationType = domainProperties.getProperty('wls.admin.httplog.rotationType')
                if not rotationType is None and len(rotationType)>0:
                    if not rotationType == 'bySize' and not rotationType == 'byTime':
                        error = 1
                        log.error('The wls.admin.httplog.rotationType property supports only [bySize,byTime].')
                    else:
                        log.debug('Admin http log rotation type property [' + str(rotationType) + '] is valid.')
 
                    if rotationType == 'bySize':
                        fileMinSize = domainProperties.getProperty('wls.admin.httplog.fileMinSize')
                        if not fileMinSize is None and len(fileMinSize)>0:
                            try:
                                int(fileMinSize)
                            except ValueError:
                                log.error('Please verify wls.admin.httplog.fileMinSize [' + str(fileMinSize) + '] property.')
                            else:
                                if int(fileMinSize)<0 or int(fileMinSize)>65535:
                                    log.error('Please verify wls.admin.httplog.fileMinSize [' + str(fileMinSize) + '] property, number is not in valid range [0-65535].')
                                else:
                                    log.debug('Admin http log file min size [' + str(fileMinSize) + '] is valid.')
                        
                    if rotationType == 'byTime':
                        rotationTime = domainProperties.getProperty('wls.admin.httplog.rotationTime')
                        if not rotationTime is None and len(rotationTime)>0:
                            if rotationTime.find(':')==-1:
                                error = 1
                                log.error('Please verify wls.admin.httplog.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                            else:
                                if len(rotationTime)<4 or len(rotationTime)>5:
                                    error = 1
                                    log.error('The wls.admin.httplog.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                                else:
                                    log.debug('Admin http log rotation time [' + str(rotationTime) + '] is valid.')
                        
                        fileTimespan = domainProperties.getProperty('wls.admin.httplog.fileTimeSpan')
                        if not fileTimespan is None and len(fileTimespan)>0:
                            try:
                                int(fileTimespan)
                            except ValueError:
                                log.error('Please verify wls.admin.httplog.fileTimeSpan [' + str(fileTimespan) + '] property.')
                            else:
                                if int(fileTimespan)<1:
                                    log.error('Please verify wls.admin.httplog.fileTimeSpan [' + str(fileTimespan) + '] property, number is not in valid range [>=1].')
                                else:
                                    log.debug('Admin http log file timespan [' + str(fileTimespan) + '] is valid.')

                rotationDir = domainProperties.getProperty('wls.admin.httplog.rotationDir')
                if not rotationDir is None and len(rotationDir)>0:
                    file = File(rotationDir)
                    if file.isAbsolute():
                        if not file.exists():
                            log.debug('[NOTE] Please make sure the user running this script has permission to create directory and file for [' + str(rotationDir) + '].')

    return error