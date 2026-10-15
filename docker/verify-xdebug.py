#!/usr/bin/env python3
"""Host-side acceptance check. Uses Python stdlib and transient Docker-gateway listener.
Run from project root, with PhpStorm's port 9003 listener stopped for this check.
It never modifies application files or IDE settings.
"""
import base64
import json
import socket
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPOSE = ['docker', 'compose']


def execute(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def receive(stream):
    length = bytearray()
    while True:
        byte = stream.read(1)
        if not byte:
            raise RuntimeError('DBGp connection closed unexpectedly')
        if byte == b'\0':
            break
        length.extend(byte)
    payload = stream.read(int(length))
    assert stream.read(1) == b'\0'
    return ET.fromstring(payload)


def command(conn, stream, name, options='', data=None):
    packet = f'{name} -i 1 {options}'.strip()
    if data is not None:
        packet += ' -- ' + base64.b64encode(data.encode()).decode()
    conn.sendall(packet.encode() + b'\0')
    result = receive(stream)
    errors = [e for e in result.iter() if e.tag.endswith('error')]
    if errors:
        raise RuntimeError(ET.tostring(result).decode())
    return result


def debug(listener, label, args, filename, line, expected_sapi):
    process = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        conn, _ = listener.accept()
        with conn:
            conn.settimeout(20)
            stream = conn.makefile('rb')
            init = receive(stream)
            assert init.get('idekey') in ('1', 'PHPSTORM'), init.attrib
            command(conn, stream, 'breakpoint_set', f'-t line -f file:///var/www/html/{filename} -n {line}')
            result = command(conn, stream, 'run')
            assert result.get('status') == 'break', ET.tostring(result)
            stack = command(conn, stream, 'stack_get')
            top = next(e for e in stack if e.tag.endswith('stack'))
            assert top.get('filename') == f'file:///var/www/html/{filename}', top.attrib
            assert int(top.get('lineno')) == line, top.attrib
            expr = 'json_encode(["sapi"=>PHP_SAPI,"php"=>PHP_VERSION,"xdebug"=>phpversion("xdebug"),"server"=>getenv("PHP_IDE_CONFIG"),"mode"=>ini_get("xdebug.mode"),"start_with_request"=>ini_get("xdebug.start_with_request"),"port"=>ini_get("xdebug.client_port"),"idekey"=>ini_get("xdebug.idekey")])'
            evaluation = command(conn, stream, 'eval', data=expr)
            prop = next(e for e in evaluation if e.tag.endswith('property'))
            data = json.loads(base64.b64decode(prop.text).decode())
            assert data['sapi'] == expected_sapi, data
            assert data['server'] == 'serverName=livewire-v3-ecommerce', data
            assert data['start_with_request'] in ('yes', '1') and data['port'] == '9003' and data['idekey'] == 'PHPSTORM', data
            command(conn, stream, 'detach')
        stdout, stderr = process.communicate(timeout=30)
        assert process.returncode == 0, (stdout, stderr)
        assert not stderr, stderr
        print(f'PASS {label}: breakpoint {filename}:{line}; {json.dumps(data)}')
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()


def check_phpstorm_mapping():
    servers = []
    present = False
    for name in ['.idea/php.xml', '.idea/workspace.xml']:
        path = ROOT / name
        if path.exists():
            present = True
            servers.extend(ET.parse(path).findall(".//component[@name='PhpServers']/servers/server"))
    if not present:
        print('SKIP PhpStorm configuration: absent; DBGp tests alone do not validate the IDE')
        return
    matching = [s for s in servers if s.get('name') == 'livewire-v3-ecommerce']
    if not matching:
        raise RuntimeError('PhpStorm server livewire-v3-ecommerce not found in saved project settings')
    mappings = [m for server in matching for m in server.findall('./path_mappings/mapping')
                if m.get('local-root') in ('$PROJECT_DIR$', str(ROOT))]
    if not mappings:
        raise RuntimeError('PhpStorm server is missing the project-root path mapping')
    for mapping in mappings:
        remote = mapping.get('remote-root', '')
        if remote != '/var/www/html':
            raise RuntimeError(f'Invalid saved PhpStorm remote root: {remote!r}; expected exactly /var/www/html (no surrounding whitespace)')
    print('PASS saved PhpStorm root mapping: exactly /var/www/html; live IDE session still requires its own check')


def main():
    check_phpstorm_mapping()
    welcome_line = next((number for number, line in enumerate((ROOT / 'routes/web.php').read_text().splitlines(), 1)
                         if "return view('welcome')" in line), None)
    if welcome_line is None:
        raise RuntimeError('Welcome-route return statement not found; update the verification target for the current application')
    gateway = execute(COMPOSE + ['exec', '-T', 'php', 'getent', 'ahostsv4', 'host.docker.internal']).split()[0]
    with socket.socket() as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((gateway, 9003))
        listener.listen(4)
        listener.settimeout(20)
        debug(listener, 'HTTP/FPM', ['curl', '--fail', '--silent', '--show-error', 'http://127.0.0.1:18080/'], 'routes/web.php', welcome_line, 'fpm-fcgi')
        prefix = COMPOSE + ['exec', '-T', 'php', 'php']
        debug(listener, 'Artisan/CLI', prefix + ['artisan', 'route:list'], 'artisan', 18, 'cli')
        debug(listener, 'PHPUnit/CLI', prefix + ['vendor/bin/phpunit', '--filter', 'test_the_application_returns_a_successful_response'], 'tests/Feature/ExampleTest.php', 15, 'cli')
        listener.settimeout(0.5)
        subprocess.run(COMPOSE + ['exec', '-T', '-e', 'XDEBUG_MODE=off', 'php', 'php', 'artisan', '--version'], cwd=ROOT, check=True)
        try:
            unexpected, _ = listener.accept()
        except TimeoutError:
            print('PASS explicit XDEBUG_MODE=off: CLI skips debugging')
        else:
            unexpected.close()
            raise RuntimeError('Unexpected debug connection with XDEBUG_MODE=off')
    print('PASS outgoing Xdebug connections to host.docker.internal:9003; temporary listener closed')


if __name__ == '__main__':
    main()
