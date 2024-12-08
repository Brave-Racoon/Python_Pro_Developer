#https://regex101.com/

import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import io

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, create_session

from informant_bot.models.models import User, UserAddresses, UserNotify, Street, Address, Blackout
from informant_bot.config import Config


def split_string(nn: str, city: str, string4split: str, dateoff: str) -> list:
    """
    Парсинг списка номеров в строке "Street"
    :param city: город
    :param nn: номер записи из оригинального списка
    :param nn: название н.п.
    :param string4split: входная строка вида "пер. Зерновой 5-7, 2-10, 16, 16Б"
    :param dateoff: дата отключения, которая будет занесена в соотв. поле
    :return: список словарей, состоящий из готовых записей
    """
    # Define the regular expression
    pattern = re.compile(r'(?P<text>[а-яА-Я. «»]+)|(?P<digit>[\d /-а-яА-Я]*[0-9а-яА-я])')
    data = []
    numbers_headers_list = ['Number_from', 'Number_to']
    output_dict = {}
    # Find all matches
    matches = re.findall(pattern, string4split)
    output_dict['Nn'] = nn
    output_dict['City'] = city
    output_dict['Street'] = matches[0][0].strip(' ')
    output_dict[numbers_headers_list[0]] = ''
    output_dict[numbers_headers_list[1]] = ''
    output_dict['Date_from'] = dateoff
    # Iterate over the matches and print them
    for match in matches:
        output_dict[numbers_headers_list[0]] = ''
        output_dict[numbers_headers_list[1]] = ''
        text_part, digit_part = match
        if text_part:
            if len(matches) == 1:  # add record, if street text-part only present
                data.append(output_dict.copy())
        elif digit_part:  # parse digit-part and add records
            digit_part = digit_part.strip(' ')
            dig_part_split_list = digit_part.split('-')
            if 0 < len(dig_part_split_list) < 3:
                for i, item in enumerate(dig_part_split_list):
                    output_dict[numbers_headers_list[i]] = dig_part_split_list[i].strip(' .,;')
                data.append(output_dict.copy())
    return data


def check_json_folder_exists(folder: str) -> str:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Check if the folder exists
    folder_path = os.path.join(script_directory, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"JSON report folder '{folder_path}' not found, created.")
    else:
        print(f"JSON report folder: '{folder_path}'")
    return folder_path


def affect_blackout_recs(table_to_affect, session_) -> bool:
    """Delete all records from the table_to_affect."""
    #session = create_session()
    try:
        # Check if the table has any records
        record_count = session.query(table_to_affect).count()
        if record_count > 0:
            # Delete all records in the table
            session_.query(table_to_affect).delete()
            # Commit the transaction
            session_.commit()
            print(f"{record_count} records in table '{table_to_affect.__tablename__}' deleted successfully.")
        else:
            print("DB empty!")
        return True
    except Exception as excp:
        # Rollback in case of error
        session_.rollback()
        print(f"Error deleting records: {excp}")
        return False


def add_blackouts(blackouts_list: list, session_):
    try:
        for item in blackouts_list:
            street_record = Street(city=item.get('City'), street=item.get('Street'))
            session_.add(street_record)
            session_.flush()  # Flush to get the ID of the newly inserted street record
            address_record = Address(street_id=street_record.id, number_from=item.get('Number_from'),
                                     number_to=item.get('Number_to'))
            session_.add(address_record)
            session_.flush()  # Flush to get the ID of the newly inserted address record
            date_obj = datetime.strptime(item.get('Date_from'), "%d.%m.%y")
            blackout_record = Blackout(address_id=address_record.id, blackout_day=date_obj)
            session_.add(blackout_record)

        session_.commit()
        print(f"{len(blackouts_list)} records inserted.")
    except Exception as ex:
        session_.rollback()
        print(f"Error inserting records: {ex}")


if __name__ == "__main__":

    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    json_subfolder = 'output'
    report_folder = check_json_folder_exists(json_subfolder)
    json_name = datetime.now().strftime("NMES_%Y_%m_%d_%H-%M.json")
    filename = os.path.join(report_folder, json_name)
    url = "https://www.donenergo.ru/grafik-otklyucheniy/57/1/"
    print('Start...')
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table")  # grab all data from html-page with tag "table"
    data = []
    row_values = []

    # headers = ['Nn', 'City', 'Street', 'Date_from', 'Date_to', 'Time_from', 'Time_to', 'Reason', 'Comment']

    for row in table.select("tr")[2:]:  # grab elements with tag filter "tr" from table (table rows)
        row_data = {}  # dict

        row_values = [td.get_text() for td in row.find_all('td')]  # grab all columns to a list[]
        if row_values[1].strip(' ;') == 'г. Новочеркасск':  # particular City only
            # Check if Street contains multiple values, separated by ";":
            streets = row_values[2].strip(' ;')  # cut unnecessary symbols from string begin/end
            streets_list = streets.split(';')  # split streets list
            if streets_list:  # non-empty list?
                for street in streets_list:
                    street = street.strip(' .,;')
                    separated_street_list = split_string(row_values[0], row_values[1].strip(' ;'), street,
                                                         row_values[3])
                    for item in separated_street_list:
                        data.append(item.copy())
            else:  # empty (or only one element) list?
                row_data['Street'] = streets.strip(' .,;')
                separated_street_list = split_string(row_values[0], row_values[1].strip(' ;'), streets, row_values[3])
                data.append(separated_street_list.copy())

    with io.open(filename, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                          indent=4, sort_keys=False,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))
    print('JSON ready.')

    # Prepare to load data to DB
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Attempt to connect to the database
        session.connection()
        print("Connection to the database established successfully.")
        if affect_blackout_recs(Street, session):
            add_blackouts(data, session)
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
    finally:
        session.close()

    print('Done.')
