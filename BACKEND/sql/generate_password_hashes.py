"""
Generador de hashes bcrypt para contrase├▒as de usuarios
Sistema Sacra360
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Contrase├▒as para cada rol
passwords = {
    "Administrador": "Admin123!",
    "Revisor": "Revisor123!",
    "Digitalizador": "Digita123!",
    "Consultor": "Consul123!"
}

print("=" * 60)
print("GENERANDO HASHES BCRYPT PARA USUARIOS SACRA360")
print("=" * 60)
print()

for rol, password in passwords.items():
    hash_result = pwd_context.hash(password)
    print(f"­ƒöÉ {rol}:")
    print(f"   Contrase├▒a: {password}")
    print(f"   Hash: {hash_result}")
    print()

print("=" * 60)
print("Ô£à Hashes generados exitosamente")
print("=" * 60)