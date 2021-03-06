from __future__ import print_function
try:
    from builtins import input, range
    import configparser
except ImportError:
    from __builtin__ import input, range
    import ConfigParser as configparser


def create_inventory(m_public='', m_local='', m_name='', key='', token='', nodes=None, **kwargs):
    if m_public != '': master_public = m_public
    if m_local  != '': master_local = m_local
    if m_name   != '': master_name = m_name
    configfile = 'inventory.conf'
    config = configparser.RawConfigParser(allow_no_value=True)
    check = config.read(configfile)
    if check == []:
        print('\nCreating a configuration file...  %s\n' % configfile)
    if not config.has_section('master'):
        config.add_section('master')
        config.set('master', master_public)
    
    if not config.has_section('master:vars'):
        config.add_section('master:vars')
    
    if not config.has_option('master:vars', 'local_host'):
        config.set('master:vars', 'local_host',master_name)
    
    if not config.has_option('master:vars', 'key'):
        config.set('master:vars', 'key',key)
    
    if nodes is not None:
        temp = [{"ip":row[0], "name":row[1]} for row in nodes]
        if config.has_option('master:vars','nodes'):
            list_nodes = eval(config.get('master:vars','nodes'))
            for n in list_nodes:
                temp.append(n)
        config.set('master:vars', 'nodes', str(temp))
    
    #if config.has_section('slaves'):
    #    for item in config.options('slaves'):
    #        config.remove_option('slaves',item)
    if not config.has_section('slaves'):
        config.add_section('slaves')
    if nodes is not None:
        for node in nodes: config.set('slaves', node[1])
    
    if not config.has_section('all:vars'):
        config.add_section('all:vars')
    
    config.set('all:vars', 'ansible_python_interpreter', '/usr/bin/python2.7')
    if not config.has_option('all:vars', 'master_ip'):
        config.set('all:vars', 'master_ip',master_local)
    if not config.has_option('all:vars', 'token'):
        config.set('all:vars', 'token',token)
    
    for key, value in kwargs.iteritems():
        config.set('all:vars', key, value)
    
    with open(configfile,'w') as f:
        config.write(f)
        f.flush()


def get_master_ip():
    configfile = 'inventory.conf'
    config = configparser.RawConfigParser(allow_no_value=True)
    check = config.read(configfile)
    return config.items('master')[0][0]


def update_inventory():
    configfile = 'inventory.conf'
    config = configparser.RawConfigParser(allow_no_value=True)
    check = config.read(configfile)
    old_nodes = config.items('slaves')
    if not config.has_section('slaves-done'):
        config.add_section('slaves-done')
    for option,value in old_nodes:
        config.set('slaves-done',option)
    config.remove_section('slaves')
    config.set('all:vars', 'kube_basics', 'false')
    config.set('all:vars', 'kube_init', 'false')
    config.set('all:vars', 'master_basics', 'false')
    with open(configfile,'w') as f:
        config.write(f)
        f.flush()
    return


