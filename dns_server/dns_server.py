#!/usr/bin/env python3
import json
import logging
import argparse
import threading
import socket
import copy
import sqlite3
import time

import scapy
from scapy.all import (
    raw
)
from scapy.layers.dns import DNS, DNSRR, DNSQR, DNSRRSOA, DNSRRMX, DNSRROPT


class DNSServer():

    def __init__(self, port: int, ip: str, stip: str, stp: int, mbs: int):
        """
        DNS Server class to receive packets

        :param port: int
        :param ip: str
        """
        self.port = port
        self.ip = ip.replace("'", "")

        # Open a UDP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))

        self.ATYPE = 1
        self.AAAATYPE = 28
        self.SOATYPE = 6
        self.CNAMETYPE = 5
        self.NSTYPE = 2
        self.MXTYPE = 15
        self.PTRTYPE = 12
        self.TXTTYPE = 16
        self.OPTTYPE = 41

        self.stubresolverIP = stip.replace("'", "")
        self.stubresolverPort = stp
        self.BUFFERSIZE = mbs

        # Set up logging
        logging.basicConfig(level=logging.DEBUG)

    def store_stubresolver_cache(self, pkt, c):
        create_time = time.time()

        for x in range(pkt[DNS].ancount):

            # A, NS, AAAA resource record entries
            if pkt[DNS].an[x].type == self.ATYPE or \
                    pkt[DNS].an[x].type == self.NSTYPE or \
                    pkt[DNS].an[x].type == self.AAAATYPE:
                c.execute("INSERT INTO stubresolver_cacheRR VALUES (?,?,?,?,?,?,?)", (
                    pkt[DNS].an[x].rrname, pkt[DNS].an[x].type, pkt[DNS].an[x].rclass,
                    pkt[DNS].an[x].ttl, pkt[DNS].an[x].rdlen, pkt[DNS].an[x].rdata, create_time))

            # SOA resource record entries
            if pkt[DNS].an[x].type == self.SOATYPE:
                c.execute("INSERT INTO stubresolver_cacheSOA VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                    pkt[DNS].an[x].rrname, pkt[DNS].an[x].type, pkt[DNS].an[x].rclass,
                    pkt[DNS].an[x].ttl, pkt[DNS].an[x].rdlen, pkt[DNS].an[x].rname,
                    pkt[DNS].an[x].mname, pkt[DNS].an[x].serial, pkt[DNS].an[x].refresh,
                    pkt[DNS].an[x].retry, pkt[DNS].an[x].expire, pkt[DNS].an[x].minimum, create_time))

            # MX resource record entries
            if pkt[DNS].an[x].type == self.MXTYPE:
                c.execute("INSERT INTO stubresolver_cacheMX VALUES (?,?,?,?,?)", (
                    pkt[DNS].an[x].rrname, pkt[DNS].an[x].type, pkt[DNS].an[x].preference,
                    pkt[DNS].an[x].exchange, create_time))
            # TXT resource record entries
            if pkt[DNS].an[x].type == self.TXTTYPE:
                c.execute("INSERT INTO stubresolver_cacheRR VALUES (?,?,?,?,?,?,?)", (
                    pkt[DNS].an[x].rrname, pkt[DNS].an[x].type, pkt[DNS].an[x].rclass,
                    pkt[DNS].an[x].ttl, pkt[DNS].an[x].rdlen, pkt[DNS].an[x].rdata[0], create_time))
            # CNAME resource record entries
            if pkt[DNS].an[x].type == self.CNAMETYPE:
                c.execute("INSERT INTO stubresolver_cacheRR VALUES (?,?,?,?,?,?,?)", (
                    pkt[DNS].an[x].rrname, pkt[DNS].an[x].type, pkt[DNS].an[x].rclass,
                    pkt[DNS].an[x].ttl, pkt[DNS].an[x].rdlen, pkt[DNS].an[x].rdata, create_time))

        for x in range(pkt[DNS].nscount):

            # NS resource record entries
            if pkt[DNS].ns[x].type == self.NSTYPE:
                c.execute("INSERT INTO stubresolver_cacheRR VALUES (?,?,?,?,?,?,?)", (
                    pkt[DNS].ns[x].rrname, pkt[DNS].ns[x].type, pkt[DNS].ns[x].rclass,
                    pkt[DNS].ns[x].ttl, pkt[DNS].ns[x].rdlen, pkt[DNS].ns[x].rdata, create_time))

            # SOA resource record entries
            if pkt[DNS].ns[x].type == self.SOATYPE:
                c.execute("INSERT INTO stubresolver_cacheSOA VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                    pkt[DNS].ns[x].rrname, pkt[DNS].ns[x].type, pkt[DNS].ns[x].rclass,
                    pkt[DNS].ns[x].ttl, pkt[DNS].ns[x].rdlen, pkt[DNS].ns[x].rname,
                    pkt[DNS].ns[x].mname, pkt[DNS].ns[x].serial, pkt[DNS].ns[x].refresh,
                    pkt[DNS].ns[x].retry, pkt[DNS].ns[x].expire, pkt[DNS].ns[x].minimum, create_time))

        for x in range(pkt[DNS].arcount):

            if pkt[DNS].ar[x].type == self.NSTYPE or pkt[DNS].ar[x].type == self.AAAATYPE:
                c.execute("INSERT INTO stubresolver_cacheRR VALUES (?,?,?,?,?,?,?)", (
                    pkt[DNS].ar[x].rrname, pkt[DNS].ar[x].type, pkt[DNS].ar[x].rclass,
                    pkt[DNS].ar[x].ttl, pkt[DNS].ar[x].rdlen, pkt[DNS].ar[x].rdata, create_time))

    def zonefile_parser(self, connect, cur):
        cur.execute(
            "CREATE TABLE IF NOT EXISTS zonefileRR(rrname text, rtype integer, rclass integer, ttl integer, rdlength integer, rdata any)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS zonefileMX(rrname text, rtype integer, preference integer, exchange text)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS zonefileSOA(rrname text, rtype integer, rclass integer, ttl integer, rdlength integer, rname any, mname any, serial integer, refresh integer, retry integer, expire integer, minimum integer)")

        cur.execute("DELETE FROM zonefileMX")
        cur.execute("DELETE FROM zonefileSOA")
        cur.execute("DELETE FROM zonefileRR")

        file = open("zone.json")
        data = json.load(file)

        rrname = data['$origin']
        domainroot = data['@']
        ttl = data['$ttl']
        if 'SOA' in data.keys():
            for x in data['SOA']:
                cur.execute("INSERT INTO zonefileSOA VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
                    rrname, self.SOATYPE, 1,
                    ttl, None, x['rname'],
                    x['mname'], x['serial'], x['refresh'],
                    x['retry'], x['expire'], x['minimum']))
        if 'MX' in data.keys():
            for x in data['MX']:
                if x['name'] == domainroot:
                    cur.execute("INSERT INTO zonefileMX VALUES (?,?,?,?)", (
                        rrname, self.MXTYPE, x['priority'], x['value']
                    ))
                else:
                    cur.execute("INSERT INTO zonefileMX VALUES (?,?,?,?)", (
                        x['name'], self.MXTYPE, x['priority'], x['value']
                    ))
        if 'A' in data.keys():
            for x in data['A']:
                if x['name'] == domainroot:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        rrname, self.ATYPE, 1, x['ttl'], None, x['value']
                    ))
                else:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        x['name'], self.ATYPE, 1, x['ttl'], None, x['value']
                    ))
        if 'AAAA' in data.keys():
            for x in data['AAAA']:
                if x['name'] == domainroot:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        rrname, self.AAAATYPE, 1, x['ttl'], None, x['value']
                    ))
                else:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        x['name'], self.AAAATYPE, 1, x['ttl'], None, x['value']
                    ))
        if 'NS' in data.keys():
            for x in data['NS']:
                if x['name'] == domainroot:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        rrname, self.NSTYPE, 1, x['ttl'], None, x['host']
                    ))
                else:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        x['name'], self.NSTYPE, 1, x['ttl'], None, x['host']
                    ))
        if 'TXT' in data.keys():
            for x in data['TXT']:
                if x['name'] == domainroot:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        rrname, self.TXTTYPE, 1, None, None, x['value']
                    ))
                else:
                    cur.execute("INSERT INTO zonefileRR VALUES (?,?,?,?,?,?)", (
                        x['name'], self.TXTTYPE, 1, None, None, x['value']
                    ))

        connect.commit()

    def clear_stubresolver_cache(self, connect, cur):
        cur.execute("DELETE FROM stubresolver_cacheMX")
        cur.execute("DELETE FROM stubresolver_cacheSOA")
        cur.execute("DELETE FROM stubresolver_cacheRR")
        connect.commit()

    # When referencing the cache, insert the new time
    def current_time(self, c):
        create_time = time.time()

        c.execute("UPDATE stubresolver_cacheRR SET rtime=(?) - rtime ", ([create_time]))

        c.execute("UPDATE stubresolver_cacheSOA SET rtime=(?) - rtime ", ([create_time]))

        c.execute("UPDATE stubresolver_cacheMX SET rtime=(?) - rtime ", ([create_time]))

    def stub_resolver_cache(self, pkt, c, rname):

        # Clear every RR with the same qname in the packet where the TTL is over
        c.execute("DELETE FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.ttl < stubresolver_cacheRR.rtime")

        # Find corresponding information according to qname and type
        if pkt[DNS][DNSQR].qtype == self.SOATYPE:
            c.execute(
                "SELECT * FROM stubresolver_cacheSOA WHERE stubresolver_cacheSOA.rrname=?  AND stubresolver_cacheSOA.rtype=?",
                [rname, self.SOATYPE])
        elif pkt[DNS][DNSQR].qtype == self.MXTYPE:
            c.execute(
                "SELECT * FROM stubresolver_cacheMX WHERE stubresolver_cacheMX.rrname=? AND stubresolver_cacheMX.rtype=?",
                [rname, self.MXTYPE])
        elif pkt[DNS][DNSQR].qtype == self.ATYPE:
            c.execute(
                "INSERT INTO stubresolver_cacheRR SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.ATYPE])
            c.execute(
                "DELETE FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.ATYPE])
            c.execute(
                "SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MAX(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.ATYPE])
        elif pkt[DNS][DNSQR].qtype == self.AAAATYPE:
            c.execute(
                "INSERT INTO stubresolver_cacheRR SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.AAAATYPE])
            c.execute(
                "DELETE FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.AAAATYPE])
            c.execute(
                "SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MAX(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.AAAATYPE])
        elif pkt[DNS][DNSQR].qtype == self.NSTYPE:
            c.execute(
                "SELECT * FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?",
                [rname, self.NSTYPE])
        elif pkt[DNS][DNSQR].qtype == self.TXTTYPE:
            c.execute(
                "SELECT * FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?",
                [rname, self.TXTTYPE])
        elif pkt[DNS][DNSQR].qtype == self.CNAMETYPE:
            c.execute(
                "INSERT INTO stubresolver_cacheRR SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.CNAMETYPE])
            c.execute(
                "DELETE FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.CNAMETYPE])
            c.execute(
                "SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MAX(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.CNAMETYPE])
        elif pkt[DNS][DNSQR].qtype == self.PTRTYPE:
            c.execute(
                "INSERT INTO stubresolver_cacheRR SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.PTRTYPE])
            c.execute(
                "DELETE FROM stubresolver_cacheRR WHERE rowid = (SELECT MIN(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.PTRTYPE])
            c.execute(
                "SELECT * FROM stubresolver_cacheRR WHERE rowid = (SELECT MAX(rowid) FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?)",
                [rname, self.PTRTYPE])

        results = c.fetchall()

        # Check for the CNAME
        if (len(results) == 0):
            cursor = c.execute(
                "SELECT * FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?",
                [rname, self.CNAMETYPE])

            results1 = cursor.fetchall()

            if (len(results1) > 0):
                cursor = c.execute(
                    "SELECT * FROM stubresolver_cacheRR WHERE stubresolver_cacheRR.rrname=? AND stubresolver_cacheRR.rtype=?",
                    [results1[0][5], self.ATYPE])

            results = cursor.fetchall()
            results = results + results1

        return results

    def zone_file_cache(self, pkt, c, rname):

        rname = rname.decode('UTF-8')

        # Find corresponding information according to qname and type
        if pkt[DNS][DNSQR].qtype == self.SOATYPE:
            c.execute(
                "SELECT * FROM zonefileSOA WHERE zonefileSOA.rrname=? AND zonefileSOA.rtype=?",
                [rname, self.SOATYPE])
        elif pkt[DNS][DNSQR].qtype == self.MXTYPE:
            c.execute(
                "SELECT * FROM zonefileMX WHERE zonefileMX.rrname=? AND zonefileMX.rtype=?",
                [rname, self.MXTYPE])

        elif pkt[DNS][DNSQR].qtype == self.ATYPE:
            c.execute(
                "INSERT INTO zonefileRR SELECT * FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.ATYPE])
            c.execute(
                "DELETE FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.ATYPE])
            c.execute(
                "SELECT * FROM zonefileRR WHERE rowid = (SELECT MAX(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.ATYPE])
            # Move the entry to the bottom of the Database and select it
        elif pkt[DNS][DNSQR].qtype == self.AAAATYPE:
            c.execute(
                "INSERT INTO zonefileRR SELECT * FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.AAAATYPE])
            c.execute(
                "DELETE FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.AAAATYPE])
            c.execute(
                "SELECT * FROM zonefileRR WHERE rowid = (SELECT MAX(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.AAAATYPE])
            # Move the entry to the bottom of the Databaseand select it
        elif pkt[DNS][DNSQR].qtype == self.NSTYPE:
            c.execute(
                "SELECT * FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?",
                [rname, self.NSTYPE])
        elif pkt[DNS][DNSQR].qtype == self.TXTTYPE:
            c.execute(
                "SELECT * FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?",
                [rname, self.TXTTYPE])
        elif pkt[DNS][DNSQR].qtype == self.CNAMETYPE:
            c.execute(
                "INSERT INTO zonefileRR SELECT * FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.CNAMETYPE])
            c.execute(
                "DELETE FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.CNAMETYPE])
            c.execute(
                "SELECT * FROM zonefileRR WHERE rowid = (SELECT MAX(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.CNAMETYPE])
            # Move the entry to the bottom of the Database and select it
        elif pkt[DNS][DNSQR].qtype == self.PTRTYPE:
            c.execute(
                "INSERT INTO zonefileRR SELECT * FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.PTRTYPE])
            c.execute(
                "DELETE FROM zonefileRR WHERE rowid = (SELECT MIN(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.PTRTYPE])
            c.execute(
                "SELECT * FROM zonefileRR WHERE rowid = (SELECT MAX(rowid) FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?)",
                [rname, self.PTRTYPE])
            # Move the entry to the bottom of the Database and select it

        results = c.fetchall()

        # Check for the CNAME
        if (len(results) == 0):
            cursor = c.execute(
                "SELECT * FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?",
                [rname, self.CNAMETYPE])

            results1 = cursor.fetchall()

            if (len(results1) > 0):
                cursor = c.execute(
                    "SELECT * FROM zonefileRR WHERE zonefileRR.rrname=? AND zonefileRR.rtype=?",
                    [results1[0][5], self.ATYPE])

            results = cursor.fetchall()
            results = results + results1

        return results

    def assemble_response_pkt(self, results, data, ednsDesired):

        response_pkt = DNS(data)
        # Set the header flag to response
        response_pkt[DNS].qr = 1
        response_pkt[DNS].opcode = 0000
        response_pkt[DNS].aa = 0
        response_pkt[DNS].tc = 0
        response_pkt[DNS].rd = 1
        response_pkt[DNS].ra = 1
        response_pkt[DNS].z = 0
        response_pkt[DNS].ad = 1
        response_pkt[DNS].cd = 0
        response_pkt[DNS].rcode = 0000
        response_pkt[DNS].qdcount = 1
        response_pkt[DNS].ancount = len(results)
        response_pkt[DNS].nscount = 0
        response_pkt[DNS].arcount = 0
        response_pkt[DNS].qd = response_pkt[DNS][DNSQR]

        for x in range(len(results)):
            if results[x][1] == self.MXTYPE:
                response_pkt[DNS].an = DNSRRMX(rrname=results[x][0], type=results[x][1], preference=results[x][2],
                                               exchange=results[x][3])
                for x in range(len(results) - 1):
                    response_pkt[DNS].an = response_pkt[DNS].an / DNSRRMX(rrname=results[x][0], type=results[x][1],
                                                                          preference=results[x][2],
                                                                          exchange=results[x][3])
            elif results[x][1] == self.SOATYPE:
                response_pkt[DNS].an = DNSRRSOA(rrname=results[x][0], type=results[x][1], rclass=results[x][2],
                                                ttl=results[x][3], rdlen=results[x][4],
                                                mname=results[x][6],
                                                rname=results[x][5], serial=results[x][7], refresh=results[x][8],
                                                retry=results[x][9], expire=results[x][10], minimum=results[x][11])
                for x in range(len(results) - 1):
                    response_pkt[DNS].an = response_pkt[DNS].an / DNSRRSOA(rrname=results[x][0], type=results[x][1],
                                                                           rclass=results[x][2],
                                                                           ttl=results[x][3], rdlen=results[x][4],
                                                                           mname=results[x][6],
                                                                           rname=results[x][5], serial=results[x][7],
                                                                           refresh=results[x][8],
                                                                           retry=results[x][9], expire=results[x][10],
                                                                           minimum=results[x][11])
            else:
                response_pkt[DNS].an = DNSRR(rrname=results[x][0], type=results[x][1], rclass=results[x][2],
                                             ttl=results[x][3], rdlen=results[x][4],
                                             rdata=results[x][5])
                for x in range(len(results) - 1):
                    response_pkt[DNS].an = response_pkt[DNS].an / DNSRR(rrname=results[x][0], type=results[x][1],
                                                                        rclass=results[x][2],
                                                                        ttl=results[x][3], rdlen=results[x][4],
                                                                        rdata=results[x][5])
        # If we recognized a EDNS query we add the following parameters to our response, which contain the EDNS Pseudo Record and the extended arcount
        if ednsDesired == 1:
            response_pkt[DNS].arcount = + 2
            response_pkt[DNS].ar = response_pkt[DNS].ar / DNSRROPT(rrname=".", type=self.OPTTYPE,
                                                                   rclass=self.BUFFERSIZE, extrcode=0, version=0, z=0,
                                                                   rdlen=None)
        return response_pkt

    def stub_resolver(self, data, conn, c):

        pkt = DNS(data)

        rname = pkt[DNS][DNSQR].qname

        ednsDesired = 0
        if pkt[DNS].ar != None:
            for x in pkt[DNS].ar:
                if x.type == self.OPTTYPE:
                    ednsDesired = 1

        # Search in zone database first before asking your stub resolver.
        results1 = self.zone_file_cache(pkt, c, rname)
        if len(results1) > 0:
            logging.info(f"The query was served by zone")
            response_pkt = self.assemble_response_pkt(results1, data, ednsDesired)
            return response_pkt

        else:

            # Search in cache database first before forwarding.
            self.current_time(c)

            results = self.stub_resolver_cache(pkt, c, rname)

            # Data from cache must always be preferred.
            if len(results) > 0:
                logging.info(f"The query was served by cache")
                response_pkt = self.assemble_response_pkt(results, data, ednsDesired)

                return response_pkt

            else:
                # Build connection with the recursive resolver.
                logging.info(
                    "Connection to the Stubresolver: " + self.stubresolverIP + ":" + str(self.stubresolverPort))

                # Forward after search in zone and cache
                logging.info(f"The query was served by forwarding")

                stub_resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                stub_resolver_socket.sendto(data, (self.stubresolverIP, self.stubresolverPort))
                response_pkt = stub_resolver_socket.recv(512)
                stub_resolver_socket.settimeout(10)
                response_pkt = DNS(response_pkt)
                self.store_stubresolver_cache(response_pkt, c)
                conn.commit()

                return response_pkt

    def create_stubresolver_cache(self, cur):
        cur.execute(
            "CREATE TABLE IF NOT EXISTS stubresolver_cacheRR(rrname text, rtype integer, rclass integer, ttl integer, rdlength integer, rdata any, rtime integer)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS stubresolver_cacheMX(rrname text, rtype integer, preference integer, exchange text, rtime integer)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS stubresolver_cacheSOA(rrname text, rtype integer, rclass integer, ttl integer, rdlength integer, rname any, mname any, serial integer, refresh integer, retry integer, expire integer, minimum integer, rtime integer)")

    def loop(self):
        """
        Start the loop.

        The basic process is as follows:
        1. Receive packet payload on listening socket
        2. Parse it into a Scapy DNS Packet object
        3. Build a response Scapy DNS Packet according to the requested data
        4. Return the raw packet payload via the socketresp
        """
        logging.info(f"Server started and listening on {self.ip}:{self.port}")
        self.conn = sqlite3.connect("stubresolver_cache.db")
        self.c = self.conn.cursor()

        self.zonefile_parser(self.conn, self.c)
        # Creating the Cache of the Stubresolver
        self.create_stubresolver_cache(self.c)
        self.clear_stubresolver_cache(self.conn, self.c)

        while True:
            # Listen for incoming packets
            data, address = self.server_socket.recvfrom(self.BUFFERSIZE)

            # Assemble the response packet
            response_pkt = self.stub_resolver(data, self.conn, self.c)

            # Send the raw bytes back
            self.server_socket.sendto(raw(response_pkt), address)


def main():
    # Install requirements with python3 -m pip install -r requirements.txt
    # Start the server with python3 dns_server.py

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Receive packets")
    parser.add_argument('-ip', '--ip_address', default="127.0.0.1", action='store', type=ascii,
                        help="Address to listen on.")
    parser.add_argument('-p', '--port', default=1234, action='store', type=int, help="Port to listen on.")
    parser.add_argument('-stip', '--stub_resolverIP', default="8.8.8.8", action='store', type=ascii,
                        help="Address of the Stubresolver")
    parser.add_argument('-stp', '--stub_resolverPort', default=53, action='store', type=int,
                        help="Port of the Stubresolver")
    parser.add_argument('-bs', '--buffersize', default=4096, action='store', type=int,
                        help="Max buffersize")
    args = parser.parse_args()

    # Initiate the server
    receiver = DNSServer(args.port, args.ip_address, args.stub_resolverIP, args.stub_resolverPort, args.buffersize)

    # Start the listening loop
    t1 = threading.Thread(target=receiver.loop, args=(), daemon=True)
    t1.start()

    while True:
        pass


if __name__ == '__main__':
    main()
