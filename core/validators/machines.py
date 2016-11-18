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

def run (config):
    machinesValid=helper.validateList(config, 'wls.domain.machines')
    if machinesValid:
        if validateMachines(config):
            return False
    else:
        return False
    return True

def validateMachines(domainProperties):
    error = 0
    machines = domainProperties.getProperty('wls.domain.machines')
    if not machines is None and len(machines)>0:
        machineList = machines.split(',')
        for machine in machineList:
            helper.printHeader('[VALIDATING] machine ' + str(machine) + ' properties')
            
            machineName = domainProperties.getProperty('wls.domain.machine.' + str(machine) + '.name')
            if machineName is None or len(machineName)==0:
                error = 1
                log.error('Please verify wls.domain.machine.' + str(machine) + '.name property if it exists in configuration.')
            else:
                log.debug('Machine [' + str(machine) + '] name property [' + str(machineName) + '] is valid.')
                
            nodeType = domainProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.type')
            if not nodeType is None and len(nodeType)>0:
                if not nodeType=='SSH' and not nodeType=='RSH' and not nodeType=='Plain' and not nodeType=='SSL' and not nodeType=='ssh' and not nodeType=='rsh' and not nodeType=='ssl' and not nodeType=='plain':
                    error = 1
                    log.error('The wls.domain.machine.' + str(machine) + '.nodemanager.type property support only [SSH,RSH,Plain,SSL,ssh,rsh,ssl,plain].')
                else:
                    log.debug('Machine [' + str(machine) + '] node type property [' + str(nodeType) + '] is valid.')

                nodeAddr = domainProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.address')
                if nodeAddr is None or len(nodeAddr)==0:
                    error = 1
                    log.error('Please verify wls.domain.machine.' + str(machine) + '.nodemanager.address property if it exists in configuration.')
                else:
                    log.debug('Machine [' + str(machine) + '] node address property [' + str(nodeAddr) + '] is valid.')

                nodePort = domainProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.port')
                if not nodePort is None and len(nodePort)>0:
                    try:
                        int(nodePort)
                    except ValueError:
                        log.error('Please verify wls.domain.machine.' + str(machine) + '.nodemanager.port property.')
                    else:
                        if int(nodePort)<0 or int(nodePort)>65535:
                            log.error('Please verify wls.domain.machine.' + str(machine) + '.nodemanager.port property, port number is not in valid range [0-65535].')
                        else:
                            log.debug('Machine [' + str(machine) + '] node manager port [' + str(nodePort) + '] is valid.')

                if nodeType=='SSH' or nodeType=='ssh' or nodeType=='RSH' or nodeType=='rsh':
                    nodehome = domainProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.nodeManagerHome')
                    if nodehome is None or len(nodehome)==0:
                        error = 1
                        log.error('Please verify wls.domain.machine.' + str(machine) + '.nodemanager.nodeManagerHome property if it exists in configuration.')
                    else:
                        log.debug('Machine [' + str(machine) + '] nodemanager home property [' + str(nodeAddr) + '] is valid.')

                    nodeShell = domainProperties.getProperty('wls.domain.machine.' + str(machine) + '.nodemanager.shellCommand')
                    if nodeShell is None or len(nodeShell)==0:
                        error = 1
                        log.error('Please verify wls.domain.machine.' + str(machine) + '.nodemanager.shellCommand property if it exists in configuration.')
                    else:
                        log.debug('Machine [' + str(machine) + '] nodemanager shell command property [' + str(nodeShell) + '] is valid.')
    return error
