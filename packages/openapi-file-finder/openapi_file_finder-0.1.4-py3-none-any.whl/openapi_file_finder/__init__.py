"""
openapi_file_finder: Tools for finding and validating OpenAPI/Swagger/API Blueprint specifications in codebases.
"""
from __future__ import annotations

from .specification import composer as composer
# Re-export composer dependency checking functions as public API

__all__ = [
    # Module export for namespacing
    'composer',
    # Back-compat explicit functions
    'has_dedoc_scramble_dependency',
    'find_composer_json_files',
    'check_dedoc_scramble_in_repo',
    'has_swagger_php_dependency',
    'has_apiblueprint_dependency',
    'check_swagger_php_dependency_in_repo',
    'check_apiblueprint_dependency_in_repo',
]

# Populate explicit function names for direct import style
from .specification.composer import (
    has_dedoc_scramble_dependency,
    find_composer_json_files,
    check_dedoc_scramble_in_repo,
    has_swagger_php_dependency,
    has_apiblueprint_dependency,
    check_swagger_php_dependency_in_repo,
    check_apiblueprint_dependency_in_repo,
)
