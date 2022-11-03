from flask import Flask, request, jsonify, Response
from flask_restful import Api, Resource
from application_vlados import processing_data, build_report
from dict2xml import dict2xml


app = Flask(__name__)
api = Api(app)


class Report(Resource):
    def get(self):
        args = request.args
        structured_info = processing_data('files/start.log', 'files/end.log',
                                          'files/abbreviations.txt')
        prepared_info_for_report = info_for_output(structured_info, args.get("order"))
        return generate_output_data(prepared_info_for_report, args.get("format"))


class Drivers(Resource):
    def get(self):
        args = request.args
        structured_info = processing_data('files/start.log', 'files/end.log',
                                          'files/abbreviations.txt')
        if args.get("abbreviation"):
            for racer in structured_info.values():
                if racer.abbreviation == args.get("abbreviation"):
                    info_about_racer = {racer.name: {'name': racer.name,
                                                     'team': racer.team,
                                                     'lap_time': racer.lap_time_str}}
                    return generate_output_data(info_about_racer, args.get("format"))
        prepared_info_for_report = info_for_output(structured_info, args.get("order"))
        return generate_output_data(prepared_info_for_report, args.get("format"))


def generate_output_data(info_for_api, format_for_output):
    if format_for_output == 'xml':
        return Response(dict2xml(info_for_api, wrap="racers", indent="  "), mimetype='application/xml')
    else:
        return jsonify(info_for_api)


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

    info_for_api = [
        {racer.name: {'place': racer.place,
                      'name': racer.name,
                      'team': racer.team,
                      'lap_time': racer.lap_time_str}} for racer in prepared_info_for_report
    ]
    return info_for_api


api.add_resource(Report, '/api/v1/report/')
api.add_resource(Drivers, '/api/v1/report/drivers/')


if __name__ == '__main__':
    app.run(debug=True)