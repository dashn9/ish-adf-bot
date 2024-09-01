#!/bin/bash

# This script generates a certificate for a given Kubernetes component with SANs support and optional group details

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
    local GROUP_DETAILS=""

    # Parse remaining arguments for DNS names, IP addresses, and group details
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
            --group)
                GROUP_DETAILS="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Create the necessary directories if they don't exist
    mkdir -p "$OUTPUT_DIR/certs" "$OUTPUT_DIR/configs"

    # Paths to the key and cert files for this component
    local KEY_FILE="$OUTPUT_DIR/certs/$NAME.key"
    local CSR_FILE="$OUTPUT_DIR/certs/$NAME.csr"
    local CERT_FILE="$OUTPUT_DIR/certs/$NAME.crt"
    local CONFIG_FILE="$OUTPUT_DIR/configs/$NAME.cnf"

    # Create the configuration file for the certificate
    cat > "$CONFIG_FILE" <<EOF
[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
EOF
    # Conditionally add req_extensions if SANs are provided
    if [[ -n "$DNS_NAMES" || -n "$IP_ADDRESSES" ]]; then
        echo "req_extensions     = req_ext" >> "$CONFIG_FILE"
    fi

    cat >> "$CONFIG_FILE" <<EOF
distinguished_name = dn

[ dn ]
CN = $CN
EOF

    # Add group details if provided
    if [[ -n "$GROUP_DETAILS" ]]; then
        echo "OU = $GROUP_DETAILS" >> "$CONFIG_FILE"
    fi

    # Add req_ext section if DNS names or IP addresses are provided
    if [[ -n "$DNS_NAMES" || -n "$IP_ADDRESSES" ]]; then
        echo -e "\n[ req_ext ]" >> "$CONFIG_FILE"
        echo "subjectAltName = @alt_names" >> "$CONFIG_FILE"
        echo "[ alt_names ]" >> "$CONFIG_FILE"

        # Add DNS names to the configuration file
        local index=1
        IFS=',' read -ra ADDR <<< "$DNS_NAMES"
        for dns in "${ADDR[@]}"; do
            echo "DNS.$index = $dns" >> "$CONFIG_FILE"
            index=$((index + 1))
        done

        # Add IP addresses to the configuration file
        local ip_index=1
        IFS=',' read -ra ADDR <<< "$IP_ADDRESSES"
        for ip in "${ADDR[@]}"; do
            echo "IP.$ip_index = $ip" >> "$CONFIG_FILE"
            ip_index=$((ip_index + 1))
        done
    fi

    # Generate the private key
    openssl genrsa -out "$KEY_FILE" 2048
    if [[ $? -ne 0 ]]; then
        echo "Error generating private key for $NAME"
        exit 1
    fi

    # Generate the CSR using the configuration file
    openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -config "$CONFIG_FILE"
    if [[ $? -ne 0 ]]; then
        echo "Error generating CSR for $NAME"
        exit 1
    fi

        # Sign the certificate with the CA
    if [[ -n "$DNS_NAMES" || -n "$IP_ADDRESSES" ]]; then
        openssl x509 -req -in "$CSR_FILE" -CA "$CA_CERT" -CAkey "$CA_KEY" -CAcreateserial -out "$CERT_FILE" -days 3650 -sha256 -extensions req_ext  -extfile "$CONFIG_FILE"
    else
        openssl x509 -req -in "$CSR_FILE" -CA "$CA_CERT" -CAkey "$CA_KEY" -CAcreateserial -out "$CERT_FILE" -days 3650 -sha256 -extfile "$CONFIG_FILE"
    fi

    if [[ $? -ne 0 ]]; then
        echo "Error signing certificate for $NAME"
        exit 1
    fi

    # Set permissions on the key file
    chmod 600 "$KEY_FILE"
}

# Check if the required arguments are provided
if [ "$#" -lt 5 ]; then
    echo "Usage: $0 <name> <common_name> <output_dir> <ca_key> <ca_cert> [--dns dns_names_comma_separated] [--ip ip_addresses_comma_separated] [--group group_details]"
    exit 1
fi

# Call the function with the provided arguments
generate_cert "$@"
