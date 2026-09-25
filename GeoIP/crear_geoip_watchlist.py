import csv
import ipaddress

DB = "IP2LOCATION-LITE-DB11.CSV" # --> DataBase free: https://www.ip2location.com/file-download
IPS = "attackerip_list.txt"
OUTPUT = "geoip.csv"

ips = set()

with open(IPS, encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        try:
            ip = ipaddress.IPv4Address(line)
            ips.add(int(ip))
        except ValueError:
            print(f"IP ignorada: {line}")

print(f"IPs a buscar: {len(ips)}")

encontradas = 0

with open(DB, encoding="utf-8") as infile, \
     open(OUTPUT, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    writer.writerow([
        "network",
        "country",
        "region",
        "city",
        "latitude",
        "longitude"
    ])

    for row in reader:
        if len(row) < 8:
            continue

        ip_from = int(row[0])
        ip_to = int(row[1])

        encontrados = [
            ip for ip in ips
            if ip_from <= ip <= ip_to
        ]

        if not encontrados:
            continue

        country = row[2]
        region = row[4]
        city = row[5]
        latitude = row[6]
        longitude = row[7]

        if country == "-":
            continue

        for ip in encontrados:
            writer.writerow([
                f"{ipaddress.IPv4Address(ip)}/32",
                country,
                region,
                city,
                latitude,
                longitude
            ])

            encontradas += 1
            ips.remove(ip)

        if not ips:
            break

print()
print(f"IPs encontradas: {encontradas}")
print(f"IPs sin información GeoIP: {len(ips)}")
print(f"Archivo generado: {OUTPUT}")