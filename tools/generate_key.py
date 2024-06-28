import secrets

def generate_key():
    try:
        with open('app/app.key', 'x') as f:
            f.write(secrets.token_hex())
            f.close()

    except Exception as e:
        print("Error: App key already exists, cannot overwrite existing key")
        print(e)

generate_key()