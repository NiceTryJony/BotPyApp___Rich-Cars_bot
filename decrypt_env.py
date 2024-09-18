#(import) subprocess

#def decrypt_env_gpg():
 #   try:
  #      subprocess.run(['gpg', '--decrypt', '--output', '.env', '.env.gpg'], check=True)
   # except subprocess.CalledProcessError as e:
    #    print(f"Error decrypting .env.gpg: {e}")
     #   raise
