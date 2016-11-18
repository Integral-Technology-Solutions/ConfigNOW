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

from java.io import FileInputStream
from java.io import File
from java.util import Properties

import os

def run():
    versionFile = File(os.getcwd(), 'core/resources/version.properties')
    log.debug('Checking if ' + str(versionFile) + ' exists')
    if os.path.exists(str(versionFile)):
        versionProperties = Properties()
        input = FileInputStream(versionFile)
        versionProperties.load(input)
        input.close()
        versionInfo=getVersionInfo(versionProperties)
    else:
    	versionInfo=getVersionInfo(None)
    log.info('this')
    log.info(versionInfo)
    
def getVersionInfo(versionProperties):
    if versionProperties is None:
        versionProperties = Properties()
        versionProperties.setProperty('version','TBA')
    
    version=versionProperties.getProperty('version')
    date=versionProperties.getProperty('release.date')
    client=versionProperties.getProperty('client')
	
    versionInfo=''
    versionInfo += '\n\n ===================================================\n'
    versionInfo += ' ===================================================\n\n'
    versionInfo += ' Redback Environment Configuration Tool\n'
    versionInfo += ' \n'
    
    if not version:
        version='TBA'
    versionInfo += '  Release Version : ' + version + '\n'
    
    if date:
        versionInfo += '     Release Date : ' + date + '\n'
        
    if client:
        versionInfo += '           Client : ' + client + '\n'
    
    versionInfo += ' \n'
    
    if version == 'TBA':
        versionInfo += ' Notes: This is a development release of ConfigNOW.\n'
        versionInfo += ' Notes: This is a development release of ConfigNOW.\n'
        versionInfo += ' This release has not been packaged as part of the\n'
        versionInfo += ' formal release process.\n\n'
    
    versionInfo += ' ===================================================\n'
    versionInfo += ' ===================================================\n'
    return versionInfo