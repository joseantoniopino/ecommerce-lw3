FROM composer:2@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac AS composer
FROM php:8.3-fpm-bookworm@sha256:f768bd9142444f6126a690697b028c23f30878c3b628a7c355dfce75e29cc045

ARG LOCAL_UID=1000
ARG LOCAL_GID=1000
# mbstring, fileinfo, curl, XML, SQLite and Opcache are already in this base.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git unzip libicu-dev libzip-dev libpng-dev libjpeg62-turbo-dev libfreetype6-dev libfcgi-bin \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" pdo_mysql intl zip bcmath gd pcntl exif \
    && pecl install xdebug-3.5.3 \
    && docker-php-ext-enable xdebug \
    && rm -rf /var/lib/apt/lists/* /tmp/pear \
    && groupadd --gid "$LOCAL_GID" app \
    && useradd --uid "$LOCAL_UID" --gid "$LOCAL_GID" --create-home --shell /bin/bash app

COPY --from=composer /usr/bin/composer /usr/local/bin/composer
COPY php.ini /usr/local/etc/php/conf.d/99-development.ini
COPY xdebug.ini /usr/local/etc/php/conf.d/99-xdebug-settings.ini
COPY www.conf /usr/local/etc/php-fpm.d/www.conf
WORKDIR /var/www/html
USER app
CMD ["php-fpm"]
