services = """● var-www-clownworld-bolshevid-public-repository.mount loaded failed failed /va>
● ai-query-app.service                                 loaded failed failed AI >
● consumer.service                                     loaded failed failed Sol>
● fancontrol.service                                   loaded failed failed fan>
● pm2-your_username.service                            loaded failed failed PM2>
● rawRabbitLogs.service                                loaded failed failed Sol>
sudo systemctl stop signatureConsumer.service
sudo systemctl disable signatureConsumer.service""".split('.service')
all_services = ""
for service in services:
    if service:
        service = f"{service.split(' ')[-1]}.service".replace(' ','')
        all_services+=f"""sudo systemctl stop {service}
    sudo systemctl disable {service}\n"""
input(all_services)
