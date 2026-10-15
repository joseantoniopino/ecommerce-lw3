<?php
// Run once on a fresh checkout as the host user; never overwrite existing env files.
declare(strict_types=1);
$root = dirname(__DIR__);
foreach (['docker/.cache/composer', 'docker/.cache/npm', 'storage/framework/cache/data', 'storage/framework/sessions', 'storage/framework/views', 'storage/logs', 'bootstrap/cache'] as $directory) {
    $path = "$root/$directory";
    if (!is_dir($path) && !mkdir($path, 0755, true)) {
        throw new RuntimeException("Cannot create $directory");
    }
}
$dockerEnv = "$root/docker/.env";
if (!file_exists($dockerEnv)) {
    $contents = "MYSQL_DATABASE=ecommerce\nMYSQL_USER=ecommerce\nMYSQL_PASSWORD=" . bin2hex(random_bytes(24)) . "\nMYSQL_ROOT_PASSWORD=" . bin2hex(random_bytes(32)) . "\n";
    file_put_contents($dockerEnv, $contents);
    chmod($dockerEnv, 0600);
}
$values = parse_ini_file($dockerEnv, false, INI_SCANNER_RAW);
if (!$values || empty($values['MYSQL_PASSWORD']) || empty($values['MYSQL_ROOT_PASSWORD']) || $values['MYSQL_PASSWORD'] === $values['MYSQL_ROOT_PASSWORD']) {
    throw new RuntimeException('docker/.env must contain independent non-empty passwords.');
}
if (!file_exists("$root/.env")) {
    $contents = file_get_contents("$root/.env.example");
    $replacements = [
        'APP_NAME' => '"Ecommerce"', 'APP_URL' => 'http://127.0.0.1:18080',
        'DB_CONNECTION' => 'mysql', 'DB_HOST' => 'mysql', 'DB_PORT' => '3306',
        'DB_DATABASE' => $values['MYSQL_DATABASE'], 'DB_USERNAME' => $values['MYSQL_USER'],
        'DB_PASSWORD' => $values['MYSQL_PASSWORD'],
    ];
    foreach ($replacements as $key => $value) {
        $contents = preg_replace('/^' . $key . '=.*$/m', $key . '=' . $value, $contents);
    }
    file_put_contents("$root/.env", $contents);
    chmod("$root/.env", 0600);
}
$laravel = parse_ini_file("$root/.env", false, INI_SCANNER_RAW);
if (!$laravel || ($laravel['DB_PASSWORD'] ?? '') !== $values['MYSQL_PASSWORD'] || ($laravel['DB_DATABASE'] ?? '') !== $values['MYSQL_DATABASE'] || ($laravel['DB_USERNAME'] ?? '') !== $values['MYSQL_USER']) {
    throw new RuntimeException('Existing Laravel and Docker database credentials differ; reconcile them manually. No existing file was overwritten.');
}
echo "Environment files preserved/created; writable directories ready. Generate APP_KEY with Artisan on first installation.\n";
