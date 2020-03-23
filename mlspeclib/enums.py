from enum import Enum, auto

class ConnectionTypes(Enum):
    CUSTOM = auto()
    AWS_BLOB = auto() # AWS Blob
    GCP_BLOB = auto() # Google Cloud Blob
    AZURE_BLOB = auto() # Azure Blob Storage
    NFS_BLOB = auto() # NFS Blob Storage
    SMB_BLOB = auto() # Samba Blob Storage
