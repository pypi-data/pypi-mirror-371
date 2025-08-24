import os
import shutil

import pytest
from django.conf import settings
from django.test import override_settings as override_django_settings
from pytest_uncollect_if import uncollect_if


def composed(*decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f

    return deco


S3_STORAGE_BACKEND = "storages.backends.s3.S3Storage"
S3_STATIC_STORAGE_BACKEND = "storages.backends.s3.S3StaticStorage"
S3_MANIFEST_STATIC_STORAGE_BACKEND = "storages.backends.s3.S3ManifestStaticStorage"
S3_CUSTOM_MANIFEST_STATIC_STORAGE_BACKEND = (
    "collectfasta.tests.utils.S3ManifestCustomStaticStorage"
)

GOOGLE_CLOUD_STORAGE_BACKEND = "collectfasta.tests.utils.GoogleCloudStorageTest"
AZURE_BLOB_STORAGE_BACKEND = "collectfasta.tests.utils.AzureBlobStorageTest"
FILE_SYSTEM_STORAGE_BACKEND = "django.core.files.storage.FileSystemStorage"

BOTO3_STRATEGY = "collectfasta.strategies.boto3.Boto3Strategy"
BOTO3_MANIFEST_MEMORY_STRATEGY = (
    "collectfasta.strategies.boto3.Boto3ManifestMemoryStrategy"
)
BOTO3_MANIFEST_FILE_SYSTEM_STRATEGY = (
    "collectfasta.strategies.boto3.Boto3ManifestFileSystemStrategy"
)
GOOGLE_CLOUD_STRATEGY = "collectfasta.strategies.gcloud.GoogleCloudStrategy"
AZURE_BLOB_STRATEGY = "collectfasta.strategies.azure.AzureBlobStrategy"
FILE_SYSTEM_STRATEGY = "collectfasta.strategies.filesystem.FileSystemStrategy"
CACHING_FILE_SYSTEM_STRATEGY = (
    "collectfasta.strategies.filesystem.CachingFileSystemStrategy"
)

S3_BACKENDS = [
    S3_STORAGE_BACKEND,
    S3_STATIC_STORAGE_BACKEND,
    S3_MANIFEST_STATIC_STORAGE_BACKEND,
    S3_CUSTOM_MANIFEST_STATIC_STORAGE_BACKEND,
]
BACKENDS = [
    *S3_BACKENDS,
    GOOGLE_CLOUD_STORAGE_BACKEND,
    AZURE_BLOB_STORAGE_BACKEND,
    FILE_SYSTEM_STORAGE_BACKEND,
]

STRATEGIES = [
    BOTO3_STRATEGY,
    BOTO3_MANIFEST_MEMORY_STRATEGY,
    BOTO3_MANIFEST_FILE_SYSTEM_STRATEGY,
    GOOGLE_CLOUD_STRATEGY,
    AZURE_BLOB_STRATEGY,
    FILE_SYSTEM_STRATEGY,
    CACHING_FILE_SYSTEM_STRATEGY,
]

COMPATIBLE_STRATEGIES_FOR_BACKENDS = {
    S3_STORAGE_BACKEND: [BOTO3_STRATEGY],
    S3_STATIC_STORAGE_BACKEND: [BOTO3_STRATEGY],
    S3_MANIFEST_STATIC_STORAGE_BACKEND: [
        BOTO3_STRATEGY,
        BOTO3_MANIFEST_MEMORY_STRATEGY,
        BOTO3_MANIFEST_FILE_SYSTEM_STRATEGY,
    ],
    S3_CUSTOM_MANIFEST_STATIC_STORAGE_BACKEND: [
        BOTO3_STRATEGY,
        BOTO3_MANIFEST_MEMORY_STRATEGY,
        BOTO3_MANIFEST_FILE_SYSTEM_STRATEGY,
    ],
    GOOGLE_CLOUD_STORAGE_BACKEND: [GOOGLE_CLOUD_STRATEGY],
    AZURE_BLOB_STORAGE_BACKEND: [AZURE_BLOB_STRATEGY],
    FILE_SYSTEM_STORAGE_BACKEND: [FILE_SYSTEM_STRATEGY, CACHING_FILE_SYSTEM_STRATEGY],
}


def two_n_plus_1(files):
    return files * 2 + 1


def n(files):
    return files


def short_name(backend, strategy):
    return f"{backend.split('.')[-1]}:{strategy.split('.')[-1]}"


def params_for_backends():
    for backend in BACKENDS:
        for strategy in COMPATIBLE_STRATEGIES_FOR_BACKENDS[backend]:
            yield pytest.param(
                (backend, strategy),
                marks=[pytest.mark.backend(backend), pytest.mark.strategy(strategy)],
                id=short_name(backend, strategy),
            )


class StrategyFixture:
    def __init__(self, expected_copied_files, backend, strategy, two_pass):
        self.backend = backend
        self.strategy = strategy
        self.expected_copied_files = expected_copied_files
        self.two_pass = two_pass


@pytest.fixture(params=params_for_backends())
def strategy(request):
    backend, strategy = request.param
    if strategy in (
        BOTO3_MANIFEST_MEMORY_STRATEGY,
        BOTO3_MANIFEST_FILE_SYSTEM_STRATEGY,
    ) and backend in (
        S3_MANIFEST_STATIC_STORAGE_BACKEND,
        S3_CUSTOM_MANIFEST_STATIC_STORAGE_BACKEND,
    ):
        expected_copied_files = two_n_plus_1
    else:
        expected_copied_files = n
    with override_django_settings(
        STORAGES={"staticfiles": {"BACKEND": backend}},
        COLLECTFASTA_STRATEGY=strategy,
    ):
        yield StrategyFixture(
            expected_copied_files,
            backend,
            strategy,
            two_pass=strategy
            in (
                BOTO3_MANIFEST_MEMORY_STRATEGY,
                BOTO3_MANIFEST_FILE_SYSTEM_STRATEGY,
            ),
        )


def uncollect_if_not_s3(strategy: tuple[str, str], **kwargs: dict) -> bool:
    backend, _ = strategy
    return backend not in S3_BACKENDS


def uncollect_if_not_cloud(strategy: tuple[str, str], **kwargs: dict) -> bool:
    backend, _ = strategy
    return (
        backend not in S3_BACKENDS
        and backend != GOOGLE_CLOUD_STORAGE_BACKEND
        and backend != AZURE_BLOB_STORAGE_BACKEND
    )


def uncollect_if_not_azure(strategy: tuple[str, str], **kwargs: dict) -> bool:
    backend, _ = strategy
    return backend not in AZURE_BLOB_STORAGE_BACKEND


live_test = pytest.mark.live_test
speed_test_mark = pytest.mark.speed_test

speed_test = composed(
    live_test,
    speed_test_mark,
    pytest.mark.skipif(
        "not config.getoption('speedtest')",
        reason="no --speedtest flag",
    ),
)

aws_backends_only = uncollect_if(func=uncollect_if_not_s3)
cloud_backends_only = uncollect_if(func=uncollect_if_not_cloud)
azure_backends_only = uncollect_if(func=uncollect_if_not_azure)


def uncollect_if_not_two_pass(strategy: tuple[str, str], **kwargs: dict) -> bool:
    _, strategy_str = strategy
    return strategy_str not in (
        BOTO3_MANIFEST_MEMORY_STRATEGY,
        BOTO3_MANIFEST_FILE_SYSTEM_STRATEGY,
    )


def uncollect_if_two_pass(strategy: tuple[str, str], **kwargs: dict) -> bool:
    return not uncollect_if_not_two_pass(strategy, **kwargs)


two_pass_only = uncollect_if(func=uncollect_if_not_two_pass)
exclude_two_pass = uncollect_if(func=uncollect_if_two_pass)


@pytest.fixture(autouse=True)
def create_test_directories():
    paths = (settings.STATICFILES_DIRS[0], settings.STATIC_ROOT, settings.MEDIA_ROOT)
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
    try:
        yield
    finally:
        for path in paths:
            shutil.rmtree(path)
