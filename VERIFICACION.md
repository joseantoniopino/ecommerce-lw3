# Verificación de Ecommerce — Laravel 10 y Livewire 3

Instalación: **15 de octubre de 2026**. Última actualización de Xdebug: **16 de octubre de 2026**, Europe/Madrid.

**Configuración vigente: `xdebug.start_with_request=yes`. Las peticiones HTTP y comandos PHP inician depuración automáticamente, sin parámetros ni cookies. Los apartados anteriores sobre trigger documentan pruebas históricas y ya no describen la configuración activa.**
Raíz definitiva: **`/home/jose/proyectos/livewire/v3/ecommerce`**.
URL: **http://127.0.0.1:18080**.

Esta revisión se ejecutó desde la carpeta definitiva. Las pruebas descritas como correctas se realizaron realmente. Las comprobaciones visuales de PhpStorm permanecen como acción manual.

## Identidad y configuración

| Elemento | Valor comprobado |
|---|---|
| Nombre de aplicación | `Ecommerce` |
| Proyecto Compose | `livewire-v3-ecommerce`, explícito en compose.yaml |
| Servicios | php, nginx, mysql; node auxiliar bajo demanda |
| Contenedores | livewire-v3-ecommerce-php-1, livewire-v3-ecommerce-nginx-1, livewire-v3-ecommerce-mysql-1 |
| Imagen PHP | livewire-v3-ecommerce-php:latest |
| Red | livewire-v3-ecommerce_default |
| Volumen persistente | livewire-v3-ecommerce_mysql_data |
| Base de datos | ecommerce |
| Usuario de aplicación MySQL | ecommerce |
| Cookie de sesión | ecommerce_session |
| Servidor PhpStorm/Xdebug | livewire-v3-ecommerce |
| PHP_IDE_CONFIG | serverName=livewire-v3-ecommerce |
| Mapeo | /home/jose/proyectos/livewire/v3/ecommerce → /var/www/html |
| HTTP host | 127.0.0.1:18080 |
| MySQL host | 127.0.0.1:13306 |
| PHP-FPM | php:9000, sin publicar |
| Xdebug | Conexión saliente hacia host.docker.internal:9003, sin publicar |
| Vite | 127.0.0.1:5173 solo durante su prueba; detenido al finalizar |

Se inspeccionaron los bind mounts reales de PHP y Nginx: ambos apuntan a la raíz definitiva sin otro directorio intermedio. No hay otra copia ni enlace en la ubicación previa. No se instalaron componentes ni se cambiaron servicios globales de Ubuntu.

## Versiones comprobadas

| Componente | Versión |
|---|---|
| Laravel framework | 10.50.3 |
| PHP CLI/FPM | 8.3.35 |
| MySQL | 8.4.11 |
| Xdebug | 3.5.3 |
| Composer | 2.10.3 |
| Node.js | 22.23.3 |
| npm | 10.9.9 |
| Vite / plugin Laravel | 7.3.7 / 2.1.0 |
| PHPUnit | 10.5.66 |
| Nginx estable, imagen fijada | 1.30.6 |

Las imágenes y locks siguen fijados; no se actualizaron las dependencias durante el traslado. Se mantienen las extensiones PHP y los ajustes de desarrollo preparados. Livewire sigue pendiente de instalación durante el curso.

## Movimiento y conservación de datos

El destino existía y estaba vacío, con UID/GID 1000:1000. Se comprobó que origen y destino estaban en el mismo sistema de archivos y se movió la carpeta completa mediante un rename atómico. No hubo mezcla con archivos de otro proyecto.

Antes de parar los servicios se inventariaron las bases y cuentas de MySQL y se generó una copia lógica completa. No había otras bases de aplicación ni cuentas adicionales que conservar. Se prepararon la base y el usuario `ecommerce` en el volumen definitivo y se restauraron tablas, datos, rutinas, eventos y triggers de la copia.

**La comparación del dump SQL completo pasó byte a byte**, incluidos esquema, datos y contadores AUTO_INCREMENT. También se contrastaron por separado los datos y los metadatos de columnas, índices y restricciones.

Copia comprobada: `docker/backups/ecommerce-before-move.sql`, **5730 bytes**, modo 600.
SHA-256 de su contenido, idéntico al dump posterior a la restauración:

```text
fd3aead3650d4eed3596ed3d3aceacfd8efbc069e3d0e5926da60a75c4fbd22e
```

Estado de las tablas conservado:

| Tabla | Filas |
|---|---:|
| migrations | 4 |
| users | 0 |
| password_reset_tokens | 0 |
| personal_access_tokens | 0 |
| failed_jobs | 0 |

Se compararon hashes de APP_KEY y de ambas contraseñas MySQL: permanecen iguales. Los secretos no se incluyen en el informe. Los recursos Docker duplicados solo se retiraron después de comprobar la restauración. Se conservan las copias SQL y la evidencia en `docker/backups/ecommerce-verification.json`, fuera de Git y con permisos 600.

## Pruebas realizadas

| Prueba | Resultado |
|---|---|
| docker compose config --quiet | Correcto |
| docker compose build php | Correcto, imagen con identidad definitiva |
| docker compose up -d --wait | PHP, Nginx y MySQL healthy |
| Reinicios de contenedores | RestartCount=0 en los tres servicios finales |
| nginx -t y php-fpm -t | Configuración válida |
| php docker/setup.php | Variables Laravel/MySQL coherentes, archivos existentes preservados |
| php artisan about | Nombre Ecommerce, Laravel 10.50.3, entorno local |
| php artisan test | 2 tests, 2 assertions, correctos |
| composer validate --strict | Correcto |
| composer check-platform-reqs | Todos los requisitos satisfechos |
| npm run build | Correcto; CSS, JS y manifest generados |
| npm audit | 0 vulnerabilidades |
| HTTP bienvenida | 200, Laravel v10.50.3 y cookie ecommerce_session |
| HTTP assets del manifest | CSS y JS devuelven 200 |
| Protección HTTP | 404 para .env, .git/config, docker/.env, vendor/autoload.php, composer.json, storage/logs/laravel.log, app/Models/User.php y phpunit.xml |
| MySQL desde Ubuntu | Conexión TCP correcta a 127.0.0.1:13306, base ecommerce, cuenta ecommerce@% |
| MySQL desde Laravel | Configuración coherente, Artisan y migraciones operativos |
| Charset/collation | utf8mb4 / utf8mb4_unicode_ci |
| Vite dev | Cliente /@vite/client devuelve 200 en loopback; HMR y public/hot correctos |
| Fin de Vite | docker stop elimina public/hot; no queda servidor Vite permanente |
| Persistencia | Ciclo completo down/up: misma identidad MySQL, datos y APP_KEY |
| Recursos ajenos | Los siete contenedores inventariados mantienen identificadores, nombres y estado |
| Rutas y permisos | Revisión de todo el proyecto, UID/GID 1000:1000, sin escritura para otros ni permisos 777 |
| Secretos | Ambos .env y copias SQL sensibles con modo 600 |
| Nombres y rutas | Barrido de contenido, rutas, enlaces y recursos Docker para detectar identidades previas |

El primer intento del cliente de prueba Vite coincidió con el breve intervalo entre la publicación del puerto Docker y el arranque del servidor y recibió un reset de conexión. Se repitió con espera acotada de disponibilidad: respondió 200, se verificó la URL HMR y se cerró correctamente el contenedor. No requirió modificar la configuración de la aplicación.

## Xdebug: prueba real de protocolo

Se ejecutó `python3 docker/verify-xdebug.py` desde la raíz definitiva. Su listener temporal se abrió solo en la IP gateway Docker y se cerró al terminar.

```text
PASS HTTP and CLI without trigger: no debugger connection
PASS HTTP/FPM: breakpoint routes/web.php:17
PASS Artisan/CLI: breakpoint artisan:18
PASS PHPUnit/CLI: breakpoint tests/Feature/ExampleTest.php:15
PASS outgoing Xdebug connections to host.docker.internal:9003; temporary listener closed
```

Las tres sesiones confirmaron PHP 8.3.35, Xdebug 3.5.3, `mode=debug,develop`, `start_with_request=trigger`, puerto 9003 y **`PHP_IDE_CONFIG=serverName=livewire-v3-ecommerce`**. HTTP confirmó `PHP_SAPI=fpm-fcgi`; Artisan y PHPUnit confirmaron `cli`. Los archivos remotos se situaron en `/var/www/html` con las líneas de pausa correctas.

Esta prueba verifica conexión y pausas DBGp. No equivale a comprobar visualmente breakpoints en PhpStorm. Su configuración no se ha modificado automáticamente.

## Auditoría Composer: limitación conocida

Se repitió `composer audit --format=json`. Finalizó con **código 1**, con los mismos cuatro avisos de laravel/framework:

- PKSA-d5tc-s1qs-h781: XSS en información de depuración.
- PKSA-m5cs-t1y6-qpcs: confusión de rutas en URL firmadas temporales.
- PKSA-3r5d-mb8f-1qw9: CRLF en validación de correo.
- PKSA-mdq4-51ck-6kdq: CRLF en validación de correo, otra fuente para el mismo advisory de GitHub.

Laravel 10 se conserva por requisito del curso. Las excepciones concretas de resolución siguen en composer.json y audit mantiene visibles los avisos. No se desactivaron políticas globales ni requisitos PHP/extensiones. Este resultado de seguridad no se marca como aprobado. npm sí terminó sin vulnerabilidades.

## Logs finales

PHP-FPM y Nginx sirven peticiones con respuesta 200, sin errores relevantes observados. MySQL está listo y mantiene visibles las advertencias de la imagen oficial sobre su CA autofirmada y el directorio de pid dentro del contenedor; no impiden el funcionamiento local. No se publican puertos adicionales.

## Comandos de referencia desde la raíz definitiva

```sh
cd /home/jose/proyectos/livewire/v3/ecommerce
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose exec php php docker/setup.php
docker compose exec php php artisan about
docker compose exec php php artisan migrate:status
docker compose exec php php artisan test
docker compose exec php composer validate --strict
docker compose exec php composer check-platform-reqs
docker compose exec php composer audit --format=json
docker compose run --rm node npm run build
docker compose run --rm node npm audit
python3 docker/verify-xdebug.py
```

La comprobación de persistencia utilizó `docker compose down` y `docker compose up -d --wait`, sin eliminar volúmenes. Se inspeccionaron también logs, montajes, nombres y etiquetas Docker, catálogos MySQL, permisos y secretos en documentación.

## Acciones manuales pendientes

- Actualizar la carpeta asociada al proyecto local de ChatGPT/Codex a `/home/jose/proyectos/livewire/v3/ecommerce`. La herramienta disponible permite cambiar el título del chat, pero no ese registro de nombre/ruta. El chat se tituló **Ecommerce — Laravel 10 y Livewire 3**.
- En PhpStorm, actualizar el archivo Compose, las rutas del intérprete y el mapeo de la raíz definitiva a `/var/www/html`.
- Configurar el servidor **livewire-v3-ecommerce** y el datasource con base y usuario **ecommerce**. Las contraseñas son las conservadas en los .env.
- Comprobar visualmente los breakpoints en el IDE siguiendo **PHPSTORM_SETUP.md**.

No se crearon configuraciones .idea, usuarios de ejemplo, funcionalidades ni paquetes adicionales. La aplicación queda arrancada y preparada para continuar el curso.


## Diagnóstico de conexión con el PhpStorm real

Se revisó el servidor guardado en el IDE y se detectó un espacio final en su mapeo remoto: `"/var/www/html "`. Esa ruta no coincide con `/var/www/html` y no contiene el archivo remoto de la aplicación. No se modificaron los archivos .idea; el usuario corrigió el valor en PhpStorm.

Antes de la corrección, una petición HTTP real con `XDEBUG_TRIGGER=1` conectó al PhpStorm que escuchaba en 9003. El IDE recibió `serverName=livewire-v3-ecommerce`, ejecutó step_into y dejó la petición pausada en public/index.php:6. Después de la corrección se repitió la petición: el mismo IDE identificó el servidor, envió run/detach y la respuesta fue HTTP 200. Al cerrar la revisión, la primera petición de diagnóstico ya no tenía una conexión de depuración activa. No fue necesario enviar señales ni reiniciar PHP-FPM; el servicio permaneció healthy.

También se ejecutaron contra el PhpStorm real, con el trigger activo:

- Artisan route:list: conexión DBGp con el IDE, run/detach y código de salida 0.
- PHPUnit: conexión DBGp con el IDE, run/detach y 2 tests / 2 assertions correctos.

Estas pruebas usaron el cliente PhpStorm real, no el cliente de prueba de Python. Los breakpoints del usuario estaban retirados para esta comprobación; no se afirma haber observado visualmente un breakpoint de usuario en routes/web.php. El código de prueba de esa ruta se conservó intacto.

El puerto HTTP 18080 se mantuvo. No impidió la conexión ni el reconocimiento del servidor. El puerto de Xdebug sigue siendo 9003. No se cambiaron puertos, versiones ni configuraciones Docker para intentar compensar el error de mapeo.

Se mejoró docker/verify-xdebug.py para comprobar también el mapeo de PhpStorm guardado, rechazar espacios en la raíz remota y localizar el return de la bienvenida aunque cambie su número de línea. Su listener de prueba requiere liberar 9003. Primero se hicieron las comprobaciones contra el IDE real mientras escuchaba; después el usuario detuvo la escucha y se ejecutó también el script completo con resultado correcto: pausa HTTP en routes/web.php:20, Artisan en artisan:18 y PHPUnit en tests/Feature/ExampleTest.php:15. Se comprobó además que no se inicia una conexión sin trigger y que el listener de prueba se cierra al terminar.


### Confirmación del breakpoint de usuario con el IDE real — 16 de octubre de 2026

En el intento inicial de esta comprobación no existía listener en 9003 y Xdebug registró `Could not connect to debugging client`. El mapeo guardado ya era correcto y el breakpoint de usuario estaba habilitado en routes/web.php:19.

Después de activar el usuario la escucha se lanzó la petición HTTP con XDEBUG_TRIGGER=1. El registro mostró el comando emitido por PhpStorm:

```text
breakpoint_set -i 13 -t line -f file:///var/www/html/routes/web.php -n 19
```

La respuesta al run fue `status=break`, archivo `file:///var/www/html/routes/web.php`, línea `19`. Las consultas de variables realizadas por el propio IDE devolvieron `$a` int 1, `$b` int 2 y `$c` sin inicializar, coherente con la pausa antes de ejecutar la suma. Esta es una parada en el breakpoint de usuario solicitada por el PhpStorm real, no por el cliente de prueba Python. El usuario puede continuar la ejecución con F9.


## Depuración automática sin trigger — 16 de octubre de 2026

Por petición expresa del usuario se cambió docker/php/xdebug.ini a `xdebug.start_with_request=yes`, manteniendo modo debug,develop y puerto 9003. Se reconstruyó la imagen y se recreó el servicio PHP.

Se lanzó una petición curl nueva a **http://127.0.0.1:18080/**, sin query string, sin cookies y sin variables de activación. PhpStorm envió el breakpoint de routes/web.php:19 y Xdebug respondió a run con `status=break`, `filename=file:///var/www/html/routes/web.php`, `lineno=19`. Esta parada se comprobó contra el IDE real.

El healthcheck de Nginx ahora consulta el archivo estático /robots.txt en lugar de ejecutar la bienvenida Laravel. PHP conserva su ping interno /ping. Se verificó que después del arranque y las comprobaciones de salud no se habían iniciado sesiones de depuración en segundo plano. La configuración final no aplica overrides PHP_ADMIN_VALUE en el ping. Los tres servicios permanecen healthy.

Se actualizaron la guía de PhpStorm, README y docker/verify-xdebug.py para utilizar URLs y comandos ordinarios, sin trigger, y comprobar start_with_request=yes. El script de verificación sigue necesitando que el listener del IDE esté apagado para poder ocupar 9003.

Para trabajar: activar la escucha en PhpStorm y colocar un breakpoint. Para continuar la petición pausada, F9. Al apagar la escucha, Xdebug sigue intentando conectar en cada petición con el timeout configurado; no se crean sesiones si el IDE no escucha. Para omitir Xdebug únicamente en un comando de mantenimiento se puede ejecutar ese comando con XDEBUG_MODE=off.
