mport csv
import ipaddress

entrada = "IP2LOCATION-LITE-DB11.CSV" # --> DataBase free: https://www.ip2location.com/file-download
salida = "geoip.csv"

with open(entrada, "r", encoding="utf-8") as infile, \
     open(salida, "w", newline="", encoding="utf-8") as outfile:

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
        country = row[2]
        region = row[4]
        city = row[5]
        latitude = row[6]
        longitude = row[7]

        if country == "-" or ip_from > ip_to:
            continue

        start = ipaddress.IPv4Address(ip_from)
        end = ipaddress.IPv4Address(ip_to)

        networks = ipaddress.summarize_address_range(start, end)

        for network in networks:
            writer.writerow([
                str(network),
                country,
                region,
                city,
                latitude,
                longitude
            ])
