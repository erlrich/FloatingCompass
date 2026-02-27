def classFactory(iface):
    from .floating_protractor_plugin import FloatingProtractorPlugin
    return FloatingProtractorPlugin(iface)
