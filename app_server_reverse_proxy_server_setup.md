# Setting up a Production-Ready API

## Step 1: Create a Self-Signed Private Key and Public Certificate for HTTPS

Git Bash is installed together with various UNIX utilities. One of these utilities is **OpenSSL**.
Execute the following in a terminal to confirm that you have OpenSSL installed:

```shell
openssl --version
```

If you do not have OpenSSL, re-install Git Bash from here: [https://git-scm.com/downloads](https://git-scm.com/downloads)

Run the following command in the **Git Bash** terminal to generate the public certificate using OpenSSL:

```shell
cd container-volumes/nginx
mkdir certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/selfsigned.key \
  -out certs/selfsigned.crt
```

Answer the prompts that follow as you see fit.

The command does the following 2 tasks:

1. Creates a new private key → **certs/selfsigned.key**
This is secret. YOU SHOULD NOT SHARE IT PUBLICLY.
Nginx uses it to prove it is the server.

2. Creates a new public certificate → **certs/selfsigned.crt**
This is the self-signed certificate.
It contains the “public half” of your identity.
Browsers use it to set up encrypted communication.

Key Points to Note:

1. With a Self-Signed Certificate (our current setup for educational purposes):
We generate **both the private key (.key) and the certificate (.crt)** ourselves.
The browser says: “I do not know this Certificate Authority that issued this
certificate (you issued the certificate yourself), so I cannot trust this identity.”
Encryption works (data is scrambled), but identity is not trusted.
Anyone could generate a certificate for localhost or even google.com if it is self-signed.

2. With a Trusted Certificate Authority (real-world setup)
You create a Certificate Signing Request (CSR)
This file contains your domain name (e.g., yourdomain.co.ke) and your public key.
You generate the public key from your private key.
You send the CSR to a Certificate Authority (CA)

Examples of CAs: Let’s Encrypt (free), DigiCert, GlobalSign, etc.

The CA confirms that you actually own yourdomain.co.ke.
With Let’s Encrypt, this happens automatically by proving DNS or serving a token via HTTP.

The CA then signs your CSR
This produces a certificate (yourdomain.crt) that says:
“The CA vouches that the owner of this public key really controls yourdomain.co.ke.”

The difference is that browsers trust your public certificate because they already trust the CA.

You can then deploy the certificate + private key in Nginx
Example in nginx.conf:

```config
ssl_certificate     /etc/nginx/certs/yourdomain.crt;
ssl_certificate_key /etc/nginx/certs/yourdomain.key;
```

This deployment is done when the Nginx image is built and the updated configuration ([container-volumes/nginx/nginx.conf](container-volumes/nginx/nginx.conf)) file is uploaded to Nginx.

## Step 2: Use Docker Compose

The building of the images in Step 3 and Step 4 below is done using the following Docker Compose file: [Docker-Compose.yaml](Docker-Compose.yaml). Execute the following to build the images and run the Docker containers:

`docker compose -f Docker-Compose.yaml up --scale flask-gunicorn-app=2 -d`

## Step 3: Create the Application Server

The application server is made up of **Gunicorn**, a Web-Server Gateway Interface (WSGI) application server.
**Gunicorn** runs in a **Python** environment to access **Flask**. Flask serves the model trained using Python through an API.
![Request Flow](frontend/RequestFlow.png)

Build the following Dockerfile to create the Gunicorn WSGI application server: [Dockerfile.flask-gunicorn-app](Dockerfile.flask-gunicorn-app)
Note that the application server also contains Python and Flask installed. We can scale up/down the number of application servers.

## Step 4: Create the Reverse Proxy

The reverse proxy is made up of the **NGINX** web server.
![Proxies](frontend/Proxies.png)

A reverse proxy:

- Terminates SSL (handles HTTPS).
- Routes requests to the right backend service (`/api` → Gunicorn, `/static` → static web files).
- Load balances between multiple backend instances.
- Caches responses (e.g., static images, JSON).
- Shields backend servers from direct exposure to the internet (security).

Build the following Dockerfile to create the NGINX web server that will be assigned the role of a reverse proxy: [Dockerfile.nginx](Dockerfile.nginx)
