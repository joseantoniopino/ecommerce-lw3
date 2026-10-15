# Configuración manual de PhpStorm

Proyecto real: **`/home/jose/proyectos/livewire/v3/ecommerce`**. Esta guía prepara únicamente este proyecto. Codex no ha abierto ni modificado preferencias, intérpretes ni archivos `.idea`. Los nombres de algunas opciones pueden variar ligeramente con la versión o idioma del IDE.

## 1. Abrir el proyecto y conectar Docker

Abrir en PhpStorm `/home/jose/proyectos/livewire/v3/ecommerce`. Desde una terminal en esa raíz:

```sh
docker compose up -d
docker compose ps
```

Los servicios `php`, `mysql` y `nginx` deben estar healthy. Node no tiene que permanecer arrancado.

En **Settings → Build, Execution, Deployment → Docker**, añadir una conexión si no existe ya una apropiada:

- Nombre sugerido: `Docker local Ubuntu`.
- Tipo: **Unix socket**.
- Socket: `unix:///var/run/docker.sock`.
- Ejecutar la comprobación de conexión del IDE; debe mostrar conexión correcta y la versión del Engine.

El contexto Docker `default` de este host utiliza ese socket. El usuario `jose` pertenece al grupo `docker` y el socket es `root:docker`, modo 660. No activar TCP inseguro ni usar una conexión de Docker Desktop. Reutilizar una conexión local ya válida no exige modificar configuraciones de otros proyectos.

## 2. Intérprete PHP de Docker Compose

Ir a **Settings → PHP → CLI Interpreter → … → + → From Docker, Vagrant, VM, WSL, Remote…** y elegir **Docker Compose**.

| Campo | Valor |
|---|---|
| Nombre sugerido | PHP 8.3 Compose — livewire-v3-ecommerce |
| Server | Conexión Docker local anterior |
| Configuration file | `/home/jose/proyectos/livewire/v3/ecommerce/compose.yaml` |
| Service | `php` |
| PHP executable | `/usr/local/bin/php` |
| Working directory, si se solicita | `/var/www/html` |

En **Lifecycle**, preferir **Connect to existing container** / `docker compose exec` para utilizar el servicio que ya está arrancado. Así el IDE usa la configuración comprobada y el mismo bind mount. Si el IDE ofrece solo crear un contenedor de servicio, debe usar igualmente el servicio `php`, su usuario de imagen y sus volúmenes; no elegir la imagen PHP base sin construir.

Actualizar la información del intérprete. Resultados esperados:

- PHP **8.3.35**; lenguaje del proyecto **8.3**.
- Debugger **Xdebug 3.5.3**.
- Extensiones: `pdo_mysql`, `mbstring`, `intl`, `zip`, `bcmath`, `gd`, `pcntl`, `exif`, `fileinfo`, Opcache, XML, cURL, entre otras.
- PHP busca INI en `/usr/local/etc/php/conf.d`; que `Loaded Configuration File` esté vacío es normal: esta imagen configura PHP mediante archivos en `conf.d`.
- `99-development.ini`, `99-xdebug-settings.ini` y una única directiva de carga en `docker-php-ext-xdebug.ini`.

Seleccionar este intérprete como intérprete del proyecto en **Settings → PHP**. No elegir el PHP local de Ubuntu. La acción de recarga debe reconocer versión y debugger; la lista completa se puede contrastar con:

```sh
docker compose exec php php -v
docker compose exec php php -m
docker compose exec php php --ini
docker compose exec php composer check-platform-reqs
```

## 3. Servidor y mapeo de rutas

En **Settings → PHP → Servers → +**:

| Campo | Valor exacto |
|---|---|
| Name | **`livewire-v3-ecommerce`** |
| Host | `127.0.0.1` |
| Port | `18080` |
| Debugger | Xdebug |
| Use path mappings | Activado |

En el árbol de archivos local, seleccionar la carpeta raíz **`/home/jose/proyectos/livewire/v3/ecommerce`** y escribir en **Absolute path on the server**:

```text
/var/www/html
```

La correspondencia completa es:

```text
/home/jose/proyectos/livewire/v3/ecommerce  →  /var/www/html
```

La ruta remota debe ser exactamente `/var/www/html`, sin espacios al principio ni al final. Un espacio final se guarda literalmente y hace que PhpStorm no encuentre los archivos remotos.

El puerto **18080** de este servidor corresponde a la URL HTTP; el puerto **9003** de PHP → Debug corresponde a la conexión Xdebug. Mantener ambos en sus campos respectivos.

No mapear únicamente `public/`, no introducir otro nivel de directorios y no usar rutas del proyecto de otro curso. Todos los archivos heredan ese mapeo:

```text
/home/jose/proyectos/livewire/v3/ecommerce/routes/web.php
→ /var/www/html/routes/web.php

/home/jose/proyectos/livewire/v3/ecommerce/artisan
→ /var/www/html/artisan

/home/jose/proyectos/livewire/v3/ecommerce/tests/Feature/ExampleTest.php
→ /var/www/html/tests/Feature/ExampleTest.php
```

Compose monta literalmente `.:/var/www/html`. `PHP_IDE_CONFIG=serverName=livewire-v3-ecommerce` está en el entorno del contenedor y FPM conserva el entorno (`clear_env=no`). Se verificó en procesos CLI y en una petición FPM real. El nombre del servidor debe coincidir exactamente, respetando letras y guiones.

## 4. Debugger y escucha

En **Settings → PHP → Debug → Xdebug**:

- **Debug port**: `9003`.
- Activar **Can accept external connections** si aparece: la conexión viene de Docker.
- Mantener habilitados los breakpoints. No activar opciones de omitir/silenciar breakpoints.
- **Break at first line in PHP scripts** es opcional para un primer diagnóstico; desactivarlo para el trabajo habitual con breakpoints propios.
- La opción **Force break at first line when no path mapping is specified** puede ayudar a detectar un mapeo ausente; no sustituye el mapeo anterior.
- No hace falta configurar DBGp Proxy, Xdebug Cloud, túneles SSH, descubrir el host por cabeceras ni opciones de Xdebug 2.

Activar **Run → Start Listening for PHP Debug Connections** (también disponible en el icono de teléfono del debugger). La acción debe pasar a **Stop Listening for PHP Debug Connections** y el icono reflejar el estado activo. Es una comprobación más fiable que un color concreto del tema.

En Ubuntu se puede comprobar el socket:

```sh
ss -ltnp '( sport = :9003 )'
```

Debe existir un listener del IDE accesible por la interfaz gateway de Docker, no exclusivamente por `127.0.0.1`. Se comprobó que `host.docker.internal` resuelve a **172.17.0.1** en esta máquina. Si el IDE solo escucha en loopback, revisar su opción de aceptar conexiones externas. Si hay un firewall activo que rechaza esta conexión, diagnosticar sus reglas con el administrador y autorizar solo el origen/interfaz Docker apropiado; no se han cambiado reglas del host.

El contenedor realiza conexiones **salientes** al IDE. No publicar `9003` en Compose. `xdebug.start_with_request=yes` inicia la depuración automáticamente en todas las peticiones y comandos PHP. Basta con activar la escucha del IDE y colocar un breakpoint; no se necesitan parámetros, cookies ni extensiones. `xdebug.mode=debug,develop` está disponible; para un CLI sin Xdebug se puede utilizar `docker compose exec -e XDEBUG_MODE=off php php artisan route:list`.

## 5. Primera prueba HTTP con el código original

1. Abrir el proyecto, configurar el intérprete y el servidor con el mapeo anterior.
2. Activar la escucha de conexiones.
3. Abrir `routes/web.php` y poner un breakpoint en una línea ejecutable de la ruta `/`, por ejemplo `return view('welcome');`. El número cambia si añades líneas de prueba.
4. Visitar **http://127.0.0.1:18080/**.
5. La petición debe quedarse esperando mientras PhpStorm muestra la sesión detenida en esa línea.
6. En Variables/Watches inspeccionar las variables de la ruta o evaluar `request()->fullUrl()` o `app()->version()`.
7. Continuar con **Resume Program (F9)**: el navegador debe recibir la bienvenida de Laravel.
8. Cada nueva petición a http://127.0.0.1:18080 se detendrá si alcanza el breakpoint y el IDE está escuchando. Al terminar, desactivar la escucha; Xdebug seguirá intentando conectarse brevemente en cada petición.

Si aparece una petición de mapeo/servidor desconocido, seleccionar `livewire-v3-ecommerce` y el mapeo de raíz; no aceptar una ruta de otro proyecto.

La activación es automática tanto por HTTP como por CLI. No hace falta una extensión de navegador ni un trigger. Los healthchecks internos están preparados para no iniciar sesiones de depuración.

## 6. Artisan y scripts PHP

Con PhpStorm escuchando, colocar un breakpoint en `artisan`, **línea 18**, en la carga de `vendor/autoload.php`. Desde la raíz:

```sh
docker compose exec php php artisan route:list
```

Debe detenerse en `artisan`, con `__DIR__` igual a `/var/www/html`. Continuar para obtener las rutas. La ruta `/` original no se ejecuta durante `route:list`, de modo que el breakpoint de su `return view(...)` no se alcanza con ese comando.

Para depurar un script desde el propio IDE, crear manualmente **Run → Edit Configurations → + → PHP Script**:

- Intérprete: el PHP 8.3 Compose de este proyecto.
- Archivo local: `/home/jose/proyectos/livewire/v3/ecommerce/artisan`.
- Argumentos: `route:list`.
- Directorio local de trabajo: `/home/jose/proyectos/livewire/v3/ecommerce` (remoto `/var/www/html`).
- Variables: `PHP_IDE_CONFIG=serverName=livewire-v3-ecommerce`.

Elegir **Debug**, no Run. El mismo procedimiento se aplica a scripts propios que se añadan durante el curso: el IDE debe mapear el fichero bajo la raíz a su ubicación en `/var/www/html`. No hace falta crear un script auxiliar para esta primera prueba.

## 7. PHPUnit

Ir a **Settings → PHP → Test Frameworks → + → PHPUnit by Remote Interpreter** y seleccionar el intérprete Docker Compose anterior.

- Método: **Use Composer autoloader**.
- Autoloader remoto: `/var/www/html/vendor/autoload.php`.
- PHPUnit remoto: `/var/www/html/vendor/bin/phpunit` si el diálogo solicita el ejecutable.
- Configuración estándar: `/var/www/html/phpunit.xml` dentro del contenedor; fichero local correspondiente `/home/jose/proyectos/livewire/v3/ecommerce/phpunit.xml`. Si el selector del IDE muestra archivos locales, seleccionar este último.
- Recargar la versión: debe detectar **PHPUnit 10.5.66**.

Crear una configuración **PHPUnit**, usar **Defined in the configuration file**, elegir el framework remoto y el `phpunit.xml` del proyecto. En su entorno añadir `PHP_IDE_CONFIG=serverName=livewire-v3-ecommerce` si el IDE no los aplica desde el intérprete. Usar **Debug**.

Primera prueba: breakpoint en `tests/Feature/ExampleTest.php`, **línea 15**, en `$response = $this->get('/');`. Al continuar hasta la línea 17 se puede inspeccionar `$response`. También es posible alcanzar `routes/web.php:17` durante este test de funcionalidad.

Alternativa desde terminal, con el IDE escuchando:

```sh
docker compose exec php php vendor/bin/phpunit
docker compose exec php php vendor/bin/phpunit \
  --filter test_the_application_returns_a_successful_response
```

Los dos tests originales pasan sin modificar su configuración. No se han creado tests de aplicación adicionales. La cobertura no está habilitada por defecto; depurar tests no requiere cobertura.

## 8. Composer con PHP de Docker

En **Settings → PHP → Composer**:

- Composer JSON: `/home/jose/proyectos/livewire/v3/ecommerce/composer.json`.
- Ejecución: **Remote interpreter**, seleccionando el intérprete PHP 8.3 Compose.
- Ejecutable Composer en el contenedor: `/usr/local/bin/composer`.
- Si la versión del IDE solicita un script Composer, esa ruta es el ejecutable PHP/PHAR copiado a la imagen; no seleccionar un Composer local ni descargar uno a Ubuntu.

Ejecutar la detección de versión. Debe mostrar Composer **2.10.3** con PHP **8.3.35**. En la consola comprobar que la invocación utiliza el servicio `php`. El comando de referencia es:

```sh
docker compose exec php composer --version
docker compose exec php composer install
docker compose exec php composer check-platform-reqs
```

Composer no debe ejecutarse como root. `docker compose exec php id` debe mostrar `uid=1000(app) gid=1000(app)`. Los avisos de Laravel fuera de soporte siguen visibles en `composer audit`; no representan un fallo del intérprete.

## 9. Base de datos en el IDE

En **Database → + → Data Source → MySQL**:

| Campo             | Valor                                                   |
|-------------------|---------------------------------------------------------|
| Nombre sugerido   | ecommerce Docker local                                  |
| Host              | 127.0.0.1                                               |
| Port              | 13306                                                   |
| Database / schema | ecommerce                                               |
| User              | ecommerce                                               |
| Password          | Copiar `MYSQL_PASSWORD` del archivo local `docker/.env` |

Descargar el driver JDBC desde el propio diálogo si el IDE lo solicita y pulsar **Test Connection**. Debe identificar MySQL **8.4.11**. Seleccionar el esquema y sincronizar; deben aparecer `migrations`, `users`, `password_reset_tokens`, `failed_jobs` y `personal_access_tokens`. `users` está vacío.

Laravel usa `mysql:3306` porque se ejecuta en la red de Compose. PhpStorm corre en Ubuntu y usa `127.0.0.1:13306`, el puerto publicado. `mysql` no es un nombre DNS del host; `localhost` dentro del contenedor PHP tampoco señala al servicio MySQL.

MySQL 8.4 usa autenticación moderna; no configurar el plugin obsoleto `mysql_native_password`. Si el driver muestra exactamente `Public Key Retrieval is not allowed`, preferir TLS con el driver actualizado. Solo si se elige deliberadamente una conexión local sin TLS se puede habilitar `allowPublicKeyRetrieval=true` en las propiedades de ese datasource. No cambiar la autenticación del servidor ni otros datasources.

## 10. Diagnósticos dirigidos

Ejecutar desde `/home/jose/proyectos/livewire/v3/ecommerce`.

| Problema | Evidencia que revisar | Resultado esperado / corrección |
|---|---|---|
| Xdebug no conecta | `ss -ltnp '( sport = :9003 )'` y escucha en IDE | Listener accesible desde Docker; comprobar que no hay otro proceso usando 9003. |
| Host no resuelve | `docker compose exec php getent hosts host.docker.internal` | `172.17.0.1` en este host; revisar `extra_hosts` si se perdió. |
| CLI no carga Xdebug | `docker compose exec php php -v` y `php --ini` | Xdebug 3.5.3; una sola directiva `zend_extension` para Xdebug. Usar el intérprete construido. |
| FPM no carga Xdebug | `docker compose exec php php-fpm -i` y logs PHP | Xdebug 3.5.3 y `start_with_request=yes`. Reconstruir y recrear PHP si cambió un INI. La prueba DBGp valida el worker real. |
| Nombre de servidor incorrecto | `docker compose exec php printenv PHP_IDE_CONFIG` | `serverName=livewire-v3-ecommerce`; exactamente el mismo nombre en Servers. |
| Rutas sin mapear / IDE abre otro archivo | Comparar el archivo remoto de la sesión con Servers | Raíz `/home/jose/proyectos/livewire/v3/ecommerce` → `/var/www/html`. Quitar mapeos contradictorios de este servidor. |
| Conexión entrante desconocida | Diálogo de servidor y ruta del primer archivo | Elegir este servidor; el primer archivo web es `/var/www/html/public/index.php`. |
| Breakpoint no se alcanza | Línea ejecutable y flujo real | HTTP: línea ejecutable de la ruta `/`; CLI: `artisan:18`; test: `ExampleTest.php:15`. Comprobar que los breakpoints no están silenciados. |
| Pausa en cada petición | Comprobar la escucha y los breakpoints | Es el comportamiento solicitado con start_with_request=yes. Desactivar la escucha al terminar o utilizar XDEBUG_MODE=off en un CLI concreto. |
| MySQL no conecta | `docker compose ps mysql`, logs y `migrate:status` | MySQL healthy y las cuatro migraciones Ran; host externo 13306, interno 3306. |
| Composer falla | Intérprete elegido, `composer validate --strict`, `composer check-platform-reqs` | PHP Docker 8.3, extensiones correctas y ficheros editables. No ignorar requisitos. |
| Permisos incorrectos | `id`, `docker compose exec php id`, `stat -c '%u:%g %a %n' storage bootstrap/cache` | Usuario local y contenedor 1000:1000; dirs escribibles por ese propietario. No usar sudo/777. |

El registro normal de conexiones está en `/tmp/xdebug.log` dentro de PHP: `docker compose exec php cat /tmp/xdebug.log`. Se conserva mientras exista ese contenedor. Para registrar un intento CLI separado sin cambiar configuración permanente:

```sh
docker compose exec php php \
  -d xdebug.log=/tmp/xdebug-cli.log -d xdebug.log_level=7 \
  artisan route:list
docker compose exec php cat /tmp/xdebug-cli.log
```

Con IDE escuchando se espera conexión establecida hacia `host.docker.internal:9003`; sin listener el log mostrará el fallo de conexión. Si se detiene en un breakpoint, continuar en el IDE para que el comando finalice. No publicar un `phpinfo()` por HTTP para diagnosticar.

Comprobación técnica repetible, independiente del IDE:

```sh
# Detener temporalmente la escucha de PhpStorm para liberar 9003.
python3 docker/verify-xdebug.py
# Volver a activar después la escucha del IDE.
```

Primero comprueba el mapeo guardado de PhpStorm, si existe, y rechaza espacios o una raíz incorrecta. Después usa Python estándar ya disponible en Ubuntu y crea un listener temporal únicamente en la IP gateway de Docker, prueba pausas/variables sin parámetros ni variables de activación por DBGp en HTTP, Artisan y PHPUnit. Al terminar cierra el listener. No edita preferencias ni archivos PHP de la aplicación. Si el puerto está ocupado, falla sin detener su propietario.

**Verificado automáticamente:** conexión contenedor → host, puerto, arranque automático, módulos CLI/FPM, variables, rutas y pausas DBGp. **Pendiente de acción manual:** crear el intérprete/servidor en tu PhpStorm y comprobar visualmente esos breakpoints, Composer, PHPUnit y el datasource. No se ha afirmado una prueba dentro de la interfaz del IDE.

Referencias oficiales consultadas: [Docker en PhpStorm](https://www.jetbrains.com/help/phpstorm/docker.html), [intérpretes remotos](https://www.jetbrains.com/help/phpstorm/configuring-remote-interpreters.html), [Xdebug en PhpStorm](https://www.jetbrains.com/help/phpstorm/configuring-xdebug.html), [PHPUnit](https://www.jetbrains.com/help/phpstorm/using-phpunit-framework.html), [protocolo y triggers de Xdebug](https://xdebug.org/docs/step_debug).
