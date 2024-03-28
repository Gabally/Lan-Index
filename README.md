# Lan Index

Web Gui to list and add a name and icon to your network devices.

Example start command:

`docker run --name lan-test -e "LISTEN_PORT=7000" -e "NETWORK_RANGE=192.168.1.1/24" --network=host --restart=unless-stopped -d lanindex`
