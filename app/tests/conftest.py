import os
import pytest # noqa: F401

# -----------------------------
# Set DATABASE_URL before importing app modules
# -----------------------------
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

