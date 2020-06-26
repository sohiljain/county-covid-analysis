import unittest
import json
import requests


class MyTestCase(unittest.TestCase):

    def one_to_one_mapping(self):
        """
        We find an exact match to county mapping and zip belongs to only one county. Observe that esitmated cases is
        less than cases in counties because it is divided by number of zipcodes in the county to estimte zipcode level data
        """
        input = 'http://127.0.0.1:5002/covid/90066?start=2020-06-21&end=2020-06-24'
        output = requests.get(input).text
        output = json.loads(output)
        expected = json.loads("""
                {"covid_analysis":[{"counties":[{"cases":83414,"fips":"06037","rate":0.83}],"dt":"2020-06-21","estimated_cases":167.83501006036218,"fips":"06037","rate":0.83},{"counties":[{"cases":86017,"fips":"06037","rate":0.85}],"dt":"2020-06-22","estimated_cases":173.07243460764587,"fips":"06037","rate":0.85},{"counties":[],"dt":"2020-06-23","estimated_cases":0,"fips":"06037","rate":0}],"zip_code":"90066"}
                """)

        self.assertEqual(sorted(output.items()) == sorted(expected.items()), True)

    def test_unsuccessfull_county_match(self):
        """
        We find no match to county mapping and cannot find the populatin and therefore rate is null. Zip belongs to only one county. Observe that esitmated cases is
        less than cases in counties because it is divided by number of zipcodes in the county to estimte zipcode level data
        """

        input = 'http://127.0.0.1:5002/covid/63132?start=2020-06-21&end=2020-06-24'
        output = requests.get(input).text
        output = json.loads(output)
        expected = json.loads('''
        {"covid_analysis":[{"counties":[{"cases":5850,"fips":"29189","rate":null}],"dt":"2020-06-21","estimated_cases":104.46428571428571,"rate":0},{"counties":[{"cases":5878,"fips":"29189","rate":null}],"dt":"2020-06-22","estimated_cases":104.96428571428571,"rate":0},{"counties":[],"dt":"2020-06-23","estimated_cases":0,"rate":0}],"zip_code":"63132"}
        ''')

        print(output)
        self.assertEqual(sorted(output.items()) == sorted(expected.items()), True)

        # self.assertEqual(sorted(output) == sorted(json_object.items()), True)

    def no_mapping(self):
        """
        When we find no mapping, estimated cases and rate values are null
        :return:
        """
        input = 'http://127.0.0.1:5002/covid/00711?start=2020-06-21&end=2020-06-24'
        output = requests.get(input).text
        output = json.loads(output)
        expected = json.loads('''
        {"covid_analysis":[{"counties":[],"dt":"2020-06-21","estimated_cases":null,"rate":null},{"counties":[],"dt":"2020-06-22","estimated_cases":null,"rate":null},{"counties":[],"dt":"2020-06-23","estimated_cases":null,"rate":null}],"zip_code":"00711"}
        ''')

        self.assertEqual(sorted(output.items()) == sorted(expected.items()), True)

    def multiple_counties_zip(self):
        """
        When we find a zip lies in multiple counties, we multiply and sum over the tot_ration to get estimated counts
        :return:
        """

        input = 'http://127.0.0.1:5002/covid/90630?start=2020-06-01&end=2020-06-24'
        output = requests.get(input).text
        output = json.loads(output)
        expected = json.loads('''
        {"covid_analysis":[{"counties":[{"cases":10422,"fips":"06059","rate":0.32},{"cases":83414,"fips":"06037","rate":0.83}],"dt":"2020-06-21","estimated_cases":71.25017478000723,"rate":0.32185305775764445},{"counties":[{"cases":10595,"fips":"06059","rate":0.33},{"cases":86017,"fips":"06037","rate":0.85}],"dt":"2020-06-22","estimated_cases":72.44179933363506,"rate":0.3318893922234806},{"counties":[],"dt":"2020-06-23","estimated_cases":0,"rate":0}],"zip_code":"90630"}
        ''')

        self.assertEqual(sorted(output.items()) == sorted(expected.items()), True)


if __name__ == '__main__':
    unittest.main()
