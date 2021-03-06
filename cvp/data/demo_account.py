"""Generate demo accounts in txt file."""
# import python libraries
import datetime
import random
import string
import os
from base64 import b64encode

# import generate_hash under feature
from cvp.features.transform import generate_hash
from cvp.app.utils import generate_block_hash
from dotenv import load_dotenv

load_dotenv()
# constant values
OLDEST_DOB = datetime.date(1910, 1, 1)  # possible oldest dob
VACCINE_START = datetime.date(2020, 11, 1)  # possible earliest vaccine date
TODAY = datetime.date.today()
RECOMMENDED_INTERVAL = 42 # CDC's recommended interval is within 42 after first dose.
DELIM = '\t'  # deliminator for txt file
ACCOUNT_SIZE = 50


def __get_names(first_names, middle_initials, last_names, inputfile):
    """
    Get names from NAMES file.
    :param first_names: set of first name
    :param middle_initials: set of middle initials
    :param last_names: set of last name
    :raise IOError if no names.txt exists
    :return: None
    """
    # open file of NAMES
    try:
        with open(inputfile) as name_file:
            # read all lines
            while name := name_file.readline():
                if len(name) < 2: continue  # filter empty line
                first, middle, last = name.split()  # unpack and obtrain first, middle, last name from read line.
                # add first, middle, last name to each set
                first_names.add(first)
                middle_initials.add(middle)
                last_names.add(last)
    except OSError:
        raise OSError("Error in reading names file.")


def __get_random_date(start, end):
    """
    Get random date between start date and end date.
    :param start: start date
    :param end: end date
    :return: date of randomly chosen date between start date and end date
    """
    date_range = (end - start).days  # get range in days
    rd_date = random.randrange(0, stop=date_range)  # get random date from date_range
    return start + datetime.timedelta(days=rd_date)  # add rd_date to start date


def __vaccine_name():
    """
    Get random vaccine name.
    :return: string of random vaccine name
    """
    return random.choice(('Pfizer', 'Moderna')) + '-' + random.choice(string.ascii_uppercase) \
           + random.choice(string.ascii_uppercase) + str(random.randint(1000, 9999))


def __account(first, last, middle_i, hospital, acc_id):
    """
    Make account from given information.
    :param first: string of first name in string
    :param last: string of last name in string
    :param middle_i: string of middle initial
    :param hospital: string of hospital name
    :param acc_id: int of account id for this account
    :return: combined single-line string for this account
    """
    user_account_id = str(acc_id)  # store acc_id in string
    domain = '@abc.com'  # sample domain for email address
    email = first.lower() + '.' + last.lower() + domain
    password = first.lower() + last.lower()
    hashed_pass, temp_salt = generate_hash(password)  # get hashed_pass and salt for this password
    hashed_pass = b64encode(hashed_pass).decode('utf-8')
    salt = b64encode(temp_salt).decode('utf-8')
    patient_num = str(random.randint(1000, 9999))  # randomly chosen patient id


    # capitalize names
    last_name = last.capitalize()
    first_name = first.capitalize()

    # if middle_i is empty, set middle to None
    middle = middle_i if middle_i else 'None'
    dob = str(__get_random_date(OLDEST_DOB, TODAY))
    hospital = hospital + random.choice(('MedicalCenter', 'Hospital'))

    vaccine_name1 = vaccine_name2 = __vaccine_name()
    first_dose_latest = TODAY - datetime.timedelta(days=RECOMMENDED_INTERVAL)
    vaccine_date1 = __get_random_date(VACCINE_START, first_dose_latest)
    day_after_first_dose = vaccine_date1+datetime.timedelta(days=1)
    # ideally second dose should be taked within 42 days from first dose.
    vaccine_date2 = __get_random_date(day_after_first_dose, TODAY)
    vaccine_date1 = str(vaccine_date1)
    vaccine_date2 = str(vaccine_date2)

    temp_prev_hash = None

    prev_hash = temp_prev_hash or os.environ['hash_0']
    items = [prev_hash, user_account_id, patient_num, last_name, first_name, middle, dob, vaccine_name1, vaccine_date1,
                 hospital, vaccine_name2, vaccine_date2, prev_hash]
    block_hash = generate_block_hash(items, temp_salt)

    # return all information in string
    return DELIM.join(
        [user_account_id, email, hashed_pass, salt, patient_num, last_name, first_name, middle,
         dob, hospital, vaccine_name1, vaccine_date1, vaccine_name2, vaccine_date2, block_hash])


def generate_accounts(inputfile, outputfile):
    """
    Generate and write account based on the ACCOUNT_SIZE.
    :param inputfile: file to be read to extract sample names
    """
    # initialize first, middle, and last names' set
    first_names, middle_initials, last_names = set(), set(), set()
    __get_names(first_names, middle_initials, last_names, inputfile)
    middle_initials.add('')  # add empty for account that does not have middle

    # make all set to tuple
    first_names, middle_initials, last_names = tuple(first_names), tuple(middle_initials), tuple(last_names)
    with open(outputfile, 'w') as account_file:
        account_file.write('User_Account_ID\tEmail\tPassword\tSalt\tPatient_Num\tLast_Name\tFirst_Name\tMiddle_Initial\t'
                           'Dob\tHospital\tVaccine_Name1\tVaccine_Date1\tVaccine_Name2\tVaccine_Date2\tBlock_Hash\n')
        for acc_id in range(1, ACCOUNT_SIZE + 1):
            acc = __account(random.choice(tuple(first_names)), random.choice(tuple(last_names)),
                            random.choice(tuple(middle_initials)), random.choice(tuple(last_names)), acc_id)
            account_file.write(acc + '\n')  # write to file


if __name__ == '__main__':
    NAMES = 'dataset/raw/names.txt'
    ACCOUNTS = 'dataset/processed/accounts.txt'

    generate_accounts(NAMES, ACCOUNTS)