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

execfile('wlst/common.py')
#from sets import Set
import sys

def run(config):
  """Shut down all servers in domain """
      
  admin_name = config.getProperty('wls.admin.name')
  log.debug("Admin server's name is '" + admin_name + "'")

  server_details = []
  serversString = config.getProperty('wls.servers')    # Collect list of servers from the properties files
  servers = serversString.split(",")
  __connectAdminServer(config)
  domainRuntime()

  for currentServer in servers:  # Collect listen address and port for the configured servers
  	currentServerName = config.getProperty('wls.server.' + currentServer + '.replace.name')
  
        if(currentServerName is None or currentServerName==''):
                currentServerName=config.getProperty('wls.server.' + currentServer + '.name')
  
        if (currentServerName != admin_name):
		serverStatus = getServerStatus(currentServerName)
		if (serverStatus.upper() != 'SHUTDOWN'):
			log.info("Sending shutdown command to server '" + currentServerName + "'")
	  		shutdown(currentServerName, 'Server', force='true')
		else:
	  		log.info("..not sending shutdown command to server '" + currentServerName + "' due to state of '" + serverStatus + "'")

  log.info("Sending shutdown command to admin server '" + admin_name + "'")
  shutdown(admin_name, 'Server', force='true')

  disconnect('true')
  
def getServerStatus(server):
  log.debug('Getting status of server ' + server)
  cd('/ServerLifeCycleRuntimes/' + server)
  return cmo.getState()
  pass
