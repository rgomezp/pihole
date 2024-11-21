#!/bin/bash

# Start the server for the whitelisting LAN page
source /home/rodrigo/myenv/bin/activate
python3 /home/rodrigo/pihole_whitelist.py

# Auto-blacklist domains that match Admiral IP addresses

TARGET_IPS=("104.18.24.111", "104.18.25.111")

PIHOLE_LOG="/var/log/pihole.log"

is_blacklisted() {
	domain=$1
	pihole -q "$domain" | grep -q "is blocked"
	return $?
}

echo "Monitoring Pi-hole for domains resolving to ${TARGET_IPS[*]}..."

tail -F "$PIHOLE_LOG" | while read -r line; do
	for ip in "${TARGET_IPS[@]}"; do
		if echo "$line" | grep -q "reply" && echo "$line" | grep -q "$ip"; then
			domain=$(echo "$line" | awk '{print $6}')

			if ! is_blacklisted "$domain"; then
				echo "Blacklisting domain: $domain (resolved to $ip)"
				pihole --regex -b "$domain"
			fi
		fi
	done
done

