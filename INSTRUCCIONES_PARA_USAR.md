# Instrucciones para ejecutar este proyecto (paso a paso y sencillas)

Estas instrucciones están pensadas para una persona sin conocimientos técnicos. Siguelas tal cual.

1. Qué necesitas descargar e instalar

- Una computadora con Windows (o Mac/Linux, los pasos son parecidos).
- Conexión a Internet para descargar programas.
- Instalar Python (recomendado: Python 3.11). Descárgalo desde:
  https://www.python.org/downloads/
  - En Windows, durante la instalación marca la casilla "Add Python to PATH".

2. Cómo preparar la carpeta del proyecto

- Copia la carpeta completa del proyecto en el equipo (la que contiene los archivos `manage.py` y [requirements.txt](requirements.txt)).

3. Pasos fáciles (usa PowerShell o Símbolo del sistema)

- Abrir PowerShell en la carpeta del proyecto: en el Explorador de archivos, entra en la carpeta del proyecto, luego clic derecho -> "Abrir en Windows Terminal" o "Abrir en PowerShell".

- (Opcional pero recomendable) Crear y activar un entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

- Instalar las dependencias necesarias (archivo requirements.txt):

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

- Ejecutar las migraciones (configura la base de datos y crea tablas):

```powershell
python manage.py migrate
```

- (Opcional) Crear un usuario administrador para entrar al panel de administración:

```powershell
python manage.py createsuperuser
```

- Ejecutar el servidor de desarrollo y abrir la aplicación en el navegador:

```powershell
python manage.py runserver
# Luego abrir en el navegador: http://127.0.0.1:8000
```

4. Qué esperas ver

- Si todo está bien, al abrir http://127.0.0.1:8000 verás la aplicación funcionando.
- Para acceder al panel de administración usa http://127.0.0.1:8000/admin e ingresa el usuario creado con `createsuperuser`.

5. Problemas comunes y soluciones rápidas

- "python no se reconoce": reinstala Python y asegúrate de marcar "Add Python to PATH".
- Fallos al instalar paquetes: revisa tu conexión a Internet. Si aparece un error sobre compilación, intenta ejecutar `pip install --upgrade pip` y volver a instalar.
- Si el puerto 8000 ya está en uso, ejecuta `python manage.py runserver 8080` y abre http://127.0.0.1:8080.

6. Notas importantes

- No necesitas instalar bases de datos extra si el proyecto ya trae `db.sqlite3` (SQLite funciona sin instalaciones adicionales).
- Si en el futuro el proyecto usa PostgreSQL u otra base de datos, te avisarán con instrucciones adicionales.

Si quieres, puedo preparar un instalador automático o una guía con capturas de pantalla paso a paso. ¿Lo quieres?

7. Instalador automático (Windows)

- He incluido un instalador automático para Windows que realiza los pasos principales: crea un entorno virtual, instala dependencias, aplica migraciones y opcionalmente crea un usuario administrador e inicia el servidor.
- Para usarlo, abre la carpeta del proyecto en el Explorador de archivos y haz doble clic en `install_and_run.bat` o ejecútalo desde PowerShell:

```powershell
.\install_and_run.bat
```

- El script pedirá confirmaciones en pantalla (por ejemplo si quieres crear un usuario admin o iniciar el servidor ahora).
- Si PowerShell bloquea la ejecución de scripts, puedes ejecutar desde PowerShell (como administrador) lo siguiente para permitir temporalmente la ejecución del instalador:

```powershell
PowerShell -NoProfile -ExecutionPolicy Bypass -File .\install_windows.ps1
```

- Si necesitas una versión para Mac/Linux dímelo y la preparo.
