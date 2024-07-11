import secrets
import logging

def generate_key(key_path):
    """
    Generates a new app key to the given file path

    Params
    ------
    key_path        The path to save the newly generated key
    """
    try:
        with open(key_path, 'x') as f:
            f.write(secrets.token_hex())
            f.close()
            
            logging.info("New app key generated")

    except Exception as e:
        logging.error("Error: App key already exists, cannot overwrite existing key")