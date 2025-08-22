"""
Test command for running database tests.
Runs database tests with dot notation support for specific tests.
"""
import os
import sys
import unittest
import asyncio
from typing import List, Optional, Tuple


class Command:
    """Test command class for running database tests."""

    def __init__(self):
        self.help = "Run database tests with dot notation support"

    async def safe_shutdown(self):
        """Safely shutdown database connections with timeout."""
        try:
            from neutronapi.db import shutdown_all_connections
            await asyncio.wait_for(shutdown_all_connections(), timeout=5)
        except asyncio.TimeoutError:
            print("Warning: Database shutdown timed out, forcing shutdown.")
        except ImportError:
            # No database connections to shut down
            pass
        except Exception as e:
            print(f"Warning: Exception during database shutdown: {e}")

    async def run_forced_shutdown(self):
        """Run shutdown in the current event loop context."""
        await self.safe_shutdown()

    def _bootstrap_sqlite(self):
        # Use in-memory sqlite as the default test DB
        import os
        from neutronapi.db import setup_databases
        os.environ['TESTING'] = '1'  # Ensure ConnectionsManager prefers :memory:
        try:
            from apps.settings import DATABASES  # Optional, if running inside a project
            setup_databases(DATABASES)
            return
        except Exception:
            # Fall back to a guaranteed in-memory configuration even if a manager already exists
            test_config = {
                'default': {
                    'ENGINE': 'aiosqlite',
                    'NAME': ':memory:',
                }
            }
            setup_databases(test_config)

    async def _run_async(self, *cmd: str, timeout: Optional[float] = None) -> Tuple[int, str, str]:
        """Run a subprocess asynchronously and capture output."""
        import asyncio
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            raise
        return proc.returncode, stdout.decode(), stderr.decode()

    async def _bootstrap_postgres(self):
        # Start a disposable PostgreSQL in Docker if available (async)
        import shutil

        self._pg_container = None
        host = os.getenv('PGHOST', '127.0.0.1')
        port = int(os.getenv('PGPORT', '54329'))  # non-standard to avoid clashes
        dbname = os.getenv('PGDATABASE', 'temp_test')
        user = os.getenv('PGUSER', 'postgres')
        password = os.getenv('PGPASSWORD', 'postgres')

        # Check if Docker is available
        docker = shutil.which('docker')
        if not docker:
            print('Docker not found, cannot bootstrap PostgreSQL')
            return False

        try:
            # Check if docker daemon is running
            code, _, _ = await self._run_async(docker, 'info', timeout=5)
            if code != 0:
                print('Docker daemon not running, cannot bootstrap PostgreSQL')
                return False

            # Ensure the required image exists locally to avoid a network pull
            image = 'postgres:15-alpine'
            code, _, _ = await self._run_async(docker, 'image', 'inspect', image, timeout=5)
            if code != 0:
                print(f"Docker image '{image}' not present locally; skipping PostgreSQL bootstrap (no network pulls)")
                return False

            # Check if a container with our name exists; if not, run one
            name = 'neutronapi_test_pg'
            code, out, _ = await self._run_async(docker, 'ps', '-q', '-f', f'name={name}', timeout=5)

            if not out.strip():
                print(f'Starting PostgreSQL container on port {port}...')
                code, _, err = await self._run_async(
                    docker, 'run', '-d', '--rm', '--name', name,
                    '-e', f'POSTGRES_PASSWORD={password}',
                    '-e', f'POSTGRES_DB={dbname}',
                    '-e', f'POSTGRES_USER={user}',
                    '-p', f'{port}:5432',
                    image,
                    timeout=20,
                )
                if code == 0:
                    self._pg_container = name
                    print(f'PostgreSQL container started: {name}')
                else:
                    print(f'Failed to start PostgreSQL container: {err.strip()}')
                    return False
            else:
                self._pg_container = name
                print(f'Using existing PostgreSQL container: {name}')

        except asyncio.TimeoutError:
            print('Docker command timed out during PostgreSQL bootstrap')
            return False
        except Exception as e:
            print(f"Error with Docker: {e}")
            return False

        # Wait for PostgreSQL to be ready
        print('Waiting for PostgreSQL to be ready...')
        try:
            import asyncpg

            async def _wait_ready():
                for i in range(60):  # Wait up to 15 seconds
                    try:
                        conn = await asyncpg.connect(
                            host=host, port=port, database=dbname, user=user, password=password
                        )
                        await conn.close()
                        return True
                    except Exception:
                        if i % 4 == 0:  # Print every second
                            print(f'  Waiting for PostgreSQL... ({i // 4 + 1}s)')
                        await asyncio.sleep(0.25)
                return False

            ready = await _wait_ready()
            if not ready:
                print('PostgreSQL failed to become ready in time')
                return False

        except Exception as e:
            print(f"Error waiting for PostgreSQL: {e}")
            return False

        # Configure environment for tests
        try:
            os.environ['TESTING'] = '1'
            os.environ['PGHOST'] = host
            os.environ['PGPORT'] = str(port)
            os.environ['PGDATABASE'] = dbname
            os.environ['PGUSER'] = user
            os.environ['PGPASSWORD'] = password

            # Force database system to use the new config
            from neutronapi.db import setup_databases
            test_config = {
                'default': {
                    'ENGINE': 'asyncpg',
                    'HOST': host,
                    'PORT': port,
                    'NAME': dbname,
                    'USER': user,
                    'PASSWORD': password,
                }
            }
            setup_databases(test_config)

            print(f'✓ PostgreSQL ready at {host}:{port}/{dbname}')
            return True

        except Exception as e:
            print(f"Error configuring PostgreSQL: {e}")
            return False

    async def _teardown_postgres(self):
        # Stop the disposable postgres container if we started it
        import shutil
        if getattr(self, '_pg_container', None):
            docker = shutil.which('docker')
            if docker:
                try:
                    await self._run_async(docker, 'stop', self._pg_container, timeout=10)
                except Exception:
                    pass

    async def handle(self, args: List[str]) -> int:
        """
        Run database tests with dot notation support.

        Usage:
            python manage.py test                    # Run all tests
            python manage.py test core.tests        # Run specific module tests
            python manage.py test core.tests.db.test_db.TestModel.test_creation  # Specific test
            python manage.py test --help            # Show help

        Examples:
            python manage.py test
            python manage.py test core.tests.db.test_db
            python manage.py test core.tests.db.test_db.TestModel.test_creation
        """

        # Show help if requested
        if args and args[0] in ["--help", "-h", "help"]:
            print(f"{self.help}\n")
            print(self.handle.__doc__)
            return

        # No project-specific env flags; keep behavior generic

        # Bootstrap test databases
        provider_env = os.getenv('DATABASE_PROVIDER', '').lower().strip()
        if provider_env in ('asyncpg', 'postgres', 'postgresql'):
            print('Bootstrapping PostgreSQL test database...')
            try:
                success = await self._bootstrap_postgres()
            except Exception:
                success = False
            if not success:
                print('Failed to bootstrap PostgreSQL, falling back to SQLite')
                self._bootstrap_sqlite()
        else:
            print('Bootstrapping SQLite in-memory test database...')
            self._bootstrap_sqlite()

        # Apply project migrations (if any) using the file-based tracker
        async def apply_project_migrations():
            try:
                base_dir = os.path.join(os.getcwd(), 'apps')
                if not os.path.isdir(base_dir):
                    return
                # Quick check: any migrations directory with numbered files?
                found_any = False
                for app_name in os.listdir(base_dir):
                    mig_dir = os.path.join(base_dir, app_name, 'migrations')
                    if os.path.isdir(mig_dir):
                        for fn in os.listdir(mig_dir):
                            if fn.endswith('.py') and fn[:3].isdigit():
                                found_any = True
                                break
                    if found_any:
                        break
                if not found_any:
                    return

                from neutronapi.db.migration_tracker import MigrationTracker
                from neutronapi.db.connection import get_databases
                tracker = MigrationTracker(base_dir='apps')
                connection = await get_databases().get_connection('default')
                await tracker.migrate(connection)
                print('✓ Applied project migrations for tests')
            except Exception as e:
                print(f"Warning: Failed to apply project migrations: {e}")

        try:
            await apply_project_migrations()
        except Exception:
            pass

        # Bootstrap internal test models (used by this package's own tests)
        async def bootstrap_test_models():
            try:
                from neutronapi.db.migrations import CreateModel
                from neutronapi.db.connection import get_databases
                
                # Try to discover test models from neutronapi.tests.db
                try:
                    from neutronapi.tests.db.test_models import TestUser
                    from neutronapi.tests.db.test_queryset import TestObject
                    
                    test_models = [TestUser, TestObject]
                    
                    # Create tables for test models using migrations
                    connection = await get_databases().get_connection('default')
                    
                    for model_cls in test_models:
                        create_operation = CreateModel(f'neutronapi.{model_cls.__name__}', model_cls._fields)
                        await create_operation.database_forwards(
                            app_label='neutronapi',
                            provider=connection.provider,
                            from_state=None,
                            to_state=None,
                            connection=connection
                        )
                    
                    print(f"✓ Bootstrapped {len(test_models)} internal test models")
                    
                except ImportError as e:
                    print(f"Note: Test models not found, skipping bootstrap: {e}")
                except Exception as e:
                    print(f"Warning: Failed to bootstrap test models: {e}")
                    
            except Exception as e:
                print(f"Warning: Could not bootstrap test models: {e}")
        
        # Run the bootstrap
        try:
            await bootstrap_test_models()
        except Exception as e:
            print(f"Error during test model bootstrap: {e}")

        print("Running tests...")

        exit_code = 0
        try:
            loader = unittest.TestLoader()
            # Basic flags handling: -q quiet, -v verbose
            verbosity = 2
            filtered_args: List[str] = []
            use_coverage = False
            cov = None
            for a in args:
                if a in ("-q", "--quiet"):
                    verbosity = 1
                elif a in ("-v", "--verbose"):
                    verbosity = 2
                elif a in ("--cov", "--coverage"):
                    use_coverage = True
                else:
                    filtered_args.append(a)

            runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stderr)
            suite = unittest.TestSuite()

            # Start coverage if requested or env flag set
            if use_coverage or os.getenv('COVERAGE', 'false').lower() == 'true':
                try:
                    import coverage
                    cov = coverage.Coverage(source=["core"], branch=True)
                    cov.start()
                except Exception as e:
                    print(f"Warning: coverage not started: {e}")

            def path_to_module(arg: str) -> str:
                # Convert a filesystem path to dotted module path
                if arg.endswith(".py"):
                    arg = arg[:-3]
                arg = arg.lstrip("./")
                return arg.replace(os.sep, ".")

            def add_target(target: str):
                # If target is an app label (directory in apps/ or 'core')
                if os.path.isdir(os.path.join("apps", target, "tests")):
                    discovered = loader.discover(os.path.join("apps", target, "tests"), pattern="test_*.py")
                    suite.addTests(discovered)
                    return
                if target == "core" and (os.path.isdir("core/tests") or os.path.isdir("neutronapi/tests")):
                    test_root = "core/tests" if os.path.isdir("core/tests") else "neutronapi/tests"
                    discovered = loader.discover(test_root, pattern="test_*.py")
                    suite.addTests(discovered)
                    return

                # If it's a file system path
                if os.path.exists(target) and target.endswith(".py"):
                    module_name = path_to_module(target)
                    suite.addTests(loader.loadTestsFromName(module_name))
                    return

                # Otherwise, treat as dotted path (module, class, or method)
                suite.addTests(loader.loadTestsFromName(target))

            if filtered_args:
                for target in filtered_args:
                    add_target(target)
            else:
                # Default: discover core and all apps/*/tests
                test_dirs = []

                # Support both legacy core/tests and current neutronapi/tests
                if os.path.isdir("core/tests"):
                    test_dirs.append("core/tests")
                if os.path.isdir("neutronapi/tests"):
                    test_dirs.append("neutronapi/tests")

                if os.path.isdir("apps"):
                    for app_name in os.listdir("apps"):
                        app_tests_dir = os.path.join("apps", app_name, "tests")
                        if os.path.isdir(app_tests_dir):
                            test_dirs.append(app_tests_dir)

                if test_dirs:
                    for test_dir in test_dirs:
                        discovered = loader.discover(test_dir, pattern="test_*.py")
                        suite.addTests(discovered)
                else:
                    suite = loader.discover(".", pattern="test_*.py")

            count = suite.countTestCases()
            if count == 0:
                print("No tests found.")
                return

            print(f"Running {count} test(s)...")
            # Run unittest in a worker thread to avoid event-loop conflicts
            result = await asyncio.to_thread(runner.run, suite)

            if not result.wasSuccessful():
                print(f"\nTests failed: {len(result.failures)} failures, {len(result.errors)} errors")
                exit_code = 1
            else:
                print(f"\nAll {result.testsRun} tests passed!")

        except Exception as e:
            print(f"Error running tests: {e}")
            import traceback
            traceback.print_exc()
            exit_code = 1
        finally:
            print("Closing test environments...")
            # Stop and report coverage if active
            try:
                if cov is not None:
                    cov.stop()
                    cov.save()
                    cov.report()
                    if os.getenv('COV_HTML', 'false').lower() == 'true':
                        cov.html_report(directory='htmlcov')
            except Exception as e:
                print(f"Warning: coverage reporting failed: {e}")
            await self.run_forced_shutdown()
            # Best-effort: stop ephemeral postgres if we started it
            try:
                await self._teardown_postgres()
            except Exception:
                pass
            # Default: hard-exit to ensure full shutdown (no lingering loops/threads)
            # For programmatic callers/tests, set NEUTRONAPI_TEST_RETURN=1 to receive the code instead.
            if os.getenv('NEUTRONAPI_TEST_RETURN', '0') == '1':
                return exit_code
            os._exit(exit_code)
