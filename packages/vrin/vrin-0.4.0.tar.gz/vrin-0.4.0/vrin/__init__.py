"""
VRIN Hybrid RAG SDK v0.4.0 - Enterprise Hybrid Cloud Architecture
Enterprise-grade Hybrid RAG SDK with multi-cloud deployment support and provider abstraction.

New in v0.4.0:
- 🌩️ Multi-cloud deployment support (AWS, Azure, GCP, on-premise)
- 🔧 Database provider abstraction (Neptune, Cosmos DB, JanusGraph) 
- 🧠 LLM provider abstraction (OpenAI, Azure OpenAI, custom models)
- ⚙️ Configuration-driven architecture for enterprise flexibility
- 🔒 VPC isolation and hybrid connectivity options
- 🤖 Intelligent hybrid agents with data classification and routing
- 📊 Compliance-aware processing (GDPR, HIPAA, SOX, PCI-DSS)
- 🔍 Automatic sensitivity detection and private infrastructure routing
- 📋 Configuration validation and health monitoring
- 🔄 Backward compatibility with existing deployments

Existing Features:
- 🧠 Multi-hop reasoning across documents with strategic insights  
- 🔄 Cross-document synthesis and pattern recognition
- 🎯 User-customizable domain specialization (legal, finance, M&A, etc.)
- ⚡ Expert-level analysis comparable to industry professionals
- 📊 Advanced fact extraction with confidence scoring
- 🔍 Sub-3s query response times for complex reasoning
- 📈 Enterprise-ready with user isolation and authentication

Example usage:
    from vrin import VRINClient, get_enterprise_client, create_enterprise_client
    
    # Standard deployment (general users)
    client = VRINClient(api_key="vrin_4926d56cff3a2adc")
    
    # Smart client selection (recommended)
    client = get_enterprise_client(api_key="vrin_ent_hybrid_abc123")  # Returns VRINEnterpriseClient
    client = get_enterprise_client(api_key="vrin_4926d56cff3a2adc")   # Returns VRINClient
    
    # Enterprise client with explicit routing control
    enterprise_client = create_enterprise_client(
        api_key="vrin_ent_hybrid_myorg_xyz789",
        config={
            "database_provider": "neptune",
            "llm_provider": "openai",
            "deployment_mode": "hybrid_explicit"
        }
    )
    
    # Insert with explicit processing location (enterprise only)
    result = enterprise_client.insert(
        content="Sensitive legal document...",
        processing_location="private"  # Client controls routing
    )
    
    # Query with processing location control  
    response = enterprise_client.query(
        "Analyze confidential data",
        processing_location="private"  # Always in client's infrastructure
    )
    
    # Get deployment information
    info = enterprise_client.get_deployment_info()
    print(f"Deployment mode: {info['deployment_mode']}")
    print(f"Database: {info['configuration']['database_provider']}")
    print(f"Capabilities: {info['capabilities']}")
    
    # Validate enterprise configuration
    validation = enterprise_client.validate_configuration()
    if validation['valid']:
        print("✅ Enterprise configuration validated")
"""

# Core client (backward compatibility)
from .client import VRINClient

# Enterprise client (consolidated from v2 and v3)
def get_enterprise_client(api_key: str, **kwargs):
    """
    Factory function to get appropriate client based on API key.
    
    Args:
        api_key: VRIN API key
        **kwargs: Additional configuration parameters
        
    Returns:
        VRINClient for general keys (vrin_*)
        VRINEnterpriseClient for enterprise keys (vrin_ent_*)
    """
    if api_key.startswith("vrin_ent_"):
        # Import enterprise client only when needed
        from .enterprise import VRINEnterpriseClient
        return VRINEnterpriseClient(api_key, **kwargs)
    else:
        # Use standard client for general API keys
        return VRINClient(api_key, **kwargs)

# Enterprise features - loaded conditionally
try:
    # Enterprise client and factories
    from .enterprise import (
        VRINEnterpriseClient,
        create_enterprise_client,
        create_air_gapped_client,
        create_vpc_isolated_client,
        create_hybrid_client
    )
    
    # Configuration and validation
    from .config import VRINConfig, ConfigManager, DeploymentMode, DatabaseProvider, LLMProvider
    from .validation import validate_and_test_config, ConfigValidator, ConfigTester
    
    # Provider abstractions
    from .providers.factory import ProviderManager
    
    # Legacy factory functions for backward compatibility
    def create_centralized_client(api_key: str, **kwargs):
        """Create standard VRIN client (legacy compatibility)."""
        return VRINClient(api_key, **kwargs)
    
    def create_hybrid_aws_client(**kwargs):
        """Create hybrid AWS client (legacy compatibility)."""
        api_key = kwargs.pop('api_key', None) or kwargs.pop('enterprise_api_key', None)
        if not api_key:
            raise ValueError("api_key or enterprise_api_key required")
        return VRINEnterpriseClient(api_key, config=kwargs)
    
    def create_hybrid_azure_client(**kwargs):
        """Create hybrid Azure client (legacy compatibility)."""
        api_key = kwargs.pop('api_key', None) or kwargs.pop('enterprise_api_key', None)
        if not api_key:
            raise ValueError("api_key or enterprise_api_key required")
        return VRINEnterpriseClient(api_key, config=kwargs)
    
    _ENTERPRISE_FEATURES_AVAILABLE = True
    
except ImportError as e:
    # Enterprise features not available - fall back to basic client only
    _ENTERPRISE_FEATURES_AVAILABLE = False
    VRINEnterpriseClient = None
    create_enterprise_client = None
    create_air_gapped_client = None  
    create_vpc_isolated_client = None
    create_hybrid_client = None
    create_centralized_client = lambda api_key, **kwargs: VRINClient(api_key, **kwargs)
    create_hybrid_aws_client = None
    create_hybrid_azure_client = None

# Legacy imports for backward compatibility
from .models import Document, QueryResult, JobStatus
from .exceptions import VRINError, JobFailedError, TimeoutError

__version__ = "0.4.0"
__author__ = "VRIN Team"
__email__ = "support@vrin.ai"

__all__ = [
    # Core client (always available)
    "VRINClient",
    
    # Smart client factory
    "get_enterprise_client",
    
    # Data models
    "Document", 
    "QueryResult",
    "JobStatus",
    
    # Exceptions
    "VRINError",
    "JobFailedError", 
    "TimeoutError",
    
    # Basic factory function (always available)
    "create_centralized_client"
]

# Add enterprise features if available
if _ENTERPRISE_FEATURES_AVAILABLE:
    __all__.extend([
        # Enterprise client and factories
        "VRINEnterpriseClient",
        "create_enterprise_client", 
        "create_air_gapped_client",
        "create_vpc_isolated_client",
        "create_hybrid_client",
        
        # Legacy enterprise factories
        "create_hybrid_aws_client", 
        "create_hybrid_azure_client",
        
        # Enterprise configuration
        "VRINConfig", "ConfigManager", "DeploymentMode", "DatabaseProvider", "LLMProvider",
        
        # Validation and testing
        "validate_and_test_config", "ConfigValidator", "ConfigTester",
        
        # Provider management
        "ProviderManager"
    ]) 