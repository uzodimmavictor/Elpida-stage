FROM influxdb:1.8.3

EXPOSE 8086
WORKDIR /var/lib/influxdb
CMD ["influxd"]
