# Создание приватного ключа

openssl genrsa -out jwt-private.pem 2048

# Создание публичного ключа на основе приватного

openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
