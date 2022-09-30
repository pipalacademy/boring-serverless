# Hamr

> Dead simple tool to nail your deployments.

Hamr (pronounced "Hammer") is a next-gen open-source self-hosted serverless platform.

## Usage

Hamr is to be setup on a machine - a raspberry PI, a cloud VM.
Then, it gives an API to deploy apps to that machine.

The apps don't live as a long-running process, and each app is invoked when a HTTP request
is received for it. This is accomplished with CGI.

## Deployment

### Recommended

1. Clone this repository on your server.
    ```
    $ git clone https://github.com/pipalacademy/hamr && cd hamr
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

4. Give Apache user access to apps/ directory. Apache user (maybe `www-data` or `apache`) needs to be given
access to the apps/ directory so that it can create directories there.

    ```
    $ mkdir apps
    $ sudo chown www-data:www-data apps
    ```

5. All set! Now change the sample files in deployment/ to use your domain and the directory where you cloned it.
Then, `cp` them to the corresponding routes in your server. You can also use symlinks instead.

    ```
    $ # symlink
    $ sudo ln -s "$(pwd)/deployment/etc/apache2/sites-available/hamr.conf" "/etc/apache2/sites-available/hamr.conf"
    ```

6. Enabling apache mods and the site:

    ```
    $ sudo a2enmod cgid rewrite vhost_alias
    $ sudo a2ensite hamr
    ```

7. \[Optional] Enabling SSL.

    For a non-wildcard URL, you can use [certbot with apache plugin](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-20-04).

    For wildcard URLs, the process is different and a temporary record needs to be added as part of the process. There are
    two alternatives:
    1. With a certbot plugin for your DNS provider (here, DigitalOcean).
       You will need to [generate an API key in DigitalOcean](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
       and follow this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-let-s-encrypt-wildcard-certificates-with-certbot).
       
       To auto-renew, you can run `crontab -e` and add a line like this - to run the renewal script every 3 months:
       ```
       0 0 1 */3 * sudo certbot certonly --force-renew --dns-digitalocean -n -d '*.rajdhani.example.com'
       ```

    2. Manually
        ```
        $ sudo certbot certonly --manual --preferred-challenges=dns -d '*.rajdhani.example.com'
        ```

        certbot will then give you some text that it will ask you to add as a TXT entry on a particular hostname.
        Once you do that, a certificate and private key will be generated for you.

     Then use the apache configuration in [`hamr-with-ssl.conf`](/deployment/etc/apache2/sites-available/hamr-with-ssl.conf)
     instead of `hamr.conf`, and replace the SSL certificate/keyfile paths with your paths.

## Timeouts

By default, Apache has a timeout for CGI scripts set to 20 seconds.
This configuration can be changed with the [`CGIDScriptTimeout` directive](https://httpd.apache.org/docs/trunk/mod/mod_cgid.html#cgidscripttimeout).

Since both deployments and user apps are served as CGI scripts, this timeout will apply to both.

## Test environment

To activate a test configuration, you can use environment variables.

In `config.yml`, create another dictionary similar to `env` named `test_env` that
would override the environment variables in testing environment.

The testing environment will be activated when a `X-HAMR-TEST` request header is sent.
