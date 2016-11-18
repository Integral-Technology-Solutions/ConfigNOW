def run(cfg):
    """JMS Fix to deal with 11.1.1.5+ requirements"""
    domainPath=cfg.getProperty('wls.domain.dir')
    domainName=cfg.getProperty('wls.domain.name')
    domainFullPath=str(domainPath) + '/' + str(domainName)
    try:
	readDomain(domainFullPath)
	cd('/JMSSystemResource/jmsResources/JmsResource/NO_NAME_0')
	delete('dist_wli.reporting.purge.queue_auto_1_auto','DistributedQueue')
	
    except Exception, error:
        log.error('Unable to update domain [' + domainFullPath + ']')
        raise error
    else:
        updateDomain()
        closeDomain()