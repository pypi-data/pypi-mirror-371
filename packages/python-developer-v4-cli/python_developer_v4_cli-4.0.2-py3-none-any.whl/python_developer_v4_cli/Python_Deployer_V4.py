"""
Python Deployer - Herramienta de deployment automatizado para proyectos .NET
Versión mejorada con mejor arquitectura, logging y validaciones
"""

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from getpass import getpass
from pathlib import Path
from typing import Dict, List, Optional, Union
import time
import requests

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


@dataclass
class DeployConfig:
    """Configuración de deployment"""
    repo: str

    sln_file: str
    build_tool: Optional[str] = None
    branch: str = "main"
    clean_build: bool = True
    timeout: int = 300
    destino: Dict = field(default_factory=dict)
    remoto: Dict = field(default_factory=dict)
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.pdb", "*.xml", "*.log"])
    
    def __post_init__(self):
        if not self.repo or not self.sln_file:
            raise ValueError("repo y sln_file son campos obligatorios")


class Logger:
    """Sistema de logging mejorado con colores"""
    
    def __init__(self, name: str = "PyDeployer", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Clean handlers to avoid duplicates on re-initialization (e.g., in tests)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, msg: str, color: str = Fore.CYAN):
        self._print_colored(msg, color)
        self.logger.info(msg)
    
    def success(self, msg: str):
        self._print_colored(msg, Fore.GREEN)
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self._print_colored(msg, Fore.YELLOW)
        self.logger.warning(msg)
    
    def error(self, msg: str):
        self._print_colored(msg, Fore.RED)
        self.logger.error(msg)
    
    def debug(self, msg: str):
        self.logger.debug(msg)
        
    def _print_colored(self, msg: str, color: str):
        if COLOR_ENABLED:
            colored_msg = f"{color}{msg}{Style.RESET_ALL}"
        else:
            colored_msg = msg
        
        encoding = sys.stdout.encoding or 'utf-8'
        try:
            print(colored_msg)
        except UnicodeEncodeError:
            safe_msg = msg.encode(encoding, errors='replace').decode(encoding)
            if COLOR_ENABLED:
                print(f"{color}{safe_msg}{Style.RESET_ALL}")
            else:
                print(safe_msg) 


class GitManager:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def get_default_branch(self, repo_url):
        """Detecta el branch por defecto desde la API de GitHub."""
        try:
            if repo_url.startswith("https://github.com/"):
                parts = repo_url.rstrip(".git").split("/")
                owner, repo = parts[-2], parts[-1]
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                r = requests.get(api_url, timeout=10)
                if r.status_code == 200:
                    return r.json().get("default_branch", "main")
        except Exception as e:
            self.logger.warning(f"⚠️  No se pudo obtener el branch por defecto: {e}")
        return "main"

    def clone_repo(self, repo_url, branch, dest_dir):
        """
        Clona un repositorio Git en una carpeta destino.
        """
        # Si no se especifica rama o parece inválida, obtener por defecto
        if not branch:
            branch = self.get_default_branch(repo_url)
            self.logger.info(f"ℹ️  Usando branch por defecto: {branch}")

        self.logger.info(f"Clonando repositorio: {repo_url} (rama: {branch}) en {dest_dir}")

        try:
            cmd = ["git", "clone", "--branch", branch, repo_url, dest_dir]
            subprocess.run(cmd, check=True)
            self.logger.info("✅  Repositorio clonado con éxito")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌  Error al clonar: {e}")
            return False


class BuildManager:
    """Gestor de compilación .NET"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def detect_build_tool(self, sln_path: str) -> str:
        """Detecta la herramienta de build más adecuada"""
        self.logger.debug(f"Detectando herramienta de build para: {sln_path}")
        
        # Verificar disponibilidad de dotnet
        try:
            subprocess.run(["dotnet", "--version"], capture_output=True, check=True)
            dotnet_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            dotnet_available = False
        
        if not dotnet_available:
            self.logger.warning("dotnet CLI no disponible, intentando con MSBuild")
            return "msbuild"
        
        try:
            # Analizar contenido del .sln
            with open(sln_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar proyectos y analizar sus tipos
            sln_dir = Path(sln_path).parent
            modern_project = False
            
            for line in content.splitlines():
                if '.csproj"' in line:
                    # Extraer ruta del proyecto
                    parts = line.split('=')
                    if len(parts) > 1:
                        proj_path = parts[-1].strip().split(',')[0].replace('"', '').strip()
                        proj_full = sln_dir / proj_path
                        
                        if proj_full.exists():
                            with open(proj_full, 'r', encoding='utf-8') as pf:
                                proj_content = pf.read()
                                if '<TargetFramework>' in proj_content or 'Sdk="Microsoft.NET.Sdk' in proj_content:
                                    modern_project = True
                                    break
            
            return "dotnet" if modern_project else "msbuild"
            
        except Exception as e:
            self.logger.debug(f"Error detectando build tool: {e}")
            return "dotnet"  # Default seguro
    
    def build_solution(self, sln_path: str, build_tool: str, clean: bool = True) -> bool:
        """Compila la solución"""
        self.logger.info(f"Compiling with {build_tool}: {Path(sln_path).name}")
        
        try:
            # Clean if necessary
            if clean:
                self._clean_solution(sln_path, build_tool)
            
            # Build command
            if build_tool == "dotnet":
                cmd = ["dotnet", "build", sln_path, "-c", "Release", "--no-restore"]
                # Restore first
                restore_cmd = ["dotnet", "restore", sln_path]
                self.logger.info("Restoring NuGet packages...")
                restore_result = subprocess.run(restore_cmd, capture_output=True, text=True, timeout=300) # Increased timeout
                if restore_result.returncode != 0:
                    self.logger.warning(f"Warning in restore: {restore_result.stderr}")
            else:
                cmd = ["msbuild", sln_path, "/p:Configuration=Release", "/p:Platform=Any CPU"]
            
            self.logger.debug(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=300)
            
            if result.returncode != 0:
                self.logger.error(f"Error in compilation:\n{result.stderr}")
                self.logger.debug(f"Stdout: {result.stdout}")
                return False
            
            self.logger.success("Compilation successful")
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error("Compilation timeout")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in compilation: {e}")
            return False
    
    def _clean_solution(self, sln_path: str, build_tool: str):
        """Limpia la solución antes de compilar"""
        try:
            if build_tool == "dotnet":
                cmd = ["dotnet", "clean", sln_path]
            else:
                cmd = ["msbuild", sln_path, "/t:Clean"]
            
            subprocess.run(cmd, capture_output=True, timeout=60)
            self.logger.debug("Cleanup completed")
        except Exception as e:
            self.logger.debug(f"Error in cleanup: {e}")
    
    def find_output_directories(self, root_dir: str) -> List[str]:
        """Encuentra todos los directorios de salida (bin/Release)"""
        output_dirs = []
        root_path = Path(root_dir)
        
        for bin_dir in root_path.rglob("bin"):
            release_dir = bin_dir / "Release"
            if release_dir.exists() and release_dir.is_dir():
                # Verificar que contenga archivos ejecutables o DLLs
                has_binaries = any(
                    f.suffix.lower() in ['.exe', '.dll'] 
                    for f in release_dir.rglob("*") 
                    if f.is_file()
                )
                if has_binaries:
                    output_dirs.append(str(release_dir))
        
        return output_dirs


class DeployManager:
    """Gestor de deployment"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def deploy_local(self, src_dirs: List[str], dst: str, exclude_patterns: List[str] = None, stop_check_callback=None) -> bool:
        """Despliegue local con soporte para múltiples directorios fuente"""
        self.logger.info(f"Deploying locally to: {dst}")
        
        try:
            dst_path = Path(dst)
            dst_path.mkdir(parents=True, exist_ok=True)
            
            total_files = 0
            for src_dir in src_dirs:
                src_path = Path(src_dir)
                if not src_path.exists():
                    self.logger.warning(f"Source directory does not exist: {src_dir}")
                    continue
                
                # Integrate stop check here as well
                if stop_check_callback and stop_check_callback():
                    self.logger.info("Local deployment interrupted by stop signal.")
                    return False

                files_copied = self._copy_directory(src_path, dst_path, exclude_patterns, stop_check_callback)
                total_files += files_copied
                self.logger.info(f"Copied {files_copied} files from {src_path.name}")
            
            self.logger.success(f"Local deployment completed. Total: {total_files} files")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in local deployment: {e}")
            return False
    
    def deploy_remote_ssh(self, src_dirs: List[str], config: Dict, exclude_patterns: List[str] = None, stop_check_callback=None) -> bool:
        """Despliegue remoto usando SSH/SCP"""
        if PARAMIKO_AVAILABLE:
            return self._deploy_with_paramiko(src_dirs, config, exclude_patterns, stop_check_callback)
        else:
            self.logger.error("❌ Paramiko is not available. Cannot perform remote deployment without paramiko.")
            return False
    
    def _deploy_with_paramiko(self, src_dirs: List[str], config: Dict, exclude_patterns: List[str] = None, stop_check_callback=None) -> bool:
        """Deploy using paramiko (more robust and now cross-platform for destination)"""
        host = config.get("host")
        user = config.get("usuario")
        password = config.get("password")
        port = int(config.get("puerto", 22))
        remote_path = config.get("ruta_destino") # La ruta_destino del JSON

        self.logger.info(f"Connecting via SSH to {user}@{host}:{port}")
        
        try:
            # Conexión SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, port=port, username=user, password=password, timeout=30)
            
            # SFTP para transferir archivos
            sftp = ssh.open_sftp()

            # --- Inicio: Pre-procesamiento robusto de remote_path ---
            # 1. Normalizar separadores y limpiar espacios extra en los extremos
            processed_remote_path = remote_path.replace('\\', '/').strip()

            # 2. Determinar si es una ruta de unidad de Windows (ej. C:/)
            is_windows_drive_path = (len(processed_remote_path) > 1 and 
                                     processed_remote_path[1] == ':' and 
                                     processed_remote_path[0].isalpha() and 
                                     (processed_remote_path[2:] == '' or processed_remote_path[2] == '/'))

            # 3. Manejo inteligente de rutas Linux/Unix
            # Si no es una ruta de unidad de Windows
            if not is_windows_drive_path:
                # Caso especial: Si la ruta comienza con '/~/', la transformamos a '/home/{usuario}/'
                if processed_remote_path.startswith('/~/'):
                    self.logger.debug(f"Detectada ruta con '/~/' al inicio: {processed_remote_path}. Transformando.")
                    processed_remote_path = f'/home/{user}/{processed_remote_path[3:]}' # Quitar '/~/' y añadir /home/user/
                # Si la ruta comienza con '~/'. Lo transformamos explícitamente a /home/user/
                elif processed_remote_path.startswith('~/'):
                    self.logger.debug(f"Detectada ruta con '~/' al inicio: {processed_remote_path}. Expandiendo a ruta absoluta.")
                    processed_remote_path = f'/home/{user}/{processed_remote_path[2:]}'
                elif not processed_remote_path.startswith('/'): # Si no es absoluta y no tiene '~/' al inicio
                    # Dividir la ruta para analizar componentes, manteniendo espacios en nombres de directorio
                    path_parts = [p.strip() for p in processed_remote_path.split('/') if p.strip()]

                    if path_parts:
                        # Caso: "home/franco/Remote_Deploy" o "franco/Remote_Deploy"
                        if (path_parts[0].lower() == 'home' and len(path_parts) > 1 and path_parts[1] == user) or \
                           (path_parts[0] == user):
                            
                            if path_parts[0].lower() == 'home':
                                processed_remote_path = '/' + '/'.join(path_parts)
                            else: # path_parts[0] == user
                                remaining_path_components_joined = '/'.join(path_parts[1:])
                                processed_remote_path = f'/home/{user}/{remaining_path_components_joined}'
                        else:
                            # Cualquier otra ruta relativa (ej. "Remote_Deploy/Deploy_2")
                            # Prefijar con /home/user/ para hacerla absoluta
                            processed_remote_path = f'/home/{user}/{processed_remote_path}'
            
            # 4. Normalización final para limpiar `.` y `..`, y dobles barras
            # Aplicamos sftp.normalize a la ruta ya pre-procesada.
            try:
                processed_remote_path = sftp.normalize(processed_remote_path)
                self.logger.debug(f"Ruta remota final normalizada por SFTP a: {processed_remote_path}")
            except Exception as e:
                self.logger.warning(f"⚠️  Advertencia: Fallo en la normalización final de la ruta '{processed_remote_path}': {e}. Procediendo con la ruta tal cual.")
                # Si falla la normalización final, solo advertimos, ya que la ruta debería estar bien formateada.
            
            # Asegurarse de que las rutas de unidad de Windows mantengan la barra (C:/)
            if is_windows_drive_path and not processed_remote_path.endswith('/') and processed_remote_path.count(':') == 1:
                processed_remote_path += '/'

            # Limpiar posibles dobles barras (ej. //)
            processed_remote_path = processed_remote_path.replace('//', '/')
            # Eliminar la barra inicial si la ruta se vuelve vacía o solo `/`
            if processed_remote_path == '/' and remote_path != '/': # Solo quitar si la ruta original no era la raíz
                processed_remote_path = ''
            elif processed_remote_path.startswith('//'): # Asegurar que no haya dobles barras al inicio
                processed_remote_path = processed_remote_path[1:]


            self.logger.debug(f"Ruta remota final para SFTP: {processed_remote_path}")
            # --- Fin: Pre-procesamiento robusto de remote_path ---

            # Asegurar que el directorio base de destino remoto existe
            try:
                self._sftp_mkdir_p(sftp, processed_remote_path)
                self.logger.debug(f"Directorio remoto asegurado: {processed_remote_path}")
            except Exception as e:
                self.logger.error(f"❌ Fallo al asegurar el directorio base remoto {processed_remote_path}: {e}")
                sftp.close()
                ssh.close()
                return False
            
            total_files = 0
            for src_dir in src_dirs:
                src_path = Path(src_dir)
                if not src_path.exists():
                    self.logger.warning(f"El directorio fuente no existe: {src_dir}")
                    continue
                
                # Integrar la verificación de stop aquí también
                if stop_check_callback and stop_check_callback():
                    self.logger.info("Despliegue remoto interrumpido por señal de stop.")
                    sftp.close()
                    ssh.close()
                    return False

                files_transferred = self._transfer_directory_sftp(sftp, src_path, processed_remote_path, exclude_patterns, stop_check_callback)
                total_files += files_transferred
                self.logger.info(f"Transferidos {files_transferred} archivos desde {src_path.name}")
            
            sftp.close()
            ssh.close()
            
            self.logger.success(f"Despliegue remoto completado. Total: {total_files} archivos")
            return True
            
        except paramiko.AuthenticationException:
            self.logger.error("❌ Fallo de autenticación. Verifica el nombre de usuario y la contraseña/claves.")
            return False
        except paramiko.SSHException as e:
            self.logger.error(f"❌ Error SSH: {e}. Verifica el host, el puerto o la conectividad de red.")
            return False
        except Exception as e:
            self.logger.error(f"Error en el despliegue remoto: {e}")
            return False
    
    def _deploy_with_scp(self, src_dirs: List[str], config: Dict, exclude_patterns: List[str] = None, stop_check_callback=None) -> bool:
        """Deploy usando scp/pscp (fallback - no implementado completamente aquí)"""
        self.logger.warning("Usando SCP (funcionalidad limitada). Instala paramiko para mejor soporte.")
        # La implementación con scp/pscp es más compleja y depende del sistema.
        # Por simplicidad, if paramiko no está, se asume que no hay despliegue remoto robusto.
        return False

    def deploy_to_github(self, src_dirs: List[str], config: Dict, exclude_patterns: List[str] = None, project_name: str = None, stop_check_callback=None) -> bool:
        """Deploy a repositorio GitHub con directorio específico del proyecto"""
        repo_dest = config.get("repo_dest")
        branch_dest = config.get("branch_dest", "main")

        if not repo_dest:
            self.logger.error("❌ No se especificó repo_dest")
            return False

        # Detectar si es SSH o HTTPS
        if repo_dest.startswith("git@"):
            repo_auth = repo_dest
        else:
            token = config.get("token")
            # En un entorno de backend, no pedimos la contraseña interactivamente.
            # El token debe venir en la configuración if se usa HTTPS.
            if not token:
                self.logger.error("❌ Se requiere un token de GitHub para el despliegue HTTPS.")
                return False
            repo_auth = repo_dest.replace("https://", f"https://oauth2:{token}@") # Usar oauth2 para tokens

        try:
            temp_dir = tempfile.mkdtemp(prefix="deploy_github_")
            self.logger.debug(f"Directorio temporal para GitHub: {temp_dir}")
            
            if stop_check_callback and stop_check_callback(): return False
            subprocess.run(["git", "clone", repo_auth, temp_dir], check=True, timeout=120)

            if stop_check_callback and stop_check_callback(): return False
            # Checkout branch destino (if no existe, lo crea)
            subprocess.run(["git", "-C", temp_dir, "checkout", "-B", branch_dest], check=True, timeout=60)

            # Crear directorio del proyecto if se especifica
            if project_name:
                project_dir = Path(temp_dir) / project_name
                project_dir.mkdir(parents=True, exist_ok=True)
                target_dir = project_dir
                self.logger.info(f"📁 Creando directorio del proyecto: {project_name}")
            else:
                target_dir = Path(temp_dir)

            # Copiar binarios al directorio específico
            total_files = 0
            for src_dir in src_dirs:
                src_path = Path(src_dir)
                if not src_path.exists():
                    self.logger.warning(f"Directorio fuente no existe para GitHub deploy: {src_dir}")
                    continue

                if stop_check_callback and stop_check_callback(): return False
                files_copied = self._copy_directory(src_path, target_dir, exclude_patterns, stop_check_callback)
                total_files += files_copied

            if stop_check_callback and stop_check_callback(): return False
            # Commit & Push
            subprocess.run(["git", "-C", temp_dir, "add", "."], check=True, timeout=60)
            
            commit_msg = f"Deploy automático de {project_name or 'proyecto'} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            subprocess.run(["git", "-C", temp_dir, "commit", "-m", commit_msg], check=True, timeout=60)
            
            if stop_check_callback and stop_check_callback(): return False
            subprocess.run(["git", "-C", temp_dir, "push", "origin", branch_dest], check=True, timeout=300)

            if project_name:
                self.logger.success(f"✅ Deploy a GitHub completado en directorio '{project_name}'. Archivos: {total_files}")
            else:
                self.logger.success(f"✅ Deploy a GitHub completado. Archivos: {total_files}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Error en deploy GitHub: {e}. Output: {e.output.decode() if e.output else 'N/A'}")
            return False
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"❌ Timeout expirado en operación Git para deploy GitHub: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error inesperado en deploy GitHub: {e}")
            return False
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _copy_directory(self, src: Path, dst: Path, exclude_patterns: List[str] = None, stop_check_callback=None) -> int:
        """Copia directorio con exclusiones, con chequeo de stop."""
        exclude_patterns = exclude_patterns or []
        files_copied = 0
        
        for item in src.rglob("*"):
            if stop_check_callback and stop_check_callback():
                self.logger.info(f"Copia de archivos interrumpida por señal de stop.")
                return files_copied # Retorna los archivos copiados hasta el momento
            
            if item.is_file():
                # Verificar exclusiones
                if any(item.match(pattern) for pattern in exclude_patterns):
                    continue
                
                rel_path = item.relative_to(src)
                dst_file = dst / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(item, dst_file)
                    files_copied += 1
                except Exception as e:
                    self.logger.warning(f"Advertencia: No se pudo copiar {item} a {dst_file}: {e}")
        
        return files_copied
    
    def _sftp_mkdir_p(self, sftp, remote_directory_unix_style):
        """
        Crea directorios recursivamente en remoto (equivalente a mkdir -p)
        usando SFTP client con rutas estilo Unix.
        """
        # Asegurarse de que la ruta use barras diagonales, independientemente del OS local
        normalized_path = remote_directory_unix_style.replace('\\', '/')
        
        # Dividir la ruta en componentes y reconstruir, intentando crear cada uno
        # `path_parts` ahora incluirá partes con espacios if `strip()` se hizo antes
        path_parts = [p for p in normalized_path.strip('/').split('/') if p] 
        
        current_path_components = []
        for part in path_parts:
            current_path_components.append(part)
            
            # Construir el segmento de ruta actual (siempre estilo Unix para SFTP)
            # Asegura una barra inicial if la ruta es absoluta.
            current_segment_path = '/' + '/'.join(current_path_components) 
            
            # If es el primer componente y es una letra de unidad (ej. C:), adaptarlo para Windows
            if len(current_path_components) == 1 and current_path_components[0].endswith(':'):
                current_segment_path = current_path_components[0] + '/' # Para C: en Windows, Paramiko espera C:/

            try:
                sftp.stat(current_segment_path)
                self.logger.debug(f"El directorio remoto {current_segment_path} ya existe. Saltando creación.")
                continue # If ya existe, pasamos al siguiente componente.
            except IOError:
                # El directorio no existe, intentar crearlo
                try:
                    self.logger.debug(f"Intentando crear directorio remoto: {current_segment_path}")
                    sftp.mkdir(current_segment_path)
                    self.logger.debug(f"Creado con éxito: {current_segment_path}")
                except IOError as e:
                    if "Permission denied" in str(e):
                        self.logger.error(f"❌ Permiso denegado al crear el directorio remoto {current_segment_path}. Asegúrate de que el usuario SSH tenga permisos de escritura para la ruta de destino y sus padres.")
                        raise # Re-lanzar para detener el despliegue
                    else:
                        self.logger.error(f"❌ Error inesperado al crear el directorio remoto {current_segment_path}: {e}")
                        raise # Re-lanzar para otros errores de E/S no manejados

    def _transfer_directory_sftp(self, sftp, src: Path, remote_base: str, exclude_patterns: List[str] = None, stop_check_callback=None) -> int:
        """Transfiere directorio via SFTP con chequeo de stop"""
        exclude_patterns = exclude_patterns or []
        files_transferred = 0
        
        # Asegurarse de que remote_base siempre esté en estilo Unix para operaciones SFTP internas
        remote_base_unix = remote_base.replace('\\', '/')
        
        for item in src.rglob("*"):
            if stop_check_callback and stop_check_callback():
                self.logger.info(f"Transferencia SFTP interrumpida por señal de stop.")
                return files_transferred
            
            if item.is_file():
                if any(item.match(pattern) for pattern in exclude_patterns):
                    continue
                
                # Convertir la ruta local relativa a la fuente a estilo Unix para el remoto
                rel_path_unix = item.relative_to(src).as_posix() # .as_posix() asegura separadores Unix
                
                remote_file_path_unix = f"{remote_base_unix.rstrip('/')}/{rel_path_unix}"
                
                # Crear directorios padre remotamente if no existen
                remote_dir_unix = "/".join(remote_file_path_unix.split("/")[:-1])
                try:
                    self._sftp_mkdir_p(sftp, remote_dir_unix)
                except Exception as e:
                    self.logger.error(f"❌ Fallo al crear la estructura de directorio remoto para {remote_file_path_unix}: {e}. Saltando archivo.")
                    continue # Continuar con el siguiente archivo if la creación de directorio para este archivo falla

                try:
                    self.logger.debug(f"Transfiriendo {item} a {remote_file_path_unix}")
                    sftp.put(str(item), remote_file_path_unix)
                    files_transferred += 1
                except Exception as e:
                    self.logger.error(f"❌ Error transfiriendo {item} → {remote_file_path_unix}: {e}")
        
        return files_transferred


class PyDeployer:
    """Clase principal del deployer"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.logger = Logger("PyDeployer", log_file)
        self.git_manager = GitManager(self.logger)
        self.build_manager = BuildManager(self.logger)
        self.deploy_manager = DeployManager(self.logger)
    
    def deploy_from_config(self, config_path: str, stop_flag_path: Optional[str] = None) -> bool:
        """
        Ejecuta deployment desde archivo de configuración.
        stop_flag_path: Ruta a un archivo que if existe, indica que el despliegue debe detenerse.
        """
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Procesando: {config_path}")
        self.logger.info(f"{'='*60}")
        
        # Función auxiliar para chequear el flag de stop
        def should_stop():
            if stop_flag_path and Path(stop_flag_path).exists():
                self.logger.info("🚩 Se detectó la señal de stop. Terminando el despliegue.")
                try:
                    Path(stop_flag_path).unlink(missing_ok=True) # Limpiar el flag
                except Exception as e:
                    self.logger.warning(f"No se pudo eliminar el archivo de stop: {e}")
                return True
            return False

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = DeployConfig(**config_data)
            
            temp_dir = tempfile.mkdtemp(prefix="pydeploy_")
            self.logger.debug(f"Directorio temporal: {temp_dir}")
            
            try:
                # Pasar la función should_stop a los managers de bajo nivel
                return self._execute_deployment(config, temp_dir, should_stop)
            finally:
                self._cleanup_temp(temp_dir)
                
        except Exception as e:
            self.logger.error(f"Error procesando configuración: {e}")
            return False

    def _execute_deployment(self, config: DeployConfig, temp_dir: str, stop_check_callback=None) -> bool:
        """
        Ejecuta el proceso completo de deployment, chequeando por un stop_flag_path.
        """
        start_time = time.time()
        
        # Antes de cada paso grande, puedes chequear:
        if stop_check_callback and stop_check_callback(): return False
        if not self.git_manager.clone_repo(config.repo, config.branch, temp_dir):
            return False

        if stop_check_callback and stop_check_callback(): return False
        sln_path = os.path.join(temp_dir, config.sln_file)
        if not os.path.isfile(sln_path):
            self.logger.error(f"Archivo .sln no encontrado: {config.sln_file}")
            return False
        
        build_tool = config.build_tool or self.build_manager.detect_build_tool(sln_path)
        self.logger.info(f"Herramienta de build: {build_tool}")
        
        if stop_check_callback and stop_check_callback(): return False
        if not self.build_manager.build_solution(sln_path, build_tool, config.clean_build):
            return False
        
        if stop_check_callback and stop_check_callback(): return False
        output_dirs = self.build_manager.find_output_directories(temp_dir)
        if not output_dirs:
            self.logger.error("No se encontraron directorios de salida con binarios")
            return False
        
        self.logger.info(f"Encontrados {len(output_dirs)} directorios de salida")
        
        destino_tipo = config.destino.get("tipo", "local").lower()
        success = False
        
        if stop_check_callback and stop_check_callback(): return False
        if destino_tipo == "local":
            dst = config.destino.get("ruta")
            if not dst:
                self.logger.error("No se especificó ruta de destino local")
                return False
            success = self.deploy_manager.deploy_local(output_dirs, dst, config.exclude_patterns, stop_check_callback)
        elif destino_tipo == "remoto":
            success = self.deploy_manager.deploy_remote_ssh(output_dirs, config.remoto, config.exclude_patterns, stop_check_callback)
        elif destino_tipo == "github":
            project_name = config.destino.get("project_name")
            if not project_name:
                repo_url = config.repo
                if repo_url.endswith('.git'):
                    repo_url = repo_url[:-4]
                project_name = repo_url.split('/')[-1]
                if config.destino.get("add_timestamp", False):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    project_name = f"{project_name}_{timestamp}"
            
            success = self.deploy_manager.deploy_to_github(output_dirs, config.remoto, config.exclude_patterns, project_name, stop_check_callback)
        else:
            self.logger.error(f"Tipo de destino desconocido: {destino_tipo}")
            return False
        
        elapsed_time = time.time() - start_time
        if success:
            self.logger.success(f"Deployment completado en {elapsed_time:.1f}s")
        else:
            self.logger.error(f"Deployment falló después de {elapsed_time:.1f}s")
        
        return success

    def _cleanup_temp(self, temp_dir: str):
        """Limpia directorio temporal con manejo robusto de archivos bloqueados"""
        if not os.path.exists(temp_dir):
            return
        try:
            git_dir = os.path.join(temp_dir, '.git')
            if os.path.exists(git_dir):
                self._cleanup_git_files(git_dir)
            time.sleep(0.5)
            shutil.rmtree(temp_dir)
            self.logger.debug("Directorio temporal eliminado")
        except PermissionError:
            self.logger.debug("Permisos denegados, intentando método alternativo...")
            try:
                self._force_remove_directory(temp_dir)
                self.logger.debug("Directorio temporal eliminado (método alternativo)")
            except FileNotFoundError:
                self.logger.debug("Directorio temporal ya eliminado")
            except Exception as e2:
                self.logger.warning(f"Error eliminando directorio temporal (método alternativo): {e2}")
        except Exception as e:
            self.logger.warning(f"Error eliminando directorio temporal: {e}")

    def _cleanup_git_files(self, git_dir: str):
        """Limpia archivos de Git que pueden estar bloqueados"""
        try:
            pack_dir = os.path.join(git_dir, 'objects', 'pack')
            if os.path.exists(pack_dir):
                for file in os.listdir(pack_dir):
                    if file.endswith('.idx') or file.endswith('.pack'):
                        try:
                            os.remove(os.path.join(pack_dir, file))
                        except:
                            pass
            index_file = os.path.join(git_dir, 'index')
            if os.path.exists(index_file):
                try:
                    os.remove(index_file)
                except:
                    pass
        except Exception as e:
            self.logger.debug(f"Error limpiando archivos Git: {e}")

    def _force_remove_directory(self, path: str):
        """Fuerza la eliminación de un directorio usando comandos del sistema"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['rmdir', '/s', '/q', path], capture_output=True, timeout=10)
            else:
                subprocess.run(['rm', '-rf', path], capture_output=True, timeout=10)
        except Exception as e:
            self.logger.debug(f"Error en eliminación forzada: {e}")
            raise


def create_sample_config(filename: str = "sample_config.json"):
    """Crea un archivo de configuración de ejemplo"""
    sample = {
        "repo": "https://github.com/cake-build/example.git",
        "sln_file": "src/Example.sln",
        "branch": "master",
        "build_tool": "dotnet",
        "clean_build": True,
        "timeout": 300,
        "destino": {
            "tipo": "github",
            "project_name": "MiProyecto-ERP",
            "add_timestamp": False
        },
        "remoto": {
            "repo_dest": "git@github.com:usuario/Deploys.git",
            "branch_dest": "main",
            # IMPORTANTE: Para despliegues remotos SSH/SFTP, la ruta_destino puede ser:
            # - Para Linux: rutas absolutas como "/home/usuario/mi_app_desplegada"
            #   o rutas de usuario como "~/mi_app_desplegada" (Paramiko las normalizará)
            #   o rutas relativas al home como "mi_app_desplegada" (se interpretarán relativas al home del usuario)
            # - Para Windows: rutas de unidad como "C:/inetpub/wwwroot/mi_app" (usar barras diagonales).
            #   También "Z:\Python_Deployer_versions\Python_Developer_V0.0.4" se normalizará a "Z:/..."
            "ruta_destino": "~/Remote_Deploy/Deploy_2", 
            "usuario": "franco",
            "host": "192.168.0.97",
            "puerto": 22,
            "password": "tu_contraseña_ssh" # Reemplazar con tu contraseña o usar clave SSH
        },
        "exclude_patterns": ["*.pdb", "*.xml", "appsettings.Development.json", "bin/*", "obj/*"]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)
    
    print(f"Archivo de configuración de ejemplo creado: {filename}")


def parse_key_value_args(arg_list):
    """Parsea argumentos tipo clave=valor en cualquier orden"""
    args_dict = {}
    for arg in arg_list:
        if "=" in arg:
            k, v = arg.split("=", 1)
            args_dict[k.strip().lower()] = v.strip()
    return args_dict


def build_config_from_args(kv_args):
    """Construye un dict de configuración desde argumentos clave=valor"""
    branch = kv_args.get("branch", None)
    tipo = kv_args.get("tipo", "local").lower()

    missing = []
    if "repo" not in kv_args:
        missing.append("repo")
    if "sln" not in kv_args:
        missing.append("sln")

    if tipo == "local":
        if "ruta" not in kv_args:
            missing.append("ruta")

    elif tipo == "remoto":
        for req in ["ruta_destino", "puerto", "host", "usuario"]:
            if req not in kv_args:
                missing.append(req)

    elif tipo == "github":
        for req in ["repo_dest", "branch_dest"]:
            if req not in kv_args:
                missing.append(req)

    if missing:
        print("\nFALTAN ARGUMENTOS OBLIGATORIOS:", ", ".join(missing))
        print("\nEjemplo local:")
        print("  python Python_Deployer.py repo=https://github.com/cake-build/example.git "
              "sln=src/Example.sln branch=master tipo=local ruta=./deploy/cake-example")
        print("\nEjemplo remoto:")
        print("  python Python_Deployer.py repo=https://github.com/cake-build/example.git "
              "sln=src/Example.sln branch=master tipo=remoto ruta_destino=/home/usuario/remote_deploy "
              "puerto=22 host=192.168.0.92 usuario=usuario_ssh")
        print("\nEjemplo github:")
        print("  python Python_Deployer.2py repo=https://github.com/cake-build/example.git "
              "sln=src/Example.sln branch=master tipo=github "
              "repo_dest=https://github.com/org/Deploys.git branch_dest=main token=ghp_xxxxxx")
        sys.exit(1)

    config = {
        "repo": kv_args["repo"],
        "sln_file": kv_args["sln"],
        "branch": branch or "main",
        "clean_build": True,
        "timeout": 300,
        "destino": {"tipo": tipo},
        "exclude_patterns": ["*.pdb", "*.xml", "*.log", "bin/*", "obj/*"]
    }

    if tipo == "local":
        config["destino"]["ruta"] = kv_args["ruta"]

    elif tipo == "remoto":
        config["remoto"] = {
            "usuario": kv_args["usuario"],
            "host": kv_args["host"],
            "puerto": int(kv_args["puerto"]),
            "ruta_destino": kv_args["ruta_destino"]
        }
        if "password" in kv_args:
            config["remoto"]["password"] = kv_args["password"]

    elif tipo == "github":
        config["remoto"] = {
            "repo_dest": kv_args["repo_dest"],
            "branch_dest": kv_args["branch_dest"]
        }
        if "token" in kv_args:
            config["remoto"]["token"] = kv_args["token"]

    return config


def main():
    parser = argparse.ArgumentParser(
        description="Python Deployer - Herramienta de deployment automatizado para .NET",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Ejemplos de uso:

  # Usando archivo(s) JSON
  python-deployer config.json
  python-deployer config1.json config2.json --log deployment.log

  # Crear archivo de configuración de ejemplo
    python-deployer --create-sample

  # Usando argumentos directos (deploy local)
  python-deployer repo=https://github.com/cake-build/example.git \\
                            sln=src/Example.sln \\
                            tipo=local \\
                            ruta=./deploy/cake-example

  # Usando argumentos directos (deploy remoto)
  python-deployer repo=https://github.com/cake-build/example.git \\
                            sln=src/Example.sln \\
                            tipo=remoto \\
                            ruta_destino=/var/www/remote_deploy \\ # Ejemplo de ruta Linux
                            puerto=22 \\
                            host=192.168.0.92 \\
                            usuario=ubuntu

  # Usando argumentos directos (deploy github)
  python-deployer repo=https://github.com/cake-build/example.git \\
                            sln=src/Example.sln \\
                            tipo=github \\
                            repo_dest=https://github.com/org/Deploys.git branch_dest=main token=ghp_xxxxxx

Notas:
  - Los argumentos pueden ir en cualquier orden.
  - 'branch' y 'tipo' son opcionales:
        * Si no se especifica branch → intenta con 'master' y luego 'main'.
        * Si no se especifica tipo   → se asume 'local'.
  - Para despliegue remoto, 'ruta_destino' debe ser una ruta absoluta en el servidor remoto.
"""
    )

    parser.add_argument("inputs", nargs="+",
                        help="Archivos de configuración JSON o argumentos clave=valor")
    parser.add_argument("--log", help="Archivo de log (opcional)")
    parser.add_argument("--create-sample", action="store_true", help="Crear archivo de configuración de ejemplo")
    parser.add_argument("--stop-flag", help="Ruta a un archivo que actúa como flag para detener el despliegue.")
    args = parser.parse_args()

    if args.create_sample:
        create_sample_config()
        return 0

    deployer = PyDeployer(args.log)
    success_count = 0
    total_count = 0

    if all("=" not in inp for inp in args.inputs):
        total_count = len(args.inputs)
        for config_path in args.inputs:
            if not os.path.isfile(config_path):
                deployer.logger.error(f"Archivo no encontrado: {config_path}")
                continue
            if deployer.deploy_from_config(config_path, args.stop_flag): 
                success_count += 1
    else:
        kv_args = parse_key_value_args(args.inputs)
        config = build_config_from_args(kv_args)

        if not deployer.git_manager.clone_repo(config["repo"], config["branch"], tempfile.mkdtemp()):
             deployer.logger.warning(f"No se pudo clonar la rama '{config['branch']}', intentando con la rama por defecto.")
             pass


        temp_config_file = tempfile.mktemp(suffix=".json")
        with open(temp_config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        total_count = 1
        if deployer.deploy_from_config(temp_config_file, args.stop_flag):
            success_count += 1

    deployer.logger.info(f"\n{'=' * 60}")
    deployer.logger.info(f"RESUMEN: {success_count}/{total_count} deployments exitosos")
    deployer.logger.info(f"{'=' * 60}")

    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
