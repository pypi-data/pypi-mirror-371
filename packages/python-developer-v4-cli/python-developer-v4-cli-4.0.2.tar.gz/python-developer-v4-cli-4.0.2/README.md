Instalador desde PyPI de el archivo Python_Deployer_V4.py 
Modo de uso:
comando para instalar : pip install python-developer-v4-cli==4.0.2
comando para ejecutar archivo: python-deployer
comando de ayuda : python-deployer --help 


demas comandos:
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

