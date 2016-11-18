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
## jndi.py
##
## This script contains functions that manipulate JNDI names.

from javax.naming import Context, InitialContext, NameNotFoundException

try:
	from weblogic.jndi import WLInitialContextFactory
except ImportError:
	WLInitialContextFactory = None


#=======================================================================================
# Load required modules
#=======================================================================================

try:
	commonModule
except NameError:
	execfile('wlst/common.py')


#=======================================================================================
# Global variables
#=======================================================================================

jndiModule = '1.0.0'

log.debug('Loading module [jndi.py] version [' + jndiModule + ']')


#=======================================================================================
# Determines if a JNDI name already exists
#=======================================================================================

def isExistingJNDI(jndi, configProperties):
	# Look up connection factory and queue in JNDI.

	# check configuration properties

	webLogicAdminURL=configProperties.getProperty('webLogicAdmin.URL')

	properties = Properties()
	properties[Context.PROVIDER_URL] = webLogicAdminURL
	properties[Context.INITIAL_CONTEXT_FACTORY] = WLInitialContextFactory.name
	
	initialContext = InitialContext(properties)
	
	log.info('Preforming JNDI lookup for [' + jndi + ']')
	
	found = true
	
	try:
		jndiLookup = initialContext.lookup(jndi)
	except NameNotFoundException, error:
		found = false

	initialContext.close()
	
	return found
	
	# Done checking JNDI names
	
