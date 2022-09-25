import mysql.connector
import netaddr
import time
import os

# Connting to MySQL database. Please use sepcific user and password here. This is me being lazy. DO NOT USE ROOT EMPTY PASSWORDS. DO NOT USE ROOT USER FOR AN APPLICATION!
conn = mysql.connector.connect(user='root', password='', host='localhost', database='pi')
cursor = conn.cursor()
# Making sure our tables has been created.
try:
    cursor.execute("CREATE TABLE IF NOT EXISTS leases ( id VARCHAR(20) NOT NULL , leasetime TIMESTAMP NOT NULL DEFAULT now() , ip INT(10) NOT NULL , host VARCHAR(50) NOT NULL , mac VARCHAR(17) NOT NULL, state CHAR(1) NOT NULL , PRIMARY KEY (id))")
except:
    print 'error creating table'
    sys.exit()
    cursor.close()

t = time.time()

while True:
    try:
        if time.time() - t > 5:
            t = time.time()
            try:
                cursor = conn.cursor()
                try:
                    with open('/var/lib/misc/dnsmasq.leases') as f:
                        leasesContent = f.read().splitlines()
                    for content in leasesContent:
                        content = content.split(' ')
                        response = os.system("ping -c 1 " + content[2])
                        print response;
                        if response == 0:
                            try:
                                cursor.execute("insert into leases (id, leaseTime, ip, host, mac, leaseStatus) values ('{0}', now(), '{1}', '{2}', '{3}', 'u') ON DUPLICATE KEY UPDATE leaseTime = now(), ip = '{1}', leaseStatus = 'u'".format(content[4], int(netaddr.IPAddress(content[2])), content[3], content[1]))
                                conn.commit()
                            except:
                                print 'error inserting MySQL row'
                        else:
                            try:
                                cursor.execute("insert into leases (id, leaseTime, ip, host, mac, leaseStatus) values ('{0}', now(), '{1}', '{2}', '{3}', 'd') ON DUPLICATE KEY UPDATE leaseTime = now(), ip = '{1}', leaseStatus = 'd'".format(content[4], int(netaddr.IPAddress(content[2])), content[3], content[1]))
                                conn.commit()
                            except:
                                print 'error inserting MySQL row'
                except:
                    print 'error deleting table leases'
            except:
                print 'cannot open cursor to MySQL database...'

    except KeyboardInterrupt:
        conn.close()
        break
        sys.exit()