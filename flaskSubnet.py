from flask import Flask, request, render_template 
import sqlite3
import subprocess 
from markupsafe import escape
import ipaddress


connection = sqlite3.connect("sweep.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
connection.commit()
  
app = Flask(__name__)

@app.route("/")
def hello_world():
    appTop = open("appTop.html","r")
    appBody = open("appBody.html","r")
    appBottom = open("appBottom.html","r")
    html = appTop.read()
    html += appBody.read()
    # html += showTable('subnet')
    table = 'subnet'
    connection = sqlite3.connect("sweep.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    connection.commit()
    cursor.execute("SELECT * FROM " + table + ";")
    html += "<table class=\"table table-dark table-hover\">"
    html += "<tr><th>ID</th><th>IP</th><th>MAC</th></tr>"
    for row in cursor.fetchall():
        if str(dict(row)['pingable']) == '0':
            pingableClass = 'table-success'
        elif str(dict(row)['pingable']) == '1':
            pingableClass = 'table-danger'
        else:
            pingableClass = 'table-default'
        html += "<tr><td>" + str(dict(row)['ID']) + "</td><td class=\"" + pingableClass + "\">" + str(dict(row)['ip']) + "</td><td>" + str(dict(row)['mac']) + "</td></tr>\n"
    html += appBottom.read()
    # mkDatabase()
    # insertTable(subnet)
    return html

@app.route("/insertTable", methods=['POST'])
def insertTable():
    data = request.form
    cidr = data['cidr']
    connection = sqlite3.connect("sweep.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("DROP TABLE subnet;")
    connection.commit()
    cursor.execute("CREATE TABLE subnet(ID INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, mac TEXT, pingable INT);")
    connection.commit()
    for ip in list(ipaddress.ip_network(cidr).hosts()):
        cursor.execute("INSERT INTO subnet (ip) VALUES ('" + str(ip) + "');")
        connection.commit()
    html = "<meta http-equiv=\"refresh\" content=\"0; url=/\" />"
    return html

@app.route("/pingHosts/<ID>")
def pinghosts(ID):
    
    table = 'subnet'
    connection = sqlite3.connect("sweep.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    connection.commit()
      
    cursor = connection.cursor()
    cursor.execute("SELECT ID FROM subnet ORDER BY ID DESC LIMIT 1")
    last_id = cursor.fetchone()
    for lastID in last_id:
        print(lastID)
    cursor = connection.cursor()
    cursor.execute("SELECT ID,ip FROM " + table + " WHERE ID = '" + ID + "';")
    appTop = open("appTop.html","r")
    appBottom = open("appBottom.html","r")
    html = appTop.read()
    for row in cursor.fetchall():
        command = ['ping', '-n', '1', '-w', '1',  str(dict(row)['ip']) ]
        cursor.execute("SELECT ID,ip FROM " + table + ";")
        pingable = subprocess.call(command)
        cursor.execute("UPDATE subnet SET pingable = " + str(pingable) +  " WHERE ID = '" + str(dict(row)['ID']) + "';")
        connection.commit()

        perCent = int((int(ID) / int(lastID)) * 100)

        if str(pingable) == '0':
            html += "<div class=\"alert alert-success\" role=\"alert\">" + str(dict(row)['ip']) + "<div class=\"progress progress-bar-striped progress-bar-animated\"><div class=\"progress-bar\" role=\"progressbar\" style=\"width: " + str(perCent) + "%\">" +str(perCent) + "%</div></div>"
        else:
            html += "<div class=\"alert alert-danger\" role=\"alert\">" + str(dict(row)['ip']) + "<div class=\"progress progress-bar-striped progress-bar-animated\"><div class=\"progress-bar\" role=\"progressbar\" style=\"width: " + str(perCent) + "%\">" +str(perCent) + "%</div></div>"

        if str(int(ID)) != str(lastID):
            html += "<meta http-equiv=\"refresh\" content=\"0; url=/pingHosts/" + str(int(ID) + 1) + "\" />"
        else:
            html += "<meta http-equiv=\"refresh\" content=\"0; url=/\" />"

    html += appBottom.read()

    return html 