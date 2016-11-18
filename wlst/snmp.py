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
## snmp.py
##
## This script contains functions that manipulate SNMP configuration

try:
	from weblogic.management.security.authentication import UserEditorMBean
except ImportError:
	UserEditorMBean = None

#=======================================================================================
# Load required modules
#=======================================================================================

try:
    commonModule
except NameError:
    execfile('wlst/common.py')
    
def __create_SNMPTrapDestination(path, beanName):
  log.info("Creating mbean of type SNMPTrapDestination ... ")
  cd(path)
  try:
    theBean = cmo.lookupSNMPTrapDestination(beanName)
    if theBean == None:
      cmo.createSNMPTrapDestination(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass

def __setAttributesFor_snmp(path, beanName, community, trapDest):
  log.debug("Setting attributes for mbean type SNMPTrapDestination")
  cd(path+"/SNMPTrapDestinations/"+beanName)
  set("Port", "162")
  set("Host", trapDest)
  set("Community", community)


def __setAttributes_SNMPAgent(path, community, port, agentx):
  log.debug("Setting attributes for mbean type SNMPAgent")
  cd(path)
  set("Enabled", "true")
  set("SNMPTrapVersion", "1")
  set("CommunityPrefix", community)
  set("SendAutomaticTrapsEnabled", "true")
  set("SNMPPort", port)
  set("PrivacyProtocol", "noPriv")
  set("LocalizedKeyCacheInvalidationInterval","3600000")
  set("MasterAgentXPort", agentx)    
  set("MaxInformRetryCount","1")
  set("InformRetryInterval","10000")
  set("InformEnabled","false")
  set("CommunityBasedAccessEnabled","true")
  set("SNMPEngineId","rwwa_snmp")
  set("AuthenticationProtocol","MD5")
  set("SNMPAccessForUserMBeansEnabled","false")


def __create_SNMPGaugeMonitor(path, beanName):
  cd(path)
  try:
    log.debug("creating mbean of type SNMPGaugeMonitor : " + beanName)
    theBean = cmo.lookupSNMPGaugeMonitor(beanName)
    if theBean == None:
      cmo.createSNMPGaugeMonitor(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass


def __setAttributesFor_SNMPGaugeMonitor(path,beanName):
  cd(path+"/SNMPGaugeMonitors/"+beanName)
  log.debug("setting attributes for mbean type SNMPGaugeMonitor : " + beanName)
  set("PollingInterval", "30")
  set("ThresholdLow", "100")
  set("ThresholdHigh", "200")
  set("MonitoredAttributeName", "MessagesCurrentCount")
  set("MonitoredMBeanType", "JMSDestinationRuntime")


def __create_SNMPLogFilter(path, beanName):
  cd(path)
  try:
    print "creating mbean of type SNMPLogFilter : " + beanName
    theBean = cmo.lookupSNMPLogFilter(beanName)
    if theBean == None:
      cmo.createSNMPLogFilter(beanName)
  except java.lang.UnsupportedOperationException, usoe:
    pass
  except weblogic.descriptor.BeanAlreadyExistsException,bae:
    pass
  except java.lang.reflect.UndeclaredThrowableException,udt:
    pass


def __setAttributesFor_SNMPLogFilter(path,beanName):
  cd(path+"/SNMPLogFilters/"+beanName)
  print "setting attributes for mbean type SNMPLogFilter : " + beanName
  set("SeverityLevel", "Error")
  set('EnabledServers',jarray.array([ObjectName('com.bea:Name=AdminServer,Type=Server')], ObjectName))


#==============================================================================
# createSNMP
#
# Creates SNMP configured in properties file.
#==============================================================================
def createSNMP(resourcesProperties, domainProperties):

  community = domainProperties.getProperty('snmp.community')
  port = domainProperties.getProperty('snmp.port')
  trapdest = domainProperties.getProperty('snmp.trapdest')
  domain = domainProperties.getProperty('wls.domain.name')
  agentx = domainProperties.getProperty('snmp.agentx')


  if not domain is None and not trapdest is None and not community is None and not port is None and not agentx is None:
    __create_SNMPTrapDestination("/SNMPAgent/"+domain, trapdest)
    __setAttributesFor_snmp("/SNMPAgent/"+domain, trapdest, community, trapdest)
    __setAttributes_SNMPAgent("/SNMPAgent/"+domain, community, port, agentx)

    __create_SNMPGaugeMonitor("/SNMPAgent/"+domain, "JMSQueueMessages")
    __setAttributesFor_SNMPGaugeMonitor("/SNMPAgent/"+domain, "JMSQueueMessages")

    __create_SNMPLogFilter("/SNMPAgent/"+domain, "SNMPLogFilter")
    __setAttributesFor_SNMPLogFilter("/SNMPAgent/"+domain,"SNMPLogFilter")
