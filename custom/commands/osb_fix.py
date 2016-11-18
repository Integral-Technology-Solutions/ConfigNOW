def run(cfg):
    
    """OSB Fix to deal with 11.1.1.5+ requirements"""
    
    username=cfg.getProperty('wls.admin.username')
    password=cfg.getProperty('wls.admin.password')
    admin=cfg.getProperty('osb.as.host')
    port=cfg.getProperty('wls.admin.listener.port')
    urladmin=admin + ":" + port
    
    
    connect(username, password, urladmin)
    edit()
    cd('/AppDeployments/ALSB Cluster Singleton Marker Application')
    startEdit()
    set('Targets',jarray.array([ObjectName('com.bea:Name=osb_cluster,Type=Cluster')], ObjectName))
    
    cd('/AppDeployments/ALSB Domain Singleton Marker Application')
    set('Targets',jarray.array([ObjectName('com.bea:Name=osb_cluster,Type=Cluster')], ObjectName))

    activate()
