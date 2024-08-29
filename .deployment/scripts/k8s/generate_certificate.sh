#!/bin/bash

# This script generates a certificate for a given Kubernetes component with SANs support

# Function to generate a certificate
generate_cert() {
    local NAME=$1
    local CN=$2
    local OUTPUT_DIR=$3
    local CA_KEY=$4
    local CA_CERT=$5
    shift 5
    local DNS_NAMES=""
    local IP_ADDRESSES=""

    # Parse remaining arguments for DNS names and IP addresses
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dns)
                DNS_NAMES="$2"
                shift 2
                ;;
            --ip)
                IP_ADDRESSES="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Create the directory if it doesn't exist
    mkdir -p "$OUTPUT_DIR"

    # Paths to the key and cert files for this component
    local KEY_FILE="$OUTPUT_DIR/$NAME.key"
    local CSR_FILE="$OUTPUT_DIR/$NAME.csr"
    local CERT_FILE="$OUTPUT_DIR/$NAME.crt"
    local CONFIG_FILE="$OUTPUT_DIR/$NAME.cnf"

    # Create the configuration file for the certificate
    cat > "$CONFIG_FILE" <<EOF
[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[ dn ]
CN = $CN

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
EOF

    # Add DNS names to the configuration file
    local index=1
    IFS=',' read -ra ADDR <<< "$DNS_NAMES"
    for dns in "${ADDR[@]}"; do
        echo "DNS.$index = $dns" >> "$CONFIG_FILE"
        index=$((index + 1))
    done

    # Add IP addresses to the configuration file
    IFS=',' read -ra ADDR <<< "$IP_ADDRESSES"
    local ip_index=1
    for ip in "${ADDR[@]}"; do
        echo "IP.$ip_index = $ip" >> "$CONFIG_FILE"
        ip_index=$((ip_index + 1))
    done

    # Generate the private key
    openssl genrsa -out "$KEY_FILE" 2048

    # Generate the CSR using the configuration file
    openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -config "$CONFIG_FILE"

    # Sign the certificate with the CA
    openssl x509 -req -in "$CSR_FILE" -CA "$CA_CERT" -CAkey "$CA_KEY" -CAcreateserial -out "$CERT_FILE" -days 3650 -sha256 -extensions req_ext -extfile "$CONFIG_FILE"
}

# Check if the required arguments are provided
if [ "$#" -lt 5 ]; then
    echo "Usage: $0 <name> <common_name> <output_dir> <ca_key> <ca_cert> [--dns dns_names_comma_separated] [--ip ip_addresses_comma_separated]"
    exit 1
fi

# Call the function with the provided arguments
generate_cert "$@"
