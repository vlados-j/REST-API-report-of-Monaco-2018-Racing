from flask import redirect, url_for, render_template, request, Blueprint
from application_vlados import processing_data, build_report


report_f1 = Blueprint('report_f1', __name__, static_folder='static', template_folder='templates')


@report_f1.route('/', methods=['GET'])
def index():
    return redirect(url_for('report_f1.report'))


@report_f1.route('/report/')
def report():
    args = request.args
    structured_info = processing_data('application/files/start.log', 'application/files/end.log',
                                      'application/files/abbreviations.txt')
    prepared_info_for_report = info_for_output(structured_info, args.get("order"))
    return render_template('report.html', prepared_info_for_report=prepared_info_for_report, order=args.get("order"))


@report_f1.route('/report/drivers/')
def drivers():
    args = request.args
    structured_info = processing_data('application/files/start.log', 'application/files/end.log',
                                      'application/files/abbreviations.txt')
    if args.get("abbreviation"):
        for racer in structured_info.values():
            if racer.abbreviation == args.get("abbreviation"):
                return render_template('driver.html', racer=racer)

    prepared_info_for_report = info_for_output(structured_info, args.get("order"))
    return render_template('drivers.html', prepared_info_for_report=prepared_info_for_report, order=args.get("order"))


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
