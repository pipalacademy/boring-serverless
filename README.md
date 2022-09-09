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

Use certbot with apache to setup SSL.
