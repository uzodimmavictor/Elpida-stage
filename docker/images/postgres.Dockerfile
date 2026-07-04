FROM postgres:17

# Update and install additional tools if necessary. 
# (Note: postgresql-client is already included in postgres:latest)
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 5432
CMD ["postgres"]
