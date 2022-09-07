# Boring serverless

## Deployment

### Recommended

1. Clone this repository on your server.

```
git clone https://github.com/pipalacademy/boring-serverless && cd boring-serverless
```

2. Make sure you have Python3.9 or above installed. Then, create a `virtualenv` and install dependencies:

```
python3.9 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

3. All set! Now change the sample files in deployment/ to use your domain and the directory where you cloned it.
Then, `cp` them to the corresponding routes in your server.

4. Start the systemd service for boring-api:

```
sudo systemctl enable boring-api.service
```

`curl localhost:8000` should now print `Works!`.

5. Enabling apache mods and the site:

```
sudo a2enmod mod_cgid mod_proxy mod_proxy_http
sudo a2ensite boring
```

6. (optional) Enabling SSL.

Use certbot with apache to setup SSL.
