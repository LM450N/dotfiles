import json
import logging
import time
import xml.etree.ElementTree as ET

from google.appengine.api import urlfetch

import webapp2
from google.appengine.ext import ndb


class HostabeeLoRaProxy(webapp2.RequestHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        # logging.warning(self.request.body)

        try:
            root = ET.fromstring(self.request.body)
            logging.warning(str(root))
            # self.response.write(root)
            payload = root.find(
                '{http://uri.actility.com/lora}payload_hex').text
            logging.warning('payload :' + str(payload))
            LrrLAT = root.find('{http://uri.actility.com/lora}LrrLAT').text
            LrrLON = root.find('{http://uri.actility.com/lora}LrrLON').text
            DevEUI = root.find('{http://uri.actility.com/lora}DevEUI').text
            code = payload[0:2].decode("hex")
        except Exception:
            logging.warning("XML data is empty or doesn't contain payload")
            return

        # A Station meteo Monceau le neuf, station la plus proche Crecy sur
        # Serre
        if code == "A":  # garden code
            formatJsonContextBroker(
                payload, "5694015311708160", "crecy-sur-serre")

        # B Saint Quentin Beehive
        elif code == 'B':  # temp, humi, battery
            formatJsonContextBroker(
                payload, "5720147234914304", "saint-quentin")

            # Monceau le neuf beehive 01
        elif code == 'C':  # temp, humi, vibration, battery
            # formatJsonContextBroker(payload,"5694015311708160","crecy-sur-serre")
            formatJsonContextBroker(
                payload, "5650665401483264", "chalons-en-champagne")


def formatJsonContextBroker(payload, hiveID, ville):
    # Temperature + humidity converted into int, need to divide by 100.0 to
    # convert into float
    temperature = int(payload[2:6], 16)
    humidity = int(payload[6:10], 16)
    temperature = temperature / 100.00
    humidity = humidity / 100.00
    battery = int(payload[10:14], 16)

    logging.warning('Float :' + str(temperature) + ',' +
                    str(humidity) + ',' + str(battery))

    # Get data from openweathermap
    json_weather = urlfetch.fetch(
        "http://api.openweathermap.org/data/2.5/find?\
        APPID=ff9a6269543a99490b5ad692b03725f9&q=%s,fr&units=metric" % (ville))
    data_weather = json.loads(json_weather.content)

    if data_weather['cod'] == "200":

        logging.warning(data_weather)

        # Contextbroker json template
        json_template_string = '{"type":"","id":"",\
            "insideTemperature":{"value":"","type":"Float"},\
            "insideHumidity":{"value":"","type":"Float"},\
            "batteryLevel":{"value":"","type":"Integer"},\
            "outsideTemperature":{"value":"","type":"Float"},\
            "outsideHumidity":{"value":"","type":"Float"},\
            "pressure":{"value":"","type":"Integer"},\
            "windSpeed":{"value":"","type":"Float"},\
            "windDeg":{"value":"","type":"Float"},\
            "weatherDescription":{"value":"","type":"String"},\
            "weatherIcon":{"value":"","type":"String"},\
            "rainDescription":{"value":"","type":"String"},\
            "rainValue":{"value":"","type":"Float"},\
            "timestamp":{"value":"","type":"String"}}'

        # Convert Json String to Json Python Object
        json_template_object = json.loads(json_template_string)

        # update type
        json_template_object['type'] = "Hive"

        # update id
        json_template_object['timestamp']['value'] = str(long(time.time()))
        # update id
        json_template_object['id'] = hiveID

        # update temp Inside
        json_template_object['insideTemperature']['value'] = temperature

        # update Hum Inside
        json_template_object['insideHumidity']['value'] = humidity

        # battery level
        json_template_object['batteryLevel']['value'] = battery

        # update temp Outside
        # json_template_object['contextElements'][0]['attributes'][1]['value']=
        # data_weather['list'][0]['main']['temp']
        json_template_object['outsideTemperature'][
            'value'] = data_weather['list'][0]['main']['temp']

        # update humidity Outside
        json_template_object['outsideHumidity'][
            'value'] = data_weather['list'][0]['main']['humidity']

        # pressure
        json_template_object['pressure']['value'] = int(
            data_weather['list'][0]['main']['pressure'])

        # wind speed and deg
        json_template_object['windSpeed'][
            'value'] = data_weather['list'][0]['wind']['speed']
        json_template_object['windDeg'][
            'value'] = data_weather['list'][0]['wind']['deg']

        # weather (description, icon)
        json_template_object['weatherDescription'][
            'value'] = data_weather['list'][0]['weather'][0]['description']
        json_template_object['weatherIcon'][
            'value'] = data_weather['list'][0]['weather'][0]['icon']

        # .warning("Value : " + data_weather['list'][0]['weather'][0])
        try:
            rain_key = data_weather['list'][0]['rain'].keys()[0]
            json_template_object['rainDescription']['value'] = rain_key
            json_template_object['rainValue'][
                'value'] = data_weather['list'][0]['rain'][rain_key]
        except Exception:
            json_template_object['rainDescription']['value'] = ''
            json_template_object['rainValue']['value'] = 0

        data = json.dumps(json_template_object)
        # logging.warning(data)
        urlfetch.fetch('http://dev-dot-hostabee-proxy.appspot.com', data,
                       headers={'Content-Type': 'application/json'},
                       method='POST')

    else:
        logging.warning("Error openweathermap Call from %s at %s" %
                        (hiveID, str(long(time.time()))))

    return

app = webapp2.WSGIApplication([
    ('/hostabee-lora-proxy', HostabeeLoRaProxy)
], debug=True)
