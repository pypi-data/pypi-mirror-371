"""All builtin sources."""

from . import op
from .auth_registry import TransientAuthEntryReference
import datetime


class LocalFile(op.SourceSpec):
    """Import data from local file system."""

    _op_category = op.OpCategory.SOURCE

    path: str
    binary: bool = False

    # If provided, only files matching these patterns will be included.
    # See https://docs.rs/globset/latest/globset/index.html#syntax for the syntax of the patterns.
    included_patterns: list[str] | None = None

    # If provided, files matching these patterns will be excluded.
    # See https://docs.rs/globset/latest/globset/index.html#syntax for the syntax of the patterns.
    excluded_patterns: list[str] | None = None


class GoogleDrive(op.SourceSpec):
    """Import data from Google Drive."""

    _op_category = op.OpCategory.SOURCE

    service_account_credential_path: str
    root_folder_ids: list[str]
    binary: bool = False
    recent_changes_poll_interval: datetime.timedelta | None = None


class AmazonS3(op.SourceSpec):
    """Import data from an Amazon S3 bucket. Supports optional prefix and file filtering by glob patterns."""

    _op_category = op.OpCategory.SOURCE

    bucket_name: str
    prefix: str | None = None
    binary: bool = False
    included_patterns: list[str] | None = None
    excluded_patterns: list[str] | None = None
    sqs_queue_url: str | None = None


class AzureBlob(op.SourceSpec):
    """
    Import data from an Azure Blob Storage container. Supports optional prefix and file filtering by glob patterns.

    Authentication mechanisms taken in the following order:
    - SAS token (if provided)
    - Account access key (if provided)
    - Default Azure credential
    """

    _op_category = op.OpCategory.SOURCE

    account_name: str
    container_name: str
    prefix: str | None = None
    binary: bool = False
    included_patterns: list[str] | None = None
    excluded_patterns: list[str] | None = None

    sas_token: TransientAuthEntryReference[str] | None = None
    account_access_key: TransientAuthEntryReference[str] | None = None
