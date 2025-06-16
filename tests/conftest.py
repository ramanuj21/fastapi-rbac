# tests/conftest.py

import pytest
import logging
from rbac.manager import RBACManager
from rbac.storage import InMemoryStorage

# Configure logging for all tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

@pytest.fixture
def rbac():
    return RBACManager(InMemoryStorage())
