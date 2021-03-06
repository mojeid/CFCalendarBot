""" Module responsible data from custom PerfectGym app HTTP responses. """
import json
import logging
import os

import jmespath

_logger = logging.getLogger("json_parser")


class PerfectGymParser:
    """
    Provides parsing functionality specific to PerfectGym system.
    """

    @staticmethod
    def get_class_id_from_classes_list(json_response, class_details):
        """ Parses JSON data and returns Class ID for specific class date/time and trainer."""

        # in PerfectGym startTime property is concatenated date and time with seconds.
        classes_start_time = class_details.date + "T" + class_details.start_time + ":00"

        jmespath_search_operator = "CalendarData[].ClassesPerHour[].ClassesPerDay[]" \
                                   "[?Name=='{name}' && Trainer=='{trainer}' && StartTime=='{start_time}'].Id". \
            format(name=class_details.name, trainer=class_details.trainer, start_time=classes_start_time)

        return max(jmespath.search(jmespath_search_operator, json_response))[0]

    @staticmethod
    def parse_booked_classes_from_users_calendar(json_response):
        """
        Extract list of classes that user has booked form user's calendar.
        :param json_response: Response from PerfectGym system page.
        :return: List with each booked class as tuple
        """
        json_classes_list = json_response['RecentItems']
        booked_classes_list = list()

        for x in json_classes_list:
            from main.data_containers import FitnessClasses
            booked_classes_list.append(
                FitnessClasses(x['Id'], x['Name'], x['StartTime'][:10], x['StartTime'][11:], None, x['Club'],
                               x['Zone']))

        return booked_classes_list

    def get_club_id(class_details):
        """
        Determines correct club ID in the system based on internal list of PerfectGym fitness clubs stored in json file.

        :param class_details: dict with class details must contain fitnessNetwork & clubName entries.

        :return: id of specified club in vendor's system
        """
        club_name = class_details.club
        # List of all supported networks and clubs
        clubs_data = _read_fitness_clubs_json()

        try:
            search_operator = "*[?name == '{club}'].id".format(club=club_name)
            print(search_operator)
            # There will be only one value in 2d array so by using max() we can extract this number.
            return max(max(jmespath.search(search_operator, clubs_data)))
        except ValueError:
            _logger.error('ERROR: There is no club with such name. Please provide correct club name!')
            return


def get_supported_fitness_networks():
    """
    :return: List of supported fitness networks
    """
    json_data = _read_fitness_clubs_json()

    fitness_networks_list = []
    for network in json_data:
        fitness_networks_list.append(network.title())
    return fitness_networks_list


def get_list_of_clubs(fitness_network_name):
    """
    Shows list of currently supported fitness clubs within given Fitness network like Platinium.

    :param fitness_network_name: E.g. Platinium, Crossfit etc
    :return: List of clubs available in that network
    """
    json_data = _read_fitness_clubs_json()
    fitness_clubs = []

    try:
        for club in json_data[fitness_network_name.lower()]:
            fitness_clubs.append(club['name'])
    except KeyError:
        _logger.warning('There is no club with such name. Please provide correct club name')
        return

    return fitness_clubs


def _read_fitness_clubs_json():
    if 'tests' in os.getcwd():
        filepath = '../main/resources/perfectgym_fitness_clubs.json'
    else:
        filepath = 'resources/perfectgym_fitness_clubs.json'

    file = open(filepath)
    json_data = json.loads(file.read())
    file.close()

    return json_data
