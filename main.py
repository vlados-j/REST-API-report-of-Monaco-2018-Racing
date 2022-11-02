from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import json
import xml.etree.ElementTree as ET
from application_vlados import processing_data, build_report


app = Flask(__name__)
api = Api(app)


class Report(Resource):
    def get(self):
        args = request.args
        structured_info = processing_data('files/start.log', 'files/end.log',
                                          'files/abbreviations.txt')
        prepared_info_for_report = info_for_output(structured_info, args.get("order"))
        if args.get("format") == 'xml':
            return generate_xml_data(prepared_info_for_report)
        else:
            return generate_json_data(prepared_info_for_report)


class Drivers(Resource):
    def get(self):
        args = request.args
        structured_info = processing_data('files/start.log', 'files/end.log',
                                          'files/abbreviations.txt')
        if args.get("abbreviation"):
            for racer in structured_info.values():
                if racer.abbreviation == args.get("abbreviation"):
                    if args.get("format") == 'xml':
                        root = ET.Element('racer')

                        drivers_name = ET.SubElement(root, 'name')
                        drivers_name.text = racer.name

                        drivers_team = ET.SubElement(root, 'team')
                        drivers_team.text = racer.team

                        drivers_lap_time = ET.SubElement(root, 'lap_time')
                        drivers_lap_time.text = racer.lap_time_str
                        return ET.tostring(root).decode()
                    else:
                        info_about_racer = {'name': racer.name,
                                            'team': racer.team,
                                            'lap_time': racer.lap_time_str}
                        return jsonify(info_about_racer)
        prepared_info_for_report = info_for_output(structured_info, args.get("order"))
        if args.get("format") == 'xml':
            return generate_xml_data(prepared_info_for_report)
        else:
            return generate_json_data(prepared_info_for_report)


def info_for_output(structured_info, ordering):
    prepared_info_for_report = build_report(structured_info, ordering)
    number_of_valid_racers = len([None for racer in prepared_info_for_report if racer.lap_time])
    if ordering == 'desc':
        racer_number_sequence = iter(range(number_of_valid_racers, 0, -1))
    else:
        racer_number_sequence = iter(range(1, number_of_valid_racers + 1))
    for racer in prepared_info_for_report:
        if racer.lap_time:
            racer.place = next(racer_number_sequence)
        else:
            racer.place = '-'
    return prepared_info_for_report


def generate_json_data(racers_list):
    info_for_api = [
        {racer.name: {'place': racer.place,
                      'name': racer.name,
                      'team': racer.team,
                      'lap_time': racer.lap_time_str}} for racer in racers_list
    ]
    return jsonify(info_for_api)


def generate_xml_data(racers_list):
    root = ET.Element('racers')
    for racer in racers_list:
        driver = ET.Element('racer', attrib={'name': racer.name})
        root.append(driver)

        drivers_place = ET.SubElement(driver, 'place')
        drivers_place.text = str(racer.place)

        drivers_name = ET.SubElement(driver, 'name')
        drivers_name.text = racer.name

        drivers_team = ET.SubElement(driver, 'team')
        drivers_team.text = racer.team

        drivers_lap_time = ET.SubElement(driver, 'lap_time')
        drivers_lap_time.text = racer.lap_time_str

    return ET.tostring(root).decode()


api.add_resource(Report, '/api/v1/report/')
api.add_resource(Drivers, '/api/v1/report/drivers/')


if __name__ == '__main__':
    app.run(debug=True)