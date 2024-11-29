# Teamproject **Implementing a DNS server - Winter term 22/23**

## Group members

- Özdemir, Tamer, 5507971, tamer.oezdemir@student.uni-tuebingen.de
- Eminovic, Enes, 5410611, enes.eminovic@student.uni-tuebingen.de
- Wang, Zhi, 5575770, zhi.wang@student.uni-tuebingen.de
- Alnajar, Yaman, 5779680, yaman.alnajar@student.uni-tuebingen.de

## About

Our DNS server is able to reply to common DNS Queries. It can reply to these requested ressource records:

- A
- AAAA
- NS
- SOA
- MX
- TXT
- CNAME
- PTR

It also uses a database to store responses of incoming requests for a specified amount of time, so the same requests can be replied much faster.
Queries whose answers are not yet stored in the database are taken over by the stub resolver, which forwards the answer from another DNS server and stores it in the database.
Our DNS server has also an own zone file where IP addresses of specified domains are stored and getting parsed into the database.
For a more balanced output of IP addresses for the same domain a load balancing system was implemented, so everytime an IP address is getting delivered to the Client it will be deleted and inserted
back at the bottom of the database. This prevents high occupancy on one single IP address of a domain which has more IP addresses available.

For a better understanding of how the DNS Server works, we added a "Documentation.pdf" file.

## Installation

To run the DNS Server you have to install python3.

pyhton3 is available on this page: https://www.python.org/downloads/

After installing python3, use the command $ python3 -m pip install -r requirements.txt

to install all necessary packages and libaries.

Now the last thing left is to start the DNS server with $ python3 dns_server.py
We also added extra arguments to change some values in the Server:

- -ip     | IP address of the DNS server                  (Default: "127.0.0.1")
- -p      | Port of the DNS server                        (Default: 1234)
- -stip   | IP address of the stub resolver               (Default: "8.8.8.8")
- -stp    | Port of the stub resolver                     (Default: 53)
- -bs     | Maximum buffersize for EDNS query replies     (Default: 4096)
