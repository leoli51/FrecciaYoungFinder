# FrecciaYoungFinder


A tool to find FrecciaYoung tickets


Trenitalia API documentation (unofficial): https://github.com/SimoDax/Trenitalia-API/wiki/Nuove-API-Trenitalia-lefrecce.it

## Run locally

1. Install poetry
2. Clone this repository
3. Run `poetry install`
4. poetry run python -m cli.main
5. 🎉

## Run as Sytemd service (Telegram Bot)

Start the service: 

```bash
# Reload systemd to recognize the new service file
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable frecciayoung-bot.service

# Start the service now
sudo systemctl start frecciayoung-bot.service
```

Check service status:

```bash
sudo systemctl status frecciayoung-bot.service
```

View logs:

```bash
sudo journalctl -u frecciayoung-bot.service -f
```

Maintenance:

```bash
# Reload
sudo systemctl daemon-reload

# Restart
sudo systemctl restart frecciayoung-bot.service

# Stop
sudo systemctl stop frecciayoung-bot.service
```