import json
import functools
from .database.model import Session, Project, Trace, Base, engine as default_engine, sessionmaker, TraceTypes
from sqlalchemy import create_engine, inspect, text
from datetime import datetime
from .connect import hora
from typing import Dict, Union
import pytz
import inspect as py_inspect
import threading
import subprocess
import os

# Global registry to track running web interfaces
_web_interface_registry = {
    'api_port': None,
    'api_thread': None,
    'reflex_process': None,
    'container_name': 'novatrace-web',
    'instance_count': 0,
    'interface_enabled': False,
    'interface_started': False
}

class NovaTrace:
    def __init__(self, session_name: str, engine_url: str = None, time_zone: pytz.tzinfo = pytz.utc, interface: bool = True, debug: bool = False):
        """
        Init a new NovaTrace instance.
        Args:
            session_name (str): Name of the session to be created or connected to.
            engine_url (str, optional): SQLAlchemy engine URL. If not provided, defaults to the default engine.
            time_zone (pytz.tzinfo, optional): Time zone for timestamps. Defaults to UTC.
            interface (bool, optional): Whether to start the web interface. Defaults to True.
            debug (bool, optional): Whether to show detailed logs. Defaults to False.
        Raises:
            ValueError: If metadata is not provided or incomplete.
        Returns:
            None
        """
        global _web_interface_registry
        
        try:
            # Original NovaTrace attributes
            self.time_zone = time_zone
            self.interface_enabled = interface
            self.debug = debug
            self.reflex_process = None
            
            # Track this instance
            _web_interface_registry['instance_count'] += 1
            self._instance_id = _web_interface_registry['instance_count']
            
            # Only set up web interface resources for the first interface-enabled instance
            if interface and not _web_interface_registry['interface_enabled']:
                _web_interface_registry['interface_enabled'] = True
                self._is_interface_owner = True
            else:
                self._is_interface_owner = False
            
            if engine_url:
                self.engine = create_engine(engine_url)
            else:
                self.engine = default_engine
            
            # Handle database migration for session_id column
            self._migrate_database_if_needed()
            
            Base.metadata.create_all(self.engine)
            session = sessionmaker(bind=self.engine)

            self.session = session() # Sesion de SQLAlchemy

            for name in ["LLM", "Agent", "Tool"]:
                if not self.session.query(TraceTypes).filter_by(name=name).first():
                    new_type = TraceTypes(name=name)
                    self.session.add(new_type) 
            self.session.commit() # BDD Build

            self.active_session = self.session.query(Session).filter_by(name=session_name).first()

            if not self.active_session:
                self.active_session = Session(name=session_name, created_at=datetime.now(self.time_zone))
                self.session.add(self.active_session)
                self.session.commit()
            self.project = None
            self.provider: str = None
            self.model: str = None
            self.input_cost_per_million_tokens: float = 0.0
            self.output_cost_per_million_tokens: float = 0.0
            self.user_external_id: str = "guest_user"
            self.user_external_name: str = "Guest User"
            
            # Register cleanup only for database session (not web interface)
            self._register_cleanup_handlers()
            
            # Start interface if this instance owns it
            if self._is_interface_owner:
                self._start_web_interface()
                
        except Exception as e:
            print(f"Warning: NovaTrace initialization failed: {e}")
            # Initialize with minimal safe defaults
            self.session = None
            self.project = None
            self.provider = None
            self.model = None
            self.input_cost_per_million_tokens = 0.0
            self.output_cost_per_million_tokens = 0.0
            self.user_external_id = "guest_user"
            self.user_external_name = "Guest User"
            self.interface_enabled = False
            self.debug = False
            self.reflex_process = None
            self._is_interface_owner = False
    
    def _register_cleanup_handlers(self):
        """Register cleanup handlers only for database session"""
        import atexit
        
        # Only register cleanup for database session - NO automatic interface cleanup
        atexit.register(self._cleanup_session)
    
    def _cleanup_session(self):
        """Clean up only the database session"""
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except Exception:
            pass  # Ignore errors in cleanup
    
    def _migrate_database_if_needed(self):
        """Handle database migration for new columns"""
        try:
            # Check if session_id column exists in traces table
            inspector = inspect(self.engine)
            if 'traces' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('traces')]
                if 'session_id' not in columns:
                    # Add session_id column to existing traces table
                    with self.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE traces ADD COLUMN session_id INTEGER"))
                        conn.commit()
                        print("NovaTrace: Added session_id column to traces table")
        except Exception as e:
            print(f"Warning: NovaTrace database migration failed: {e}")
    
    def _start_web_interface(self):
        """
        Start the web interface. Tries React interface first, falls back to Reflex.
        """
        global _web_interface_registry
        
        # Only start if we're the interface owner
        if not self._is_interface_owner:
            return
        
        # Prevent multiple starts
        if _web_interface_registry['interface_started']:
            if self.debug:
                print("   💡 Web interface already started")
            return
        
        _web_interface_registry['interface_started'] = True
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        react_interface_dir = os.path.join(current_dir, "web_interface")
        
        # Store reference in global registry
        _web_interface_registry['reflex_process'] = None
        
        # Check if new React interface exists
        if os.path.exists(react_interface_dir):
            self._start_react_interface()
        else:
            # Fallback to original Reflex interface
            self._start_reflex_interface()
    
    def _start_react_interface(self):
        """
        Start the React web interface using Docker.
        This will start the containerized React app on port 3000.
        """
        global _web_interface_registry
        
        def run_web_interface():
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                web_interface_dir = os.path.join(current_dir, "web_interface")
                
                # Start API server first
                self._start_api_server()
                
                # Check if Docker is available
                try:
                    subprocess.run(["docker", "--version"], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("❌ Docker not found. Please install Docker to use the web interface.")
                    return
                
                # Build Docker image if it doesn't exist
                container_name = _web_interface_registry['container_name']
                image_name = "novatrace-web:latest"
                build_cmd = ["docker", "build", "-t", image_name, "."]
                
                print("🚀 Iniciando NovaTrace con dashboard...")
                
                # Stop existing container if running
                try:
                    subprocess.run(["docker", "stop", container_name], 
                                 capture_output=True, check=False)
                    subprocess.run(["docker", "rm", container_name], 
                                 capture_output=True, check=False)
                except:
                    pass
                
                # Check if image already exists and if we need to rebuild
                image_check = subprocess.run(
                    ["docker", "images", "-q", image_name], 
                    capture_output=True, text=True
                )
                image_exists = bool(image_check.stdout.strip())
                
                # Check if we need to rebuild (dockerfile or entrypoint changed)
                force_rebuild = getattr(self, 'force_rebuild', False)
                if not force_rebuild and image_exists:
                    # Check if entrypoint script exists in the image (simple way to detect old image)
                    inspect_result = subprocess.run([
                        "docker", "run", "--rm", "--entrypoint", "ls", image_name, "/docker-entrypoint.sh"
                    ], capture_output=True, text=True)
                    if inspect_result.returncode != 0:
                        if self.debug:
                            print("   🔄 Detected old Docker image without dynamic port detection")
                        force_rebuild = True
                
                if not image_exists or force_rebuild:
                    if force_rebuild and self.debug:
                        print("   Rebuilding Docker image (with dynamic port detection)...")
                    elif self.debug:
                        print("   Building Docker image (first time)...")
                    
                    if self.debug:
                        print("   ✅ Docker build logs will be shown below:")
                        print("   " + "="*50)
                        build_process = subprocess.Popen(build_cmd, cwd=web_interface_dir)
                    else:
                        build_process = subprocess.Popen(
                            build_cmd, 
                            cwd=web_interface_dir,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    
                    build_process.wait()
                    
                    if build_process.returncode != 0:
                        print("   ❌ Docker build failed")
                        return
                    
                    if self.debug:
                        print("   ✅ Docker image built successfully with dynamic port detection")
                elif self.debug:
                    print("   ✅ Using existing Docker image with dynamic port detection")
                    print("   💡 Image will automatically detect API port at startup")
                
                # Run the Docker container
                run_cmd = [
                    "docker", "run", "-d",
                    "--name", container_name,
                    "-p", "3000:80",
                    "--add-host", "host.docker.internal:host-gateway",
                    image_name
                ]
                
                if self.debug:
                    docker_process = subprocess.Popen(run_cmd, cwd=web_interface_dir)
                else:
                    docker_process = subprocess.Popen(
                        run_cmd, 
                        cwd=web_interface_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                docker_process.wait()
                
                # Store in global registry
                _web_interface_registry['reflex_process'] = docker_process
                
                # Wait a bit for the container to start
                import time
                time.sleep(3)
                
                # Check if container is running
                check_cmd = ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and "Up" in result.stdout:
                    print("   Web interface running at: http://localhost:3000/")
                    if self.debug:
                        print("   📊 Dashboard: http://localhost:3000/")
                        print("   📁 Projects: http://localhost:3000/projects")
                        print("   ⚙️  Settings: http://localhost:3000/settings")
                        print("   💡 Use debug=False to hide detailed logs")
                else:
                    print("   ❌ Container failed to start")
                        
            except Exception as e:
                print(f"Warning: Could not start React web interface: {e}")
                # Fallback to old Reflex interface
                print("   Falling back to legacy Reflex interface...")
                self._start_reflex_interface()
        
        # Start web interface in a separate thread so it doesn't block the main application
        web_thread = threading.Thread(target=run_web_interface, daemon=True)
        web_thread.start()
    
    def _start_reflex_interface(self):
        """
        Start the Reflex web interface in a separate thread.
        This will start both frontend (port 3000) and backend (port 8000).
        """
        def run_reflex():
            try:
                # Change to the web_interface directory where rxconfig.py is located
                current_dir = os.path.dirname(os.path.abspath(__file__))
                web_interface_dir = os.path.join(current_dir, "web_interface_old")
                novatrace_root = os.path.dirname(current_dir)  # Parent directory of novatrace package
                
                # Check if web_interface directory exists
                if not os.path.exists(web_interface_dir):
                    print("❌ Web interface directory not found. Creating basic structure...")
                    return
                
                # Set up environment with correct PYTHONPATH
                env = os.environ.copy()
                env['PYTHONPATH'] = f"{novatrace_root}:{env.get('PYTHONPATH', '')}"
                    
                # Run reflex run command with proper flags
                if self.interface_logs:
                    # Show all logs when interface_logs=True
                    print("🚀 NovaTrace interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                    print("   ✅ All Reflex logs will be shown below:")
                    print("   " + "="*50)
                    
                    # Use no redirection to show all logs
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev", "--loglevel", "debug"],
                        cwd=web_interface_dir,
                        env=env
                    )
                else:
                    # Hide logs when interface_logs=False (default)
                    DEVNULL = subprocess.DEVNULL
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev"],
                        cwd=web_interface_dir,
                        env=env,
                        stdout=DEVNULL,  # Hide stdout logs
                        stderr=DEVNULL,  # Hide stderr logs
                        text=True
                    )
                    print("🚀 NovaTrace interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                
                # Wait a bit for the process to start
                import time
                time.sleep(2)
                
                if self.reflex_process.poll() is None:
                    print("   ✅ App running at: http://localhost:3000/")
                    if not self.interface_logs:
                        print("   💡 Use interface_logs=True to see detailed logs")
                else:
                    print("   ❌ Process failed to start")
                        
            except Exception as e:
                print(f"Warning: Could not start Reflex interface: {e}")
        
        # Start Reflex in a separate thread so it doesn't block the main application
        reflex_thread = threading.Thread(target=run_reflex, daemon=True)
        reflex_thread.start()
    
    def _find_available_port(self, preferred_ports=[4444, 4445, 4446, 4447]):
        """Find an available port from the preferred list"""
        import socket
        
        for port in preferred_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        
        # If none of the preferred ports work, find any available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            return s.getsockname()[1]

    def _kill_process_on_port(self, port):
        """Kill any existing process using the specified port"""
        import subprocess
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                existing_pids = result.stdout.strip().split('\n')
                for pid in existing_pids:
                    if pid:
                        print(f"   🔄 Stopping existing process on port {port} (PID: {pid})")
                        subprocess.run(['kill', '-9', pid], capture_output=True)
                import time
                time.sleep(1)  # Wait for the port to be freed
                return True
        except:
            pass
        return False

    def _start_api_server(self):
        """
        Start the FastAPI server for the web interface.
        This will start the API server on port 4444 or next available port.
        """
        global _web_interface_registry
        
        def run_api_server():
            try:
                # Find available port
                api_port = self._find_available_port()
                _web_interface_registry['api_port'] = api_port
                
                if self.debug:
                    print("🔌 Starting NovaTrace API server...")
                    print(f"   API will be available at: http://localhost:{api_port}")
                    
                    if api_port != 4444:
                        print(f"   💡 Using port {api_port} (4444 was occupied)")
                
                # Import and start FastAPI
                import uvicorn
                from .api import app
                
                # Configure uvicorn to run quietly unless debug=True
                if self.debug:
                    log_level = "info"
                    print("   ✅ API logs will be shown below:")
                    print("   " + "="*50)
                else:
                    log_level = "error"  # Only show errors
                
                # Start the API server
                uvicorn.run(
                    app, 
                    host="0.0.0.0", 
                    port=api_port,
                    log_level=log_level,
                    access_log=self.debug
                )
                
            except Exception as e:
                print(f"Warning: Could not start API server: {e}")
        
        # Start API server in a separate thread
        api_thread = threading.Thread(target=run_api_server, daemon=True)
        _web_interface_registry['api_thread'] = api_thread
        api_thread.start()
        
        # Give the API server a moment to start
        import time
        time.sleep(2)
    
    def _start_reflex_interface(self):
        """
        Start the legacy Reflex web interface (fallback).
        This will start both frontend (port 3000) and backend (port 8000).
        """
        def run_reflex():
            try:
                # Change to the web_interface_old directory where rxconfig.py is located
                current_dir = os.path.dirname(os.path.abspath(__file__))
                web_interface_dir = os.path.join(current_dir, "web_interface_old")
                novatrace_root = os.path.dirname(current_dir)  # Parent directory of novatrace package
                
                # Check if web_interface_old directory exists
                if not os.path.exists(web_interface_dir):
                    print("❌ Legacy web interface directory not found.")
                    return
                
                # Set up environment with correct PYTHONPATH
                env = os.environ.copy()
                env['PYTHONPATH'] = f"{novatrace_root}:{env.get('PYTHONPATH', '')}"
                    
                # Run reflex run command with proper flags
                if self.debug:
                    # Show all logs when debug=True
                    print("🚀 NovaTrace legacy interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                    print("   ✅ All Reflex logs will be shown below:")
                    print("   " + "="*50)
                    
                    # Use no redirection to show all logs
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev", "--loglevel", "debug"],
                        cwd=web_interface_dir,
                        env=env
                    )
                else:
                    # Hide logs when debug=False (default)
                    DEVNULL = subprocess.DEVNULL
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev"],
                        cwd=web_interface_dir,
                        env=env,
                        stdout=DEVNULL,  # Hide stdout logs
                        stderr=DEVNULL,  # Hide stderr logs
                        text=True
                    )
                    print("🚀 NovaTrace legacy interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                
                # Wait a bit for the process to start
                import time
                time.sleep(2)
                
                if self.reflex_process.poll() is None:
                    print("   ✅ App running at: http://localhost:3000/")
                    if not self.debug:
                        print("   💡 Use debug=True to see detailed logs")
                else:
                    print("   ❌ Process failed to start")
                        
            except Exception as e:
                print(f"Warning: Could not start Reflex interface: {e}")
        
        # Start Reflex in a separate thread so it doesn't block the main application
        reflex_thread = threading.Thread(target=run_reflex, daemon=True)
        reflex_thread.start()
        
    def close(self):
        """
        Close the current session and connection to the database.
        Also stops the web interface if it's running.
        Returns:
            None
        """
        try:
            # Force cleanup when explicitly calling close()
            self.cleanup(force=True)
                    
        except Exception as e:
            print(f"Warning: NovaTrace close failed: {e}")

    def list_projects(self):
        """
        List all projects in the current session.
        """
        return self.session.query(Project).filter_by(session_id=self.active_session.id).all()
    
    def _find_available_port(self, preferred_ports=[4444, 4445, 4446, 4447]):
        """Find an available port from the preferred list"""
        import socket
        
        for port in preferred_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        
        # If none of the preferred ports work, find any available port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            return s.getsockname()[1]

    def _kill_process_on_port(self, port):
        """Kill any existing process using the specified port"""
        import subprocess
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                existing_pids = result.stdout.strip().split('\n')
                for pid in existing_pids:
                    if pid:
                        print(f"   🔄 Stopping existing process on port {port} (PID: {pid})")
                        subprocess.run(['kill', '-9', pid], capture_output=True)
                import time
                time.sleep(1)  # Wait for the port to be freed
                return True
        except:
            pass
        return False

    def tokenizer(self, response) -> Dict[str, Union[int, float]]:
        """
        Tokenizer to calculate the number of tokens used in a response and their cost.
        Args:
            response: The response object from the LLM or agent.
        Returns:
            Dict[str, Union[int, float]]: A dictionary containing the number of input tokens,
                                          output tokens, total tokens
        """
        if hasattr(response, "usage"):
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens

            tokens = {
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }
        else:
            tokens = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }
        return tokens
    
    def metadata(self, metadata: Dict[str, Union[str, float]]):
        """
        Set metadata for the current session.
        Args:
            metadata (Dict[str, Union[str, float]]): A dictionary containing metadata about the model
               - provider (str) | The provider of the model (e.g., "OpenAI", "Anthropic")
               - model (str) | The name of the model (e.g., "gpt-3.5-turbo", "claude-3-haiku-20240307")
               - input_cost_per_million_tokens (float) | Cost per million tokens for input
               - output_cost_per_million_tokens (float) | Cost per million tokens for output
        Raises:
            ValueError: If metadata is not provided or does not contain the required keys.
        Returns:
            None
        """
        try:
            if not isinstance(metadata, dict):
                print("Warning: NovaTrace metadata must be a dictionary")
                return
            
            self.provider = metadata.get('provider', None)
            self.model = metadata.get('model', None)
            self.input_cost_per_million_tokens = metadata.get('input_cost_per_million_tokens', 0.0)
            self.output_cost_per_million_tokens = metadata.get('output_cost_per_million_tokens', 0.0)

            if not all([self.provider, self.model, self.input_cost_per_million_tokens, self.output_cost_per_million_tokens]):
                print("Warning: NovaTrace metadata incomplete - some fields missing")
        except Exception as e:
            print(f"Warning: NovaTrace metadata configuration failed: {e}")

    def set_user(self, user_id: str = None, user_name: str = None):
        """
        Set default user information for traces.
        Args:
            user_id (str, optional): External user ID.
            user_name (str, optional): External user name.
        Returns:
            None
        """
        try:
            self.user_external_id = user_id or "guest_user"
            self.user_external_name = user_name or "Guest User"
        except Exception as e:
            print(f"Warning: NovaTrace set_user failed: {e}")

    def create_project(self, project_name: str):
        """
        Create a new project in the current session.
        Args:
            project_name (str): Name of the project to be created.
        Raises:
            ValueError: If a project with the same name already exists in the current session.
        Returns:
            None
        """
        try:
            if not self.session or not self.active_session:
                print("Warning: NovaTrace not properly initialized, cannot create project")
                return
                
            existing_project = self.session.query(Project).filter_by(name=project_name, session_id=self.active_session.id).first()
            if existing_project:
                print(f"Warning: Project '{project_name}' already exists in session '{self.active_session.name}'")
                return
            self.project = Project(name=project_name, session_id=self.active_session.id, created_at=datetime.now(self.time_zone))

            self.session.add(self.project)
            self.session.commit()
        except Exception as e:
            print(f"Warning: NovaTrace create_project failed: {e}")

    def connect_to_project(self, project_name: str):
        """
        Connect to an existing project in the current session.
        Args:
            project_name (str): Name of the project to connect to.
        Raises:
            ValueError: If the project with the specified name does not exist in the current session.
        Returns:
            Project: The project object if found.
        """
        try:
            if not self.session or not self.active_session:
                print("Warning: NovaTrace not properly initialized, cannot connect to project")
                return None
                
            self.project = self.session.query(Project).filter_by(name=project_name, session_id=self.active_session.id).first()
            if not self.project:
                print(f"Warning: Project '{project_name}' not found in session '{self.active_session.name}'")
                return None
            return self.project
        except Exception as e:
            print(f"Warning: NovaTrace connect_to_project failed: {e}")
            return None

    def _get_named_args(self, func, *args, **kwargs):
        """
        Get named arguments from a function call.
        """
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        named_args = {}
        for name, value in bound_args.arguments.items():
            named_args[name] = {
                "type": type(value).__name__,
                "value": value
            }
        return named_args

    def _extract_user_info(self, func, *args, **kwargs):
        """
        Extract user information from function arguments.
        Looks for user_id, user_name, user, or context parameters.
        """
        try:
            sig = py_inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            user_id = None
            user_name = None
            
            # Strategy 1: Direct user_id and user_name parameters
            if 'user_id' in bound_args.arguments:
                user_id = bound_args.arguments['user_id']
            if 'user_name' in bound_args.arguments:
                user_name = bound_args.arguments['user_name']
                
            # Strategy 2: From user object
            if 'user' in bound_args.arguments:
                user_obj = bound_args.arguments['user']
                if hasattr(user_obj, 'id'):
                    user_id = user_obj.id
                elif hasattr(user_obj, 'user_id'):
                    user_id = user_obj.user_id
                if hasattr(user_obj, 'name'):
                    user_name = user_obj.name
                elif hasattr(user_obj, 'username'):
                    user_name = user_obj.username
                    
            # Strategy 3: From context object
            if 'context' in bound_args.arguments:
                context_obj = bound_args.arguments['context']
                if hasattr(context_obj, 'user_id'):
                    user_id = context_obj.user_id
                if hasattr(context_obj, 'user_name'):
                    user_name = context_obj.user_name
                elif hasattr(context_obj, 'user') and hasattr(context_obj.user, 'name'):
                    user_name = context_obj.user.name
                    
            # Strategy 4: From request object (web frameworks)
            if 'request' in bound_args.arguments:
                request_obj = bound_args.arguments['request']
                if hasattr(request_obj, 'user'):
                    if hasattr(request_obj.user, 'id'):
                        user_id = request_obj.user.id
                    if hasattr(request_obj.user, 'name'):
                        user_name = request_obj.user.name
                        
            # Strategy 5: From kwargs
            if user_id is None and 'user_id' in kwargs:
                user_id = kwargs['user_id']
            if user_name is None and 'user_name' in kwargs:
                user_name = kwargs['user_name']
                
            # Use defaults if not found
            if user_id is None:
                user_id = self.user_external_id
            if user_name is None:
                user_name = self.user_external_name
                
            return str(user_id) if user_id else None, str(user_name) if user_name else None
            
        except Exception as e:
            print(f"Warning: Could not extract user info: {e}")
            return self.user_external_id, self.user_external_name

    def _get_trace_type_id(self, type_name):
        """Get trace type ID by name."""
        try:
            if not self.session:
                return {"LLM": 1, "Agent": 2, "Tool": 3}.get(type_name, 1)
            trace_type = self.session.query(TraceTypes).filter_by(name=type_name).first()
            return trace_type.id if trace_type else {"LLM": 1, "Agent": 2, "Tool": 3}.get(type_name, 1)
        except Exception as e:
            print(f"Warning: NovaTrace _get_trace_type_id failed: {e}")
            return {"LLM": 1, "Agent": 2, "Tool": 3}.get(type_name, 1)

    def _log_trace(self, type_id: int, input_data, output_data, request_time, response_time,
                    input_tokens=0, output_tokens=0, model_name=None, model_provider=None,
                    user_external_id=None, user_external_name=None):
        """
        Log a trace for the current request.
        Args:
            type_id (int): Type of trace (1 for LLM, 2 for Agent, 3 for Tool).
            input_data: Input data for the trace.
            output_data: Output data for the trace.
            request_time (datetime): Time when the request was made.
            response_time (datetime): Time when the response was received.
            input_tokens (int, optional): Number of input tokens used. Defaults to 0.
            output_tokens (int, optional): Number of output tokens used. Defaults to 0.
            user_external_id (str, optional): External user ID. Defaults to None.
            user_external_name (str, optional): External user name. Defaults to None.
        Returns:
            None
        Raises:
            None
        """
        try:
            if not self.session or not self.project or not self.active_session:
                print("Warning: NovaTrace not properly initialized, cannot log trace")
                return
                
            duration = (response_time - request_time).total_seconds() * 1000  # ms
            trace = Trace(
                type_id=type_id,
                input_data=json.dumps(input_data, default=str),
                output_data=json.dumps(output_data, default=str),
                project_id=self.project.id,
                session_id=self.active_session.id,  # Agregar referencia a la sesión
                created_at=response_time,
                request_time=request_time,
                response_time=response_time,
                duration_ms=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,

                model_provider=model_provider if model_provider else self.provider,
                model_name=model_name if model_name else self.model,
                model_input_cost=self.input_cost_per_million_tokens,
                model_output_cost=self.output_cost_per_million_tokens,
                call_cost = ((input_tokens * (self.input_cost_per_million_tokens/1000000)) + (output_tokens * (self.output_cost_per_million_tokens/1000000))),
                
                # Add user information
                user_external_id=user_external_id,
                user_external_name=user_external_name
            )
            self.session.add(trace)
            self.session.commit()
        except Exception as e:
            print(f"Warning: NovaTrace _log_trace failed: {e}")

    def llm(self, func):
        """
        Decorator to trace LLM calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                response_time = datetime.now(self.time_zone)
                try:
                    _args = self._get_named_args(func, *args, **kwargs)
                except Exception as e:
                    _args = {"args": args}
                self._log_trace(self._get_trace_type_id("LLM"), {"args": _args},
                                result, request_time, response_time,
                                model_name=kwargs.get("model_name", self.model),
                                model_provider=kwargs.get("model_provider", self.provider),
                                input_tokens=kwargs.get("input_tokens", 0),
                                output_tokens=kwargs.get("output_tokens", 0),
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                return result
            except Exception as e:
                print(f"Warning: NovaTrace LLM decorator failed: {e}")
                # Return the original function result even if tracing fails
                try:
                    return func(*args, **kwargs)
                except:
                    # If even the original function fails, let it propagate
                    raise
        return wrapper

    def agent(self, func):
        """
        Decorator to trace agent calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace. 
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                tokens = self.tokenizer(result)
                response_time = datetime.now(self.time_zone)
                try:
                    _args = self._get_named_args(func, *args, **kwargs)
                except Exception as e:
                    _args = {"args": args}
                self._log_trace(self._get_trace_type_id("Agent"), {"args": _args}, 
                                result, request_time, response_time,
                                tokens.get("input_tokens", 0),
                                tokens.get("output_tokens", 0),
                                model_name=kwargs.get("model_name", self.model),
                                model_provider=kwargs.get("model_provider", self.provider),
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                return result
            except Exception as e:
                print(f"Warning: NovaTrace Agent decorator failed: {e}")
                # Return the original function result even if tracing fails
                try:
                    return func(*args, **kwargs)
                except:
                    # If even the original function fails, let it propagate
                    raise
        return wrapper

    def tool(self, func):
        """ 
        Decorator to trace tool calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                try:
                    result_raw = result[-1]['result']
                    result_text = result_raw[0].text if isinstance(result_raw, list) and result_raw else ""

                except Exception as e:
                    result_text = result

                response_time = datetime.now(self.time_zone)
                try:
                    _args = self._get_named_args(func, *args, **kwargs)
                except Exception as e:
                    _args = {"args": args}
                self._log_trace(self._get_trace_type_id("Tool"), {"args": _args}, 
                                str(result_text), request_time, response_time,
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                return result
            except Exception as e:
                print(f"Warning: NovaTrace Tool decorator failed: {e}")
                # Return the original function result even if tracing fails
                try:
                    return func(*args, **kwargs)
                except:
                    # If even the original function fails, let it propagate
                    raise
        return wrapper
    
    def cleanup(self, force=False):
        """
        Clean up resources: stop API server and Docker container/Reflex process
        This method is idempotent and safe to call multiple times
        
        Args:
            force (bool): If True, forces cleanup even if interface is enabled
        """
        global _web_interface_registry
        
        # Only cleanup interface resources if we're the owner and force=True
        if not self._is_interface_owner and not force:
            # Just close database session for non-owners
            try:
                if hasattr(self, 'session') and self.session:
                    self.session.close()
            except Exception:
                pass
            return
        
        # Only cleanup interface if forced or explicitly requested
        if not force and getattr(self, 'interface_enabled', False):
            # Just close database session, but keep interface running
            try:
                if hasattr(self, 'session') and self.session:
                    self.session.close()
            except Exception:
                pass
            return
        
        try:
            if getattr(self, 'debug', False):
                print("\n🛑 NovaTrace cleanup starting...")
            
            # Close database session
            if hasattr(self, 'session') and self.session:
                self.session.close()
            
            # Stop API server
            api_port = _web_interface_registry.get('api_port')
            if api_port:
                if getattr(self, 'debug', False):
                    print(f"   🔌 Stopping API server on port {api_port}")
                self._kill_process_on_port(api_port)
                _web_interface_registry['api_port'] = None
            
            # Stop web interface (Docker container or Reflex process)
            reflex_process = _web_interface_registry.get('reflex_process')
            if reflex_process:
                try:
                    # Try to stop Docker container first (React interface)
                    container_name = _web_interface_registry['container_name']
                    try:
                        subprocess.run([
                            "docker", "stop", container_name
                        ], capture_output=True, text=True, timeout=10)
                        
                        subprocess.run([
                            "docker", "rm", container_name
                        ], capture_output=True, text=True)
                        
                        if getattr(self, 'debug', False):
                            print("   🐳 Docker container stopped")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                        # Fallback to process termination (Reflex interface)
                        if hasattr(reflex_process, 'poll') and reflex_process.poll() is None:
                            # First try graceful termination
                            reflex_process.terminate()
                            
                            # Wait a bit for graceful shutdown
                            import time
                            time.sleep(2)
                            
                            # If still running, force kill
                            if reflex_process.poll() is None:
                                reflex_process.kill()
                            
                            if getattr(self, 'debug', False):
                                print("   🔄 Reflex process terminated")
                    
                    _web_interface_registry['reflex_process'] = None
                except Exception as e:
                    if getattr(self, 'debug', False):
                        print(f"   ⚠️  Interface cleanup warning: {e}")
            
            # Reset the registry
            _web_interface_registry['interface_enabled'] = False
            _web_interface_registry['interface_started'] = False
            
            if getattr(self, 'debug', False):
                print("   ✅ NovaTrace cleanup completed")
            
        except Exception as e:
            if getattr(self, 'debug', False):
                print(f"   ⚠️  Cleanup warning: {str(e)}")

    def __del__(self):
        """Destructor - ensure cleanup when object is destroyed"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors in destructor

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatic cleanup"""
        self.cleanup(force=True)

    def enable_signal_cleanup(self):
        """
        Enable signal handlers for cleanup (Ctrl+C, SIGTERM).
        Call this if you want the interface to close when user presses Ctrl+C.
        """
        import signal
        
        def signal_handler(signum, frame):
            print("\n🛑 Signal received, cleaning up NovaTrace...")
            self.cleanup(force=True)
            exit(0)
        
        try:
            signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
            signal.signal(signal.SIGTERM, signal_handler)  # Termination
        except AttributeError:
            # Some signals might not be available on all platforms
            pass

    def shutdown_all_interfaces(self):
        """
        Manually shutdown all NovaTrace web interfaces.
        Use this when you want to stop everything.
        """
        self.cleanup(force=True)

    def start_web_interface(self, force_rebuild=False):
        """
        Start the web interface with optional force rebuild
        
        Args:
            force_rebuild (bool): If True, forces Docker image rebuild
        """
        self.force_rebuild = force_rebuild
        return self._start_web_interface()
    
    def rebuild_web_interface(self):
        """
        Force rebuild the Docker image and restart the web interface
        """
        print("🔨 Force rebuilding NovaTrace web interface...")
        return self.start_web_interface(force_rebuild=True)

    def list_projects(self):
        """
        List all projects in the current session.
        """
        try:
            if not self.session or not self.active_session:
                print("Warning: NovaTrace not properly initialized, cannot list projects")
                return []
            return self.session.query(Project).filter_by(session_id=self.active_session.id).all()
        except Exception as e:
            print(f"Warning: NovaTrace list_projects failed: {e}")
            return []