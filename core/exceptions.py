class SiteAnalyzerException(Exception):
    """Base exception for site analyzer"""
    pass

class EnumerationException(SiteAnalyzerException):
    """Exception during enumeration process"""
    pass

class StorageException(SiteAnalyzerException):
    """Exception during storage operations"""
    pass

class ConfigurationException(SiteAnalyzerException):
    """Exception in configuration"""
    pass

class APIException(SiteAnalyzerException):
    """Exception in external API calls"""
    pass
