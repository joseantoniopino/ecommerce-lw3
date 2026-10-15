# Ecommerce — Laravel 10 y Livewire 3

Entorno local en `/home/jose/proyectos/livewire/v3/ecommerce`. Laravel está instalado directamente en la raíz. Livewire 3 se instalará durante el curso; no se han instalado starter kits ni funcionalidades de demostración. Las dependencias PHP originales del esqueleto (incluidos Sanctum, Sail, Tinker, Pint e Ignition) se conservan; Sail no gestiona este entorno. No hay usuarios creados.

## Uso diario

Desde la raíz:

```sh
cd /home/jose/proyectos/livewire/v3/ecommerce
docker compose up -d
```

Abrir **http://127.0.0.1:18080**. Xdebug está configurado con `start_with_request=yes`: activar la escucha en PhpStorm y colocar un breakpoint basta para depurar, sin triggers ni extensiones. Los comandos PHP también intentan conectar automáticamente. No hace falta arrancar Node/Vite para usar los assets ya compilados.

```sh
docker compose down
```

El proyecto Compose se llama explícitamente `livewire-v3-ecommerce`; la aplicación se identifica como `Ecommerce`, con base de datos y usuario `ecommerce`. El servidor Xdebug de PhpStorm se llama `livewire-v3-ecommerce`. Para PhpStorm, el mapeo local es `/home/jose/proyectos/livewire/v3/ecommerce` → `/var/www/html`.

La parada conserva los datos MySQL, las dependencias, las claves y los assets. El arranque no instala dependencias, no migra, no cambia propietarios y no regenera claves.

## Versiones verificadas el 15 de octubre de 2026

| Componente | Versión |
|---|---|
| PHP FPM/CLI | 8.3.35 |
| Laravel framework | 10.50.3 |
| Esqueleto laravel/laravel | 10.3.3 |
| MySQL LTS | 8.4.11 |
| Nginx estable | 1.30.6 |
| Xdebug | 3.5.3 |
| Composer | 2.10.3 |
| Node.js | 22.23.3 |
| npm | 10.9.9 |
| Vite / plugin Laravel | 7.3.7 / 2.1.0 |
| PHPUnit | 10.5.66 |
| Docker Engine / Compose del host | 29.8.2 / 5.5.1 |

El host trae Compose 5, no 2. Se utiliza la interfaz moderna `docker compose` y una configuración compatible con Compose V2 (se recomienda V2.20 o posterior). No se ha cambiado Docker del host.

Las imágenes oficiales se fijan mediante sus digests en Compose y en el Dockerfile. `composer.lock` y `package-lock.json` fijan dependencias. Las actualizaciones deliberadas requieren revisar los digests y regenerar los locks. Los paquetes Debian del Dockerfile proceden de sus repositorios: una reconstrucción futura no es una reproducción binaria exacta de esos paquetes.

Laravel 10 está fuera de soporte. Composer registra cuatro excepciones concretas de avisos de Laravel para permitir resolver esta rama exigida para aprendizaje local. **`composer audit` sigue mostrando los cuatro avisos y termina con código 1.** No se han desactivado las comprobaciones de compatibilidad PHP/extensiones ni las políticas generales de otros paquetes. Ver `VERIFICACION.md`. No publicar este entorno en Internet.

## Estructura y arquitectura

```text
.
├── app/ bootstrap/ config/ database/ public/
├── resources/ routes/ storage/ tests/
├── vendor/ node_modules/                  # dependencias locales ignoradas
├── artisan composer.json composer.lock
├── package.json package-lock.json vite.config.js
├── compose.yaml
├── .env .env.example
├── docker/
│   ├── .env .env.example                 # infraestructura / ejemplo sin secretos
│   ├── setup.php                         # preparación inicial, no se ejecuta al arrancar
│   ├── verify-xdebug.py                   # verificación DBGp desde Ubuntu
│   ├── .cache/                           # cachés de Composer y npm, ignoradas
│   ├── php/                              # Dockerfile, PHP, Xdebug y pool FPM
│   ├── nginx/default.conf
│   └── node/entrypoint.sh                 # retira public/hot al terminar Vite
├── README.md
├── PHPSTORM_SETUP.md
└── VERIFICACION.md
```

Los cuatro servicios comparten la red bridge privada del proyecto Compose. Nginx sirve únicamente `public/`, remite el front controller a `php:9000` y monta el proyecto en lectura. PHP monta la raíz en `/var/www/html` y utiliza UID/GID **1000:1000**, también en FPM. Node usa ese mismo UID/GID bajo el perfil `tools`. MySQL almacena los datos en el volumen `livewire-v3-ecommerce_mysql_data` (nombre de proyecto fijado explícitamente en Compose). No hay nombres globales de contenedor.

El healthcheck de MySQL ejecuta un `SELECT 1` autenticado con el usuario de aplicación. PHP espera a MySQL healthy; su healthcheck consulta el ping FastCGI. Nginx espera a PHP healthy y comprueba HTTP sobre el archivo estático robots.txt. PHP utiliza el ping interno de FPM, sin ejecutar la aplicación. Así las comprobaciones internas no abren sesiones de depuración. El puerto del ping FPM no está publicado.

| Servicio | Desde Ubuntu | Dentro de Docker |
|---|---|---|
| HTTP | 127.0.0.1:18080 | nginx:80 |
| MySQL | 127.0.0.1:13306 | mysql:3306 |
| FPM | Sin publicar | php:9000 |
| Xdebug | PhpStorm escucha 9003 | Conexión saliente hacia host.docker.internal:9003 |
| Vite | Sin publicar al arrancar normalmente | 5173 solo bajo demanda |

No se usan 80 ni 3306 del host. El puerto 33060 que muestra la imagen MySQL no está publicado. No se modifican servicios de Ubuntu.

## Variables, secretos y permisos

`.env` contiene exclusivamente la configuración Laravel: `DB_HOST=mysql`, `DB_PORT=3306`, base `ecommerce`, usuario `ecommerce`, URL de aplicación y clave generada. El correo usa el transportador `log` para no depender de otro servicio.

`docker/.env` contiene las credenciales de inicialización MySQL. **Solo el servicio MySQL lo carga mediante `env_file`.** Los puertos y UID/GID son valores explícitos de `compose.yaml`: no dependen de interpolar el `.env` de Laravel ni de usar `--env-file`. Las contraseñas de aplicación y root son aleatorias e independientes. Ambos archivos reales tienen permisos 600 y están ignorados por Git; los ejemplos no incluyen contraseñas ni APP_KEY.

`docker/setup.php` genera archivos ausentes sin sobrescribir los existentes, prepara directorios y comprueba la coincidencia de credenciales. No regenera APP_KEY. Cambiar contraseñas en los archivos después de inicializar MySQL **no cambia las cuentas del volumen existente**: habría que usar `ALTER USER` y sincronizar ambos archivos. No eliminar el volumen para resolverlo.

Composer, Artisan, FPM y npm crean archivos con UID/GID 1000:1000. `storage/`, `bootstrap/cache/`, `vendor/` y `node_modules/` son editables por jose. No se requiere `sudo`, permisos 777 ni cambios recursivos de propietarios al arrancar. Las cachés están en `docker/.cache/`.

## Primera instalación en otro checkout limpio

La instalación actual ya está terminada. Estos pasos son para reproducirla desde una copia del proyecto con los archivos de aplicación y locks, pero sin dependencias ni secretos.

```sh
id
ss -ltn '( sport = :18080 or sport = :13306 )'
# Deben estar libres. En otro usuario, ajustar primero ambos UID/GID de Compose.
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$PWD:/var/www/html" -w /var/www/html \
  php:8.3-fpm-bookworm@sha256:f768bd9142444f6126a690697b028c23f30878c3b628a7c355dfce75e29cc045 \
  php docker/setup.php

docker compose config --quiet
docker compose build php
docker compose up -d mysql php
docker compose exec php composer install --no-interaction --prefer-dist
docker compose exec php php artisan key:generate
docker compose exec php php artisan migrate --force
docker compose run --rm node npm ci
docker compose run --rm node npm run build
docker compose up -d --wait
docker compose exec php php artisan test
```

No copiar antes los `.env.example` a los archivos reales: el script completa sus valores de forma coherente. Si ya existen, el script los conserva; reconciliar manualmente cualquier discrepancia que señale. No ejecutar `key:generate` sobre una aplicación que ya tenga datos cifrados.

La instalación inicial de este proyecto descargó el esqueleto 10.3.3 con `composer create-project --no-install --no-scripts` en `/tmp/laravel10` dentro del contenedor. Se copiaron los archivos a la raíz tras comprobar colisiones; se conservó el `.gitignore` preparado y se sustituyó el README estándar tras leerlo. Se retiró el directorio temporal. No hay que repetir `create-project` en un checkout de este proyecto.

## Comandos de trabajo

```sh
docker compose ps
docker compose logs -f --tail=100
docker compose logs --tail=100 php nginx mysql
docker compose exec php php -v
docker compose exec php composer --version
docker compose exec php composer install
docker compose exec php composer check-platform-reqs
docker compose exec php composer audit
docker compose exec php php artisan route:list
docker compose exec php php artisan migrate
docker compose exec php php artisan migrate:status
docker compose exec php php artisan optimize:clear
docker compose exec php php artisan test
docker compose exec php php vendor/bin/phpunit
docker compose run --rm node npm install
docker compose run --rm node npm ci
docker compose run --rm node npm run build
docker compose run --rm node npm audit
```

`npm install` actualiza el lock según las restricciones; `npm ci` reproduce el lock y reemplaza `node_modules/`. Composer y npm se ejecutan en Docker, sin instalaciones globales en Ubuntu. El bootstrap original de Laravel conserva sus rutas, tests y migraciones.

Para reconstruir PHP tras cambiar sus INI o Dockerfile:

```sh
docker compose build php
docker compose up -d --wait
```

Esto conserva el volumen y los archivos. No usar `down -v`, comandos de prune ni migraciones destructivas para reiniciar el entorno.

## Vite bajo demanda

```sh
ss -ltn '( sport = :5173 )'
docker compose run --rm -p 127.0.0.1:5173:5173 node npm run dev
```

Dejar la terminal abierta y visitar la aplicación en **http://127.0.0.1:18080**. Vite escucha dentro del contenedor en 0.0.0.0:5173; Docker solo publica loopback. HMR apunta al navegador en 127.0.0.1:5173 y el puerto es estricto. Se probó `/@vite/client` con HTTP 200.

Detener con Ctrl+C. El entrypoint elimina `public/hot` al terminar por señal normal para volver a utilizar `public/build/manifest.json`. Si el proceso muere con SIGKILL y queda un marcador obsoleto, comprobar que Vite ya no está ejecutándose y retirarlo con `docker compose run --rm node rm -f public/hot`. Después ejecutar `npm run build` dentro del servicio si cambió el código.

Si 5173 está ocupado, elegir otro puerto libre y ajustar de forma coherente el mapeo de Docker, `server.port` y `hmr.clientPort` en `vite.config.js`. No detener procesos ajenos. La bienvenida original incluye sus estilos; no se modificó para añadir una interfaz de ejemplo.

## MySQL, persistencia y copias

Laravel conecta a `mysql:3306`. Un cliente ejecutado en Ubuntu o PhpStorm conecta a `127.0.0.1:13306`, base `ecommerce`, usuario `ecommerce`, contraseña `MYSQL_PASSWORD` de `docker/.env`.

```sh
# Cliente del contenedor; introducir la contraseña cuando la solicite.
docker compose exec mysql mysql -u ecommerce -p ecommerce
# Cliente ya instalado en Ubuntu (opcional, no instalado por esta tarea).
mysql --protocol=TCP -h 127.0.0.1 -P 13306 -u ecommerce -p ecommerce
# Inspección del volumen, sin modificarlo.
docker volume inspect livewire-v3-ecommerce_mysql_data
```

El nombre de proyecto está fijado como `livewire-v3-ecommerce` en `compose.yaml`: mover la carpeta no cambia por sí solo el volumen. Cambiar deliberadamente ese nombre sí seleccionaría otros recursos. `docker compose down` conserva el actual. Se verificó un ciclo completo de parada y arranque con la misma identidad de MySQL, cuatro migraciones y cero usuarios.

Copia lógica desde la raíz (los ficheros quedan fuera de Git). La contraseña se utiliza dentro del contenedor y no aparece como argumento del cliente:

```sh
mkdir -p docker/backups
backup_path="docker/backups/ecommerce-$(date +%Y%m%d-%H%M%S).sql"
(umask 077; docker compose exec -T mysql sh -c \
  'MYSQL_PWD="$MYSQL_PASSWORD" exec mysqldump --single-transaction --no-tablespaces -u "$MYSQL_USER" "$MYSQL_DATABASE"' \
  > "$backup_path")
```

Comprobar que el comando termina con código 0 y que el fichero tiene contenido. Copiar también el `.env` con APP_KEY de forma privada si se necesita recuperar datos cifrados. El directorio de copias está ignorado.

La restauración modifica las tablas existentes; realizarla solo deliberadamente sobre la base adecuada y tras guardar una copia actual:

```sh
docker compose exec -T mysql sh -c \
  'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql -u "$MYSQL_USER" "$MYSQL_DATABASE"' \
  < docker/backups/archivo-elegido.sql
```

Sustituir la ruta final por una copia real. La restauración de la copia `docker/backups/ecommerce-before-move.sql` se ha probado y comparado con el esquema y datos de origen; véase `VERIFICACION.md`.

## Diagnóstico

| Síntoma | Comprobación y acción |
|---|---|
| Puerto ocupado | `ss -ltn`; elegir otro loopback en Compose y actualizar APP_URL, setup.php y guía del IDE. No detener servicios ajenos. |
| MySQL no saludable | `docker compose logs mysql`; revisar credenciales existentes y salud autenticada. No borrar datos. |
| Error 502 | `docker compose ps`, `docker compose logs php nginx`, `docker compose exec php php-fpm -t`. FPM debe escuchar en 9000. |
| Error de permisos | `id`, `docker compose exec php id`, `stat storage bootstrap/cache`. Deben coincidir UID/GID 1000:1000. Corregir el origen concreto; no usar 777. |
| Cambio PHP no aplicado | INI copiados a imagen: reconstruir PHP y ejecutar `up -d`. Opcache revalida el código en cada petición. |
| Fallo de assets | Revisar `public/hot`, proceso Vite y `public/build/manifest.json`; compilar con el servicio Node. |
| Composer bloquea una actualización | Leer el aviso; las excepciones actuales son concretas. No desactivar políticas globalmente ni ignorar requisitos de plataforma. |
| Xdebug / PhpStorm | Seguir `PHPSTORM_SETUP.md`; `python3 docker/verify-xdebug.py` prueba el protocolo sin cambiar el IDE. |

Referencias utilizadas: [variables de Compose](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/), [políticas de Composer](https://getcomposer.org/doc/06-config.md), [Xdebug](https://xdebug.org/docs/step_debug). La evidencia concreta de esta instalación está en `VERIFICACION.md`.
