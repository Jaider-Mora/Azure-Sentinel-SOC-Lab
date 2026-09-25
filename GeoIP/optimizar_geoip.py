import csv
import ipaddress

entrada = "geoip.csv"
salida = "geoip_optimizado.csv"

def mismo_lugar(a, b):
    return (
        a["country"] == b["country"]
        and a["region"] == b["region"]
        and a["city"] == b["city"]
        and a["latitude"] == b["latitude"]
        and a["longitude"] == b["longitude"]
    )

def fusionar_redes(red1, red2):
    try:
        redes = list(ipaddress.collapse_addresses([
            ipaddress.ip_network(red1),
            ipaddress.ip_network(red2)
        ]))

        if len(redes) == 1:
            return str(redes[0])

    except ValueError:
        pass

    return None

with open(entrada, newline="", encoding="utf-8") as infile, \
     open(salida, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)

    campos = [
        "network",
        "country",
        "region",
        "city",
        "latitude",
        "longitude"
    ]

    writer = csv.DictWriter(outfile, fieldnames=campos)
    writer.writeheader()

    anterior = None
    procesados = 0
    fusionados = 0

    for fila in reader:
        procesados += 1

        if anterior is None:
            anterior = fila
            continue

        nueva_red = None

        if mismo_lugar(anterior, fila):
            nueva_red = fusionar_redes(
                anterior["network"],
                fila["network"]
            )

        if nueva_red:
            anterior["network"] = nueva_red
            fusionados += 1
        else:
            writer.writerow(anterior)
            anterior = fila

        if procesados % 100000 == 0:
            print(
                f"Procesados: {procesados:,} | "
                f"Fusionados: {fusionados:,}"
            )

    if anterior:
        writer.writerow(anterior)

print()
print("Proceso terminado.")
print(f"Registros procesados: {procesados:,}")
print(f"Fusionados: {fusionados:,}")
