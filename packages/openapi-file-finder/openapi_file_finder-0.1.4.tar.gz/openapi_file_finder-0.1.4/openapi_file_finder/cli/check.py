from __future__ import annotations

import typer
from rich.console import Console

from .utils import run_async
from openapi_file_finder.specification import check_repository_apiblueprint_usage
from openapi_file_finder.specification import check_repository_apiblueprint_usage_async
from openapi_file_finder.specification import check_repository_swagger_php_usage
from openapi_file_finder.specification import check_repository_swagger_php_usage_async
from openapi_file_finder.specification.composer import check_apiblueprint_dependency_in_repo
from openapi_file_finder.specification.composer import check_dedoc_scramble_in_repo
from openapi_file_finder.specification.composer import check_swagger_php_dependency_in_repo

console = Console()


def check_swagger_php(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the PHP repository to scan',
    ),
    use_async: bool = typer.Option(
        False, '--async', help='Use async implementation.',
    ),
    log_level: str | None = typer.Option(
        'info', '--log-level', help='Set log level (debug, info, warning, error)',
    ),
):
    """
    Check if swagger-php annotations are used in the repository.
    """
    import structlog
    logger = structlog.get_logger()
    if use_async:
        result = run_async(check_repository_swagger_php_usage_async(repo_path))
    else:
        result = check_repository_swagger_php_usage(repo_path)
    if result:
        console.print(
            '[bold green]swagger-php annotations detected.[/bold green]',
        )
        logger.info('swagger_php_found')
    else:
        console.print(
            '[bold yellow]No swagger-php annotations detected.[/bold yellow]',
        )
        logger.info('swagger_php_not_found')


def check_apiblueprint(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the PHP repository to scan',
    ),
    use_async: bool = typer.Option(
        False, '--async', help='Use async implementation.',
    ),
    log_level: str | None = typer.Option(
        'info', '--log-level', help='Set log level (debug, info, warning, error)',
    ),
):
    """
    Check if API Blueprint annotations are used in the repository.
    """
    import structlog
    logger = structlog.get_logger()
    if use_async:
        result = run_async(
            check_repository_apiblueprint_usage_async(repo_path),
        )
    else:
        result = check_repository_apiblueprint_usage(repo_path)
    if result:
        console.print(
            '[bold green]API Blueprint annotations detected.[/bold green]',
        )
        logger.info('apiblueprint_found')
    else:
        console.print(
            '[bold yellow]No API Blueprint annotations detected.[/bold yellow]',
        )
        logger.info('apiblueprint_not_found')


def check_dedoc_scramble(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the repository to scan for dedoc/scramble dependency',
    ),
    log_level: str | None = typer.Option(
        'info', '--log-level', help='Set log level (debug, info, warning, error)',
    ),
):
    """
    Check if dedoc/scramble dependency is used in composer.json files.
    """
    import structlog
    logger = structlog.get_logger()

    result = check_dedoc_scramble_in_repo(repo_path)

    if result:
        console.print(
            '[bold green]dedoc/scramble dependency found in composer.json files:[/bold green]',
        )
        for file_path in result:
            console.print(f'  - {file_path}')
        logger.info('dedoc_scramble_found', files=result)
    else:
        console.print(
            '[bold yellow]No dedoc/scramble dependency found in composer.json files.[/bold yellow]',
        )
        logger.info('dedoc_scramble_not_found')


def check_composer_swagger_php(
        repo_path: str = typer.Argument(
            ...,
            help='Path to the repository to scan for composer swagger-php dependency',
        ),
        log_level: str | None = typer.Option(
            'info', '--log-level', help='Set log level (debug, info, warning, error)',
        ),
):
    """Check if zircote/swagger-php is required in composer.json files."""
    import structlog
    logger = structlog.get_logger()
    result = check_swagger_php_dependency_in_repo(repo_path)
    if result:
        console.print(
            '[bold green]zircote/swagger-php dependency found in composer.json files:[/bold green]',
        )
        for file_path in result:
            console.print(f'  - {file_path}')
        logger.info('composer_swagger_php_found', files=result)
    else:
        console.print(
            '[bold yellow]No zircote/swagger-php dependency found in composer.json files.[/bold yellow]',
        )
        logger.info('composer_swagger_php_not_found')


def check_composer_apiblueprint(
        repo_path: str = typer.Argument(
            ...,
            help='Path to the repository to scan for composer apiblueprint dependency',
        ),
        log_level: str | None = typer.Option(
            'info', '--log-level', help='Set log level (debug, info, warning, error)',
        ),
):
    """Check if apiaryio/api-blueprint is required in composer.json files."""
    import structlog
    logger = structlog.get_logger()
    result = check_apiblueprint_dependency_in_repo(repo_path)
    if result:
        console.print(
            '[bold green]apiaryio/api-blueprint dependency found in composer.json files:[/bold green]',
        )
        for file_path in result:
            console.print(f'  - {file_path}')
        logger.info('composer_apiblueprint_found', files=result)
    else:
        console.print(
            '[bold yellow]No apiaryio/api-blueprint dependency found in composer.json files.[/bold yellow]',
        )
        logger.info('composer_apiblueprint_not_found')
