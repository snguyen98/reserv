import secrets

try:
    with open('src/app/app.key', 'x') as f:
        f.write(secrets.token_hex())
        f.close()

except:
    print("Error: App key already exists, cannot overwrite existing key")