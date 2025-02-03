# # Use base image
# FROM hyperledger/besu:22.10.0-RC2

# # Define working directory
# WORKDIR /besu-config

# # Copy local config files to image
# COPY ./initialGenesis.json /besu-config
# COPY ./config.toml /besu-config
# COPY ./permissions_config.toml /besu-config

# # Set user to root
# USER root

# ENTRYPOINT ["/bin/bash", "-c", "besu operator generate-blockchain-config --config-file=/besu-config/initialGenesis.json --to=/besu-config/networkFiles --private-key-file-name=key && while true; do sleep 30; done;"]

# Use base image
FROM hyperledger/besu:22.10.0-RC2

# Define working directory
WORKDIR /besu-config

# Set user to root
USER root

# Comando de generación de archivos
ENTRYPOINT ["/bin/bash", "-c", "besu operator generate-blockchain-config --config-file=/besu-config/initialGenesis.json --to=/besu-config/networkFiles --private-key-file-name=key && while true; do sleep 30; done;"]
