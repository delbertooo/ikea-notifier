# IKEA Delivery Available Notifier

Sends a mail if an item is available for delivery.

## Usage

Define your slugs (the complete id part in your item's URL) and set up your
mail config.


Build the project and create a data volume:
```bash
docker build -t ikea-notifier .
docker volume create ikea-notifier-data
```

Set up a cron job with something like:
```bash
docker run --rm \
    -v ikea-notifier-data:/data \
    -e 'SLUGS=hemnes-schuhschrank-2fach-weiss-20169559:voxtorp-schubladenfront-dunkelgrau-90454100:hemnes-kommode-mit-6-schubladen-weiss-20374277' \
    -e IGNORE_FOR_SECONDS=3600 \
    -e MAIL_HOST=smtp.gmail.com \
    -e MAIL_PORT=587 \
    -e MAIL_USER=example@gmail.com \
    -e MAIL_PASS=yourPassword \
    -e MAIL_FROM=example@gmail.com \
    -e MAIL_TO=example1@gmail.com,example2@gmail.com \
    ikea-notifier
```

The `IGNORE_FOR_SECONDS` of `3600` will ignore available items for 3600
seconds (1 hour) without re-sending an email each time the tool runs.
