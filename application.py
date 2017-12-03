import os
import re
from flask import Flask, jsonify, render_template, request

from cs50 import SQL
import sqlite3
import websiteconfig

import json
import collections

#AWS DB test
import pandas as pd
import pymysql
import pymysql.cursors

# Configure app
application = app = Flask(__name__)
app.api_key = websiteconfig.API_KEY

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

#AWS DB test
host="sashatest.clyaav4frtez.us-west-2.rds.amazonaws.com"
port=3306
dbname="sashatest"
user="sasharamani"
password="Freedom55!?"

conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)

# pd.read_sql('select count(distinct origin) AS "Distinct Origins" from flights;', con=conn)
# print (pd.read_sql('select * from airportdata Limit 1;', con=conn))

# export API_KEY=AIzaSyB_5erBSxNPAMdDOtl0PucoNDuexof2i0U
# https://developers.google.com/maps/web/

# run the app.
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Render map"""
    #if not os.environ.get("API_KEY"):
    #    raise RuntimeError("API_KEY not set")
    #return render_template("index.html", key=os.environ.get("API_KEY"))
    return render_template("index.html", key=app.api_key)


@app.route("/articles")
def articles():
    """Look up articles for geo"""
    if not request.args.get("geo"):
        raise RuntimeError("Geo not found")

    return jsonify(lookup(request.args.get("geo")))


@app.route("/search")
def search():
    """Search for places that match query"""
    if request.args.get("q"):
        if len(request.args.get("q")) >= 3:  # Apply a minimum length of string before we start searching
            q = request.args.get("q") + '%'

            conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)

            #print ("trying query: " + q)
            query = "SELECT * FROM airportdata WHERE Iata_Code LIKE %(the_value)s OR Serves LIKE %(the_value)s or Airport_Name Like %(the_value)s ORDER BY Number_of_Routes DESC;"

            try:
                cursor = conn.cursor()
                cursor.execute(query, {'the_value': q})
            except:
                conn.rollback()
                raise
            else:
                conn.commit()


                rows = []
                for row in cursor:
                    thedict = {}
                    thedict['id'] = row[0]
                    thedict['IATA_Code'] = row[1]
                    thedict['ICAO_Code'] = row[2]
                    thedict['Other_Code'] = row[3]
                    thedict['Active'] = 1
                    thedict['Cleaned_Wiki_URL'] = row[5]
                    thedict['Airport_Name'] = row[6]
                    thedict['Serves'] = row[7]
                    thedict['Location'] = row[8]
                    thedict['Country_ID'] = row[9]
                    thedict['State_ID'] = row[10]
                    thedict['Latitude_Val'] = row[11]
                    thedict['Longitude_Val'] = row[12]
                    thedict['Number_of_Routes'] = row[13]
                    thedict['Adj_Airport_Name'] = row[14]
                    thedict['Adj_Serves'] = row[15]
                    thedict['Adj_Location'] = row[16]
                    thedict['Macro_Country'] = row[17]
                    thedict['Broad_3_Continent_Zones'] = row[18]
                    thedict['SR_NA_Zone'] = row[19]
                    thedict['SR_Zone'] = row[20]

                    rows.append(thedict)

                #print(rows)

                json_test = json.dumps(rows)
                #print(json_test)

            conn.close()

            return json_test

@app.route("/update")
def update():
    """Find up to 10 places within view"""

    # Ensure parameters are present
    if not request.args.get("sw"):
        raise RuntimeError("missing sw")
    if not request.args.get("ne"):
        raise RuntimeError("missing ne")

    # Ensure parameters are in lat,lng format
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("sw")):
        raise RuntimeError("invalid sw")
    if not re.search("^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$", request.args.get("ne")):
        raise RuntimeError("invalid ne")

    # Explode southwest corner into two variables
    sw_lat, sw_lng = map(float, request.args.get("sw").split(","))

    # Explode northeast corner into two variables
    ne_lat, ne_lng = map(float, request.args.get("ne").split(","))

    # Find 10 cities within view, sorted by most routes (proxy for airport size)

    conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)

    query = "SELECT * FROM airportdata WHERE %(sw_lat)s <= Latitude_Val AND Latitude_Val <= %(ne_lat)s AND (%(sw_lng)s <= Longitude_Val AND Longitude_Val <= %(ne_lng)s) ORDER BY Number_of_Routes DESC LIMIT 10;"
    #print ("trying query: " + query)

    try:
        cursor = conn.cursor()
        cursor.execute(query, {'sw_lat': float(sw_lat), 'ne_lat': float(ne_lat), 'sw_lng': float(sw_lng), 'ne_lng': float(ne_lng)})
    except:
        conn.rollback()
        raise
    else:
        conn.commit()


        rows = []
        for row in cursor:
            thedict = {}
            thedict['id'] = row[0]
            thedict['IATA_Code'] = row[1]
            thedict['ICAO_Code'] = row[2]
            thedict['Other_Code'] = row[3]
            thedict['Active'] = 1
            thedict['Cleaned_Wiki_URL'] = row[5]
            thedict['Airport_Name'] = row[6]
            thedict['Serves'] = row[7]
            thedict['Location'] = row[8]
            thedict['Country_ID'] = row[9]
            thedict['State_ID'] = row[10]
            thedict['Latitude_Val'] = row[11]
            thedict['Longitude_Val'] = row[12]
            thedict['Number_of_Routes'] = row[13]
            thedict['Adj_Airport_Name'] = row[14]
            thedict['Adj_Serves'] = row[15]
            thedict['Adj_Location'] = row[16]
            thedict['Macro_Country'] = row[17]
            thedict['Broad_3_Continent_Zones'] = row[18]
            thedict['SR_NA_Zone'] = row[19]
            thedict['SR_Zone'] = row[20]

            rows.append(thedict)

        #print(rows)

        json_test = json.dumps(rows)
        #print(json_test)

    conn.close()

    return json_test


@app.route("/routesearch")
def routesearch():
    """Search for non-stop flights from a certain airport"""

    print('started route search')
    if request.args.get("id"):

        airportid = request.args.get("id")
        conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)

        print ("trying airport id: " + airportid)
        query = "select distinct airport_id1, airport_id2, iata_code, airport_name, serves, location, latitude_val, Longitude_Val  from routematrix inner join airportdata on routematrix.airport_id2 = airportdata.id inner join airlinemap on routematrix.airline_id = airlinemap.id where airport_id1 =  %(sourceairportid)s"

        if (request.args.get("star") == 'true'):
            query = query + " and (airlinemap.alliance = 'Star'"

            if (request.args.get("ow") == 'true'):
                query = query + " or airlinemap.alliance = 'OneWorld'"

            if (request.args.get("sky") == 'true'):
                query = query + " or airlinemap.alliance = 'Skyteam'"

            query = query + ')'
        else:

            if (request.args.get("ow") == 'true'):
                query = query + " and (airlinemap.alliance = 'OneWorld'"

                if (request.args.get("sky") == 'true'):
                    query = query + " or airlinemap.alliance = 'Skyteam'"

                query = query + ')'
            else:

                if (request.args.get("sky") == 'true'):
                    query = query + " and (airlinemap.alliance = 'Skyteam')"

        query = query + ';'
        print(query)

        try:
            cursor = conn.cursor()
            cursor.execute(query, {'sourceairportid': airportid})
        except:
            conn.rollback()
            raise
        else:
            conn.commit()

            rows = []
            for row in cursor:
                thedict = {}
                thedict['originairportid'] = row[0]
                thedict['connairportid'] = row[1]
                thedict['connairportiata'] = row[2]
                thedict['airport_name'] = row[3]
                thedict['serves'] = row[4]
                thedict['location'] = row[5]
                thedict['latitude_val'] = row[6]
                thedict['longitude_val'] = row[7]

                rows.append(thedict)

            #print(rows)

            json_test = json.dumps(rows)
            #print(json_test)

        conn.close()

        return json_test



@app.route("/connectingairlines")
def connectingairlines():
    """Get airlines connecting together two airports"""

    print('started airline search')
    if request.args.get("airport1"):

        airportid1 = request.args.get("airport1")
        airportid2 = request.args.get("airport2")
        conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)

        query = "SELECT Airport_ID1, Airport_ID2, Airline_ID, airline_brand, iata_designator FROM routematrix inner join airlinemap on routematrix.Airline_ID = airlinemap.id where (routematrix.Airport_ID1 = %(airportid1)s) and (routematrix.Airport_ID2 = %(airportid2)s) and airlinemap.CargoOrPassenger != 'Cargo'"

        if (request.args.get("star") == 'true'):
            query = query + " and (airlinemap.alliance = 'Star'"

            if (request.args.get("ow") == 'true'):
                query = query + " or airlinemap.alliance = 'OneWorld'"

            if (request.args.get("sky") == 'true'):
                query = query + " or airlinemap.alliance = 'Skyteam'"

            query = query + ')'
        else:

            if (request.args.get("ow") == 'true'):
                query = query + " and (airlinemap.alliance = 'OneWorld'"

                if (request.args.get("sky") == 'true'):
                    query = query + " or airlinemap.alliance = 'Skyteam'"

                query = query + ')'
            else:

                if (request.args.get("sky") == 'true'):
                    query = query + " and (airlinemap.alliance = 'Skyteam')"

        query = query + ';'
        print(query)

        try:
            cursor = conn.cursor()
            cursor.execute(query, {'airportid1': airportid1, 'airportid2': airportid2})
        except:
            conn.rollback()
            raise
        else:
            conn.commit()

            rows = []
            for row in cursor:
                thedict = {}
                thedict['airportid1'] = row[0]
                thedict['airportid2'] = row[1]
                thedict['airlineid'] = row[2]
                thedict['airline_brand'] = row[3]
                thedict['iata_designator'] = row[4]

                rows.append(thedict)

            #print(rows)

            json_test = json.dumps(rows)
            #print(json_test)

        conn.close()

        return json_test



@app.route("/calcmiles")
def calcmiles():
    """Calculate the number of frequent flyer miles to fly between two airports (on a given airline)"""

    #print('started mileagecalc')

    airportid1 = request.args.get("airportid1")
    airportid2 = request.args.get("airportid2")
    airlineid = request.args.get("airlineid")
    directionality = request.args.get("directionality")
    travelclass = request.args.get("travelclass")
    traveldate = request.args.get("traveldate")

    mileageprograms = [1, 2, 3, 4, 5] #, 7, 8, 9, 10, 11, 12, 16, 19, 23, 48]
    programnames = {1: 'American AAdvantage', 2: 'United MileagePlus', 3: 'Lufthansa Miles and More', 4: 'British Airways Avios', 5: 'Air Canada Aeroplan'}


    if (directionality == 'One-way'):
        shortdirectionality = 'ow'
    elif (directionality == 'Round-trip'):
        shortdirectionality = 'rt'

    if (travelclass == 'Economy Class'):
        shorttravelclass = 'Economy'
    elif (travelclass == 'Business Class'):
        shorttravelclass = 'Business'
    elif (travelclass == 'First Class'):
        shorttravelclass = 'First'

    rows = []

    for mileageprogram in mileageprograms:
        conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)

        query = "select fn_calcMiles(%(program)s, %(airportid1)s, 0, 0, %(airportid2)s, %(airlineid)s, 0, 0, fnCalcDistanceBetweenAirports(%(airportid1)s, %(airportid2)s), 0, 0, %(traveldate)s, %(travelclass)s, %(direction)s, 1);"
        #print(query)

        if verifyairlineprogrammatch(mileageprogram, airlineid) == 1:
            try:
                cursor = conn.cursor()
                #cursor.execute(query, {'program': 2, 'airportid1': airportid1, 'airportid2': airportid2, 'airlineid': airlineid, 'traveldate': '2018-01-01', 'travelclass': 'Economy', 'direction': 'ow'})
                cursor.execute(query, {'program': mileageprogram, 'airportid1': airportid1, 'airportid2': airportid2, 'airlineid': airlineid, 'traveldate': traveldate, 'travelclass': shorttravelclass, 'direction': shortdirectionality})
            except:
                conn.rollback()
                raise
            else:
                conn.commit()

                thedict = {}
                for row in cursor:
                    thedict['programname'] = programnames[mileageprogram]
                    thedict['miles'] = numberformat(int(row[0]))

                rows.append(thedict)
                conn.close()

        else:
            thedict = {}
            thedict['programname'] = programnames[mileageprogram]
            thedict['miles'] = 'n/a'
            rows.append(thedict)


    airportstring = getairportdetails(airportid1) + ' to ' + getairportdetails(airportid2)
    airlinestring = 'Traveling on ' + getairlinedetails(airlineid) + ', ' + directionality + ' in ' + travelclass + ', departing ' + traveldate

    return render_template("calcmiles.html", airportstring=airportstring, airlinestring = airlinestring, programs=rows)


def verifyairlineprogrammatch(programid, airlineid):
    """Confirm that a given airline is part of a specific program"""

    conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)
    query = "select count(*) from partnerships where (program_id = %(programid)s) and (airline_id = %(airlineid)s);"

    matchval = 0

    try:
        cursor = conn.cursor()
        cursor.execute(query, {'programid': programid, 'airlineid': airlineid})
    except:
        conn.rollback()
        raise
    else:
        conn.commit()

        for row in cursor:
            matchval = row[0]

        conn.close()

    return matchval






def getairportdetails(airportid):
    """Get Airport Details"""
    outputstring = ""

    conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)
    query = "select id, iata_code, airport_name, serves from airportdata where id=%(airportid)s;"

    try:
        cursor = conn.cursor()
        cursor.execute(query, {'airportid': airportid})
    except:
        conn.rollback()
        raise
    else:
        conn.commit()

        for row in cursor:
            outputstring = row[1] + ' - ' + row[3] + ' (' + row[2] + ')'

        conn.close()

    return outputstring



def getairlinedetails(airlineid):
    """Get Airline Details"""
    outputstring = ""

    conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, autocommit=False)
    query = "select id, airline_brand, iata_designator from airlinemap where id=%(airlineid)s;"

    try:
        cursor = conn.cursor()
        cursor.execute(query, {'airlineid': airlineid})
    except:
        conn.rollback()
        raise
    else:
        conn.commit()

        for row in cursor:
            outputstring = row[1] + ' (' + row[2] + ')'

        conn.close()

    return outputstring

def numberformat(value):
    """Formats value as comma-separated"""
    return f"{value:,.0f}"