# ---------------------------------------------------------------------
# Import Module

import re
import requests
import json
import csv
import time
import folium
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# Variable

regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'  # apache log format
map = folium.Map(location=[48.85, 2.34], zoom_start=3)  # creating map with start point at Paris

# ---------------------------------------------------------------------
# Fonction

# Parsing apache log in list
def parsing(file):
    print("Début parsing --")
    ans = []
    f = open(file, 'r')
    for line in f.readlines():
        ans.append(re.match(regex, line).groups())
    print("-- Fin parsing --")
    return ans

# Getting json infos with input log-apache-parsing output list of dictionaries
def ip_to_info_json(list_ip_log_info):
    print("-- Début ip to json --")
    current = 1
    output = []
    ip_alr_check = []
    ll = log_to_ip_list(log_apache_parsing)
    for i in list_ip_log_info:
        if i[0] not in ip_alr_check:
            good = 0
            while good != 1:
                try:
                    print(current, "ip sur", len(ll), "ip", end="\r")
                    response = requests.get(
                        'https://api.freegeoip.app/json/{}?apikey=045324a0-5747-11ec-819a-43a1b701a3ac'.format(i[0]))
                    # api key freegeoip.app '045324a0-5747-11ec-819a-43a1b701a3ac' // 15000 requests/h
                    result = response.content.decode()
                    output.append(json.loads(result))
                    good = 1
                    current += 1
                    ip_alr_check.append(i[0])
                except:
                    print("Erreur venant du site, attente de 20 secondes pour recommencer", end="\r")
                    time.sleep(20)
    print("-- FIN ip to json --")
    return output

# Converting log infos into list of ip
def log_to_ip_list(list_ip_log_info):
    print("Start convert log to ip list")
    list_ip = []
    for i in list_ip_log_info:
        if i[0] not in list_ip:
            list_ip.append(i[0])
    print("-- Fin conversion des ip--")
    return list_ip

# Getting 'country_name' of ip in list
def country(list_ip_log_info):
    print("-- Début country")
    output = {}
    output["total"] = 0
    for i in list_ip_log_info:
        coty = i['country_name']
        if coty in output.keys():
            output[coty] += 1
            output["total"] += 1
        else:
            output[coty] = 1
            output["total"] += 1
    print("-- Fin country -- ")
    return output
#oui
# Creating marks on map
def position_on_map(list_ip_log_info):
    print("-- Debut positionnement sur la carte --")
    for i in list_ip_log_info:
        folium.Marker([i["latitude"], i["longitude"]], popup="<i>{}</i>".format(i), tooltip=i['ip']).add_to(map)
    map.save("index1.html")
    print("-- Toute les ip on était placé sur la carte disponible dans le 'index.html' --")

# Exporting into CSV file
def export_csv(list_ip_log_info):
    print("-- Debut conversion en format .csv --")
    writer = csv.writer(open("out1.csv", "w"))
    writer.writerows(list_ip_log_info)
    print("-- FIN conversion CSV--")

# Exporting into JSON file
def export_json(list_ip_log_info):
    writer = open("out1.json", "w")
    writer.write(json.dumps(list_ip_log_info, indent=4, separators=(";", ":")))
    writer.close()
#oui
# Exporting into XML file
def export_xml(list_ip_log_info):
    # create root and sub element
    usrconfig = ET.Element("usrconfig")
    usrconfig = ET.SubElement(usrconfig, "usrconfig")
    # insert list element into sub elements
    for user in range(len(list_ip_log_info)):
        usr = ET.SubElement(usrconfig, "usr")
        usr.text = str(list_ip_log_info[user])
    tree = ET.ElementTree(usrconfig)
    # write the file
    tree.write("out1.xml", encoding='utf-8', xml_declaration=True)
#oui
# Creating graph of country connexions
def graphic_creation(country_info):
    print(country_info)
    height = []
    bars = []
    for key, value in country_info.items():
        if key != 'total':
            height.append(value)
            bars.append(key)

    y_pos = np.arange(len(bars))
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars, rotation = 90)
    plt.savefig('graph1.png', bbox_inches='tight')
    plt.title(label="Country graph",fontsize=30,color="red")
    plt.show()

# ---------------------------------------------------------------------
# Affichage
print("-- Début programme -- ")
log_apache_parsing = parsing('Log-Aapche-petit.log') #log --> list
ip_info = ip_to_info_json(log_apache_parsing)  # ip info de list --> list[{info1},{info2}]

position_on_map(ip_info)
print(country(ip_info))
export_csv(log_apache_parsing)
export_xml(log_apache_parsing)
export_json(log_apache_parsing)

graphic_creation(country(ip_info))
print("-- FIN programme -- ")

# https://www.python-graph-gallery.com/barplot/