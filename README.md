# Boring serverless

## Deployment

### Recommended

1. Clone this repository on your server.

```
$ git clone https://github.com/pipalacademy/boring-serverless && cd boring-serverless
```

2. Make sure you have Python3.9 or above installed. Then, create a `virtualenv` and install dependencies:

```
$ # installing python3.9 on debian/ubuntu
$ sudo apt-get install python3.9 python3.9-venv
$ python3.9 -m ensurepip
```

```
$ # create virtual env, and install requirements
$ python3.9 -m venv venv
$ venv/bin/python -m pip install -r requirements.txt
```

3. Install apache server. For example, on Debian/Ubuntu:
```
$ sudo apt-get install apache2
```

4. All set! Now change the sample files in deployment/ to use your domain and the directory where you cloned it.
Then, `cp` them to the corresponding routes in your server. You can also use symlinks instead.

```
# symlink
$ sudo ln -s "$(pwd)/deployment/etc/apache2/sites-available/boring.conf" "/etc/apache2/sites-available/boring.conf"
```

5. Enabling apache mods and the site:

```
$ sudo a2enmod cgid rewrite
$ sudo a2ensite boring
```

6. (optional) Enabling SSL.

For a non-wildcard URL, you can use [certbot with apache plugin](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-20-04).

However, for wildcard URLs, you will have to go to your DNS settings and add a TXT entry as part of the process.

```
sudo certbot certonly --manual --preferred-challenges=dns -d '*.rajdhani.example.com'
```

certbot will then give you some text that it will ask you to add as a TXT entry on a particular hostname.
Once you do that, a certificate and private key will be generated for you.

Then use the apache configuration in [`boring-with-ssl.conf`](/deployment/etc/apache2/sites-available/boring-with-ssl.conf)
instead of `boring.conf`, and replace the SSL certificate/keyfile paths with your paths.
