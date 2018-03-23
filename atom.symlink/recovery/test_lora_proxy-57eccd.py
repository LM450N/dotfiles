#!/usr/bin/env python
# coding=utf-8

from lora_proxy.lora_proxy.core import LoRaProxy


class TestLoraProxy:

    def test_hexa_to_dict(self):
        # TODO: Use a mock for the expected hive.
        hexa = "410D611644002D"
        d = lora_proxy.hexa_to_dict(hexa)
        assert isinstance(d, dict)
        assert d.get('type') == 'A'
        assert d.get('temperature') == 34.25
        assert d.get('humidity') == 57
        assert d.get('batteryLevel') == 45

    def test_get_weather(self, city):
        # TODO: Use a mock for the expected weather.
        weather = lora_proxy.get_weather(city)
        assert isinstance(weather, dict)
        assert weather.get('outsideTemperature') == 21.5
        assert weather.get('outsideHumidity') == 55
        assert weather.get('windDeg') == 180
        assert weather.get('windSpeed') == 2.3
        assert weather.get('rainDescription') == "3h"
        assert weather.get('rainValue') == 1.2
        assert weather.get('weatherDescription') == "broken clouds"
        assert weather.get('weatherIcon') == "04d"
        assert weather.get('pressure') == 1006

    def test_format_to_ngsi2(self, hive, weather):
        # TODO: Use hive and weather mocks to feed the method.
        data_ngsi2_format = lora_proxy.format_to_ngsi2(hive, weather)
        # TODO: Use mock of NGSI2 format to check the return.
