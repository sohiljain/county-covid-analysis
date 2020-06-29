from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask import jsonify
import requests, json
import logging
import datetime

db_connect = create_engine('sqlite:///covid_analysis.db')
app = Flask(__name__)
api = Api(app)


def get_county(zip: str):
    """
    Method to return a list of [fips, tot_ratio] given zip_code
    :param zip: str
    :return: [fips, tot_ratio]
    """

    url = f"https://www.huduser.gov/hudapi/public/usps?type=2&query={zip}"
    response = requests.get(url, headers={
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU0ZmMyZDcxZjllMTAwMTI4ZDdiYjRiYjY4NjRmNzI5MjEwOGYwMGU3MTA1NjUwM2YwMzQyNzBhNDY5MTZjNzljYzhkNjYwMjAzMzIzYTZlIn0.eyJhdWQiOiI2IiwianRpIjoiZTRmYzJkNzFmOWUxMDAxMjhkN2JiNGJiNjg2NGY3MjkyMTA4ZjAwZTcxMDU2NTAzZjAzNDI3MGE0NjkxNmM3OWNjOGQ2NjAyMDMzMjNhNmUiLCJpYXQiOjE1OTMwNTgxNTUsIm5iZiI6MTU5MzA1ODE1NSwiZXhwIjoxOTA4NTkwOTU1LCJzdWIiOiI2MDczIiwic2NvcGVzIjpbXX0.GHD3rstCi4_g0zluSfddqapUsfHZ9zkV4TxXt-j--tS6hwYxpcM3slFIScwvmdAtXZLh_WP2iwIEE1_lF68U4w'})
    try:
        output_text = response.text
        df = json.loads(output_text)
        results = df.get('data', '').get('results', '')
        geoids = [[result.get('geoid'), result.get('tot_ratio')] for result in results]
        return geoids
    except requests.exceptions.Timeout as e:
        raise SystemExit(e)
    except requests.exceptions.TooManyRedirects as e:
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except ValueError as e:  # includes simplejson.decoder.JSONDecodeError
        logging.error(f'Decoding JSON has failed for {output_text}. Error {e}')
        return []
    except AttributeError as e:  # includes simplejson.decoder.JSONDecodeError
        logging.error(f'Decoding JSON has failed for {output_text}. Error {e}')
        return []


def get_zip_cnt(fips: str):
    """
    Method to return count of zip_codes in a fips code
    :param fips: str
    :return: return count of zip_codes in a fips code
    """
    url = f"https://www.huduser.gov/hudapi/public/usps?type=7&query={fips}"
    response = requests.get(url, headers={
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImU0ZmMyZDcxZjllMTAwMTI4ZDdiYjRiYjY4NjRmNzI5MjEwOGYwMGU3MTA1NjUwM2YwMzQyNzBhNDY5MTZjNzljYzhkNjYwMjAzMzIzYTZlIn0.eyJhdWQiOiI2IiwianRpIjoiZTRmYzJkNzFmOWUxMDAxMjhkN2JiNGJiNjg2NGY3MjkyMTA4ZjAwZTcxMDU2NTAzZjAzNDI3MGE0NjkxNmM3OWNjOGQ2NjAyMDMzMjNhNmUiLCJpYXQiOjE1OTMwNTgxNTUsIm5iZiI6MTU5MzA1ODE1NSwiZXhwIjoxOTA4NTkwOTU1LCJzdWIiOiI2MDczIiwic2NvcGVzIjpbXX0.GHD3rstCi4_g0zluSfddqapUsfHZ9zkV4TxXt-j--tS6hwYxpcM3slFIScwvmdAtXZLh_WP2iwIEE1_lF68U4w'})
    try:
        output_text = response.text
        df = json.loads(output_text)
        results = df.get('data', '').get('results', '')
        geoids = [[result.get('geoid'), result.get('tot_ratio')] for result in results]
        return len(geoids)
    except requests.exceptions.Timeout as e:
        raise SystemExit(e)
    except requests.exceptions.TooManyRedirects as e:
        raise SystemExit(e)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except ValueError as e:  # includes simplejson.decoder.JSONDecodeError
        logging.error(f'Decoding JSON has failed for {output_text}. Error {e}')
        return 0
    except AttributeError as e:  # includes simplejson.decoder.JSONDecodeError
        logging.error(f'Decoding JSON has failed for {output_text}. Error {e}')
        return 0


class Covid(Resource):
    def get(self):
        conn = db_connect.connect()  # connect to database
        query = conn.execute("select * from covid_1")  # This line performs query and returns json result
        return {'covid_analysis': [i[0] for i in query.cursor.fetchall()]}  # Fetches first column that is Employee ID


class Covid_Rate(Resource):

    def get(self, zip_code):
        start = request.args.get('start')
        end = request.args.get('end')
        conn = db_connect.connect()
        geoids = get_county(zip_code)  # Get fips code py using zip-county crosswalk
        dates = []
        date_time_obj = datetime.datetime.strptime(start, '%Y-%m-%d')
        end = datetime.datetime.strptime(end, '%Y-%m-%d')
        while date_time_obj < end:
            estimated_cases = 0 if len(geoids) > 0 else None
            rate = 0 if len(geoids) > 0 else None
            counties = []
            for geoid in geoids:
                fips = geoid[0]
                tot_ratio = geoid[1]
                query = conn.execute(f"""select fips, cases, rate from covid 
                                     where fips='{fips}' and dt='{date_time_obj.strftime("%Y-%m-%d")}'""")
                result = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
                print(result)
                if len(result) == 0:
                    estimated_cases = None
                    rate = None
                    continue
                counties.append(result[0])

                # If a zip lies in multiple counties, we multiply and sum over the tot_ration to get estimated counts
                # Divide total cases in county by total zipcodes in the county to estimate cases in zipcode
                estimated_cases += float(result[0]['cases'] * tot_ratio) / get_zip_cnt(fips)
                rate += result[0].get('rate', 0) * tot_ratio if result[0].get('rate', 0) is not None else 0

            zipcode = {'estimated_cases': estimated_cases, 'rate': rate, 'dt': date_time_obj.strftime("%Y-%m-%d"),
                       'counties': counties}
            date_time_obj += datetime.timedelta(days=1)
            dates.append(zipcode)

        data = {'zip_code': zip_code, 'covid_analysis': dates}
        return jsonify(data)

api.add_resource(Covid_Rate, '/covid/<zip_code>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002')
