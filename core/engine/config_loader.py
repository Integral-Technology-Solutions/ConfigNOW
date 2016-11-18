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

from org.apache.log4j import Logger
from java.io import FileInputStream
from java.io import FileOutputStream
from java.util import Properties
from java.lang import String

import sys
import re
import os

import redback

execfile('core/commands/password_encrypter.py')

log = Logger.getLogger('config_loader')
data_linage = Properties()

def addPropertiesFromFile(props, filename, site_home):
    addProps = Properties()
    input = FileInputStream(filename)
    addProps.load(input)
    input.close()

    baseFileList = addProps.getProperty('base')
    
    if not baseFileList is None:
        baseFiles = baseFileList.split(",")
        for baseFile in baseFiles:
            baseFileResolved=getBaseFile(baseFile, site_home)
            if baseFileResolved=='':
                log.error('Configuration inherits from properties file that does not exist: ' + baseFile)
                log.info('Suggested Fix: Update the base property within ' + filename + ' to the correct file path')
                sys.exit()
            log.debug('Attempting to load properties from ' + baseFile)
            addPropertiesFromFile(addProps, baseFileResolved, site_home)
            addProps.remove('base')

    enum = addProps.keys()
    while enum.hasMoreElements():
        key = enum.nextElement()
        if props.getProperty(key) is None:
            props.setProperty(key, addProps.getProperty(key))
            addDataLinage(key,filename,addProps.getProperty(key))

def addDataLinage(key,filename,value):
    if data_linage.getProperty(key) is None:
        data_linage.setProperty(key,filename + ' [Value=' + value + ']')
    else:
        # Simple bit of code that stops it adding the same file twice
        if String(data_linage.getProperty(key)).indexOf(filename) != 0:
            data_linage.setProperty(key,filename + ' [Value=' + value + ']' + ' --> \r\n        Inherited From : ' + data_linage.getProperty(key))

def getDataLinage():
    return data_linage
       
def getBaseFile(baseFile, site_home):
	if site_home:
		if os.path.exists(site_home + '/' + baseFile):
			return site_home + '/' + baseFile
	if os.path.exists(baseFile):
		return baseFile		
	return ''

def resolveProperty(key, configProperties):
    initialValue = configProperties.getProperty(key)
    if initialValue is None:
        return initialValue
    # Check if any of the property is referenceing itself
    if initialValue.find("${"+key+"}")>-1:
    	log.error("property is referencing itself. Please verify property definition for -> "+key)
    	sys.exit("Property can't reference itself")        
    resolvedValue = initialValue
    allMatches = re.search(r"\$\{(.*?)\}", initialValue)
    while not allMatches is None:
        propValue = resolveProperty(allMatches.group(1), configProperties)
        if not propValue is None:
            resolvedValue = resolvedValue.replace("${" + allMatches.group(1) + "}", propValue)
            allMatches = re.search(r"\$\{(.*?)\}", resolvedValue)
        else:
            return None

    return resolvedValue
   

def loadProperties(cfg_file, extra_props):
    props = Properties()
    iterated_props = Properties()
    inherited_props = Properties()
    
    data_linage = Properties()
	
    redback_reg = redback.load_redback_registry() 
    site_home = redback_reg.getProperty('site.home') 
    global_properties = redback_reg.getProperty('global.properties')

    if global_properties:
        if site_home:
            baseFile=getBaseFile(global_properties, site_home)
            if baseFile=='':
                log.error('Global properties file does not exist: ' + global_properties)
                log.info('Suggested Fix: Update the global.properties property within redback.properties to the correct file path')
                sys.exit()
            global_properties=baseFile
        log.info('Loading global configuration from file: ' + global_properties)
        addPropertiesFromFile(props, global_properties, site_home)
    
    if cfg_file:
        addPropertiesFromFile(props, cfg_file, site_home)
    
    if extra_props:
        props.putAll(extra_props)
		
	# resolve property level inheritance and iterations
    log.debug('Attempting to resolve property level inheritance')
    enum = props.keys()
    while enum.hasMoreElements():
        key = enum.nextElement()
        value = props.getProperty(key)
        # Check for property level inheritance
        if re.search(r"\.base$", key) is not None:				
            prop_to_inherit = value
            prop_to_extend = key[:-5]
            log.debug('Inheriting the properties from the ' + prop_to_inherit + ' section in to the section ' + prop_to_extend)
            # Iterate the properties again looking for a match on properties to inherit
            enum_inner = props.keys()
            while enum_inner.hasMoreElements():
                key_inner = enum_inner.nextElement()
                value_inner = props.getProperty(key_inner)
                log.debug('Checking key_inner [' + key_inner + '] matches ' + prop_to_inherit)
                if String.startsWith(String(key_inner),String(prop_to_inherit)):
                    new_property = prop_to_extend + String.substring(key_inner, len(prop_to_inherit))					
                    # Don't override the property if it has already been defined earlier
                    if props.getProperty(new_property) is None:
                        log.debug('Setting inherited property ' + new_property + ' to value ' + value_inner)
                        inherited_props.setProperty(new_property, value_inner)
                        addDataLinage(key,cfg_file,value_inner)
            # Remove the key that defines the base, just keeps us consistant with the template behaviours
            log.debug("About to remove key " + key)
            props.remove(key)
                        
    props.putAll(inherited_props)
    
    log.debug('Attempting to resolve iterations')
    enum = props.keys()
    while enum.hasMoreElements():			
        key = enum.nextElement()
        value = props.getProperty(key)				
        # Check for property set iterations
        if re.search(r"\.iterate$", key) is not None:
            iteration_key = key            
            iteration_set = eval(value)
            prop_to_iterate = key[:-9]
            log.debug('Iterating the properties from the ' + prop_to_iterate + ' section')
            # Iterate the properties again looking for a match on properties to iterate
            enum_inner = props.keys()
            while enum_inner.hasMoreElements():
                key_inner = enum_inner.nextElement()
                value_inner = props.getProperty(key_inner)
                # if the string is part of the set but not the actual iterator then we will check it
                if String.startsWith(String(key_inner),String(prop_to_iterate)) and key_inner != iteration_key:
                    log.debug('Checking if the key [' + key_inner + '] or value = ' + value_inner + ' contains an iterator ')
                    contains_iterator = 0
                    iterated_key = String(key_inner)
                    iterated_value = String(value_inner)
					
                    if String.indexOf(String(key_inner),"%") > -1:
                        log.debug(key_inner + ' contains an iterator, replacing it')						
                        contains_iterator = 1

                    if String.indexOf(String(value_inner),"%") > -1:
                        log.debug(value_inner + ' contains an iterator, replacing it')	
                        contains_iterator = 1											
					                                       
                    for i in iteration_set:
                        iterated_key = String.replaceAll(String(key_inner),"\%",str(i))
                        iterated_value = String.replaceAll(String(value_inner),"\%",str(i))	
						
                        # Don't override the property if it has already been defined earlier
                        if props.getProperty(iterated_key) is None:
                            log.debug('Setting iterated property ' + iterated_key + ' to value ' + iterated_value)
                            iterated_props.setProperty(iterated_key, iterated_value)
                            addDataLinage(key,cfg_file,iterated_value)
					
                    # Remove the key that gets iterated, just keeps us consistant with the template behaviours
                    if (contains_iterator == 1):
                        log.debug('About to remove ' + key_inner)
                        props.remove(key_inner)
                        
            # Remove the key that defines the iterations, just keeps us consistant with the template behaviours
            props.remove(iteration_key)
	
	# Add the iterated properties back in to the main set    
    props.putAll(iterated_props)
	
    # resolve embedded references
    enum = props.keys()
    while enum.hasMoreElements():
        key = enum.nextElement()
        value = props.getProperty(key)
        if not value is None and len(value) > 0:
            if re.search(r"\$\{(.*?)\}", value) is not None:
                resolvedValue = resolveProperty(key, props)
                if resolvedValue is None:
                    raise Exception('unable to resolve property: ' + key + '=' + value)
                else:
                    props.setProperty(key, resolvedValue)
                    addDataLinage(key,cfg_file,resolvedValue)   
    
    # remove any properties that start with base (assumed that these are baseline properties that have been inherited
    enum = props.keys()
    while enum.hasMoreElements():
        key = enum.nextElement()
        if String.startsWith(String(key),'base.'):
            props.remove(key)
    
    decryptAllPasswords(cfg_file,props)

    return props
    

def createEmpty():
    return Properties()
