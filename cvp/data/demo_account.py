# import python libraries
import datetime
import random
import string

# import generate_hash under feature
from cvp.features.transform import generate_hash

# constant values
NAMES = 'cvp/data/Names.txt'
ACCOUNTS = 'cvp/data/accounts.txt'
OLDEST_DOB = datetime.date(1910, 1, 1)  # possible oldest dob
VACCINE_START = datetime.date(2020, 11, 1)  # possible earliest vaccine date
TODAY = datetime.date.today()
DELIM = ' '  # deliminator for txt file
ACCOUNT_SIZE = 10



def __get_names(first_names, middle_initials, last_names):
    """
    Get names from NAMES file.
    :param first_names: set of first name
    :param middle_initials: set of middle initials
    :param last_names: set of last name
    :return: None
    """
    # open file of NAMES
    with open(NAMES) as name_file:
        # read all lines
        while name := name_file.readline():
            if len(name) < 2: continue  # filter empty line
            first, middle, last = name.split()  # unpack and obtrain first, middle, last name from read line.
            # add first, middle, last name to each set
            first_names.add(first)
            middle_initials.add(middle)
            last_names.add(last)


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
    domain = '@patient.abc.com'  # sample domain for email address
    email = first.lower() + '.' + last.lower() + domain
    password = first.lower() + last.lower()
    hashed_pass, salt = generate_hash(password)  # get hashed_pass and salt for this password
    hashed_pass = str(hashed_pass)
    salt = str(salt)
    patient_num = str(random.randint(1, 9999))  # randomly chosen patient id

    # capitalize names
    last_name = last.capitalize()
    first_name = first.capitalize()

    # if middle_i is empty, set middle to None
    middle = middle_i if middle_i else 'None'

    def get_random_date(start, end):
        """
        Get random date between start date and end date.
        :param start: start date
        :param end: end date
        :return: date of randomly chosen date between start date and end date
        """
        date_range = (end - start).days  # get range in days
        rd_date = random.randrange(date_range)  # get random date from date_range
        return start + datetime.timedelta(days=rd_date)  # add rd_date to start date

    dob = str(get_random_date(OLDEST_DOB, TODAY))
    hospital = hospital + random.choice(('MedicalCenter', 'Hospital'))

    def vaccine_name():
        """
        Get random vaccine name.
        :return: string of random vaccine name
        """
        return random.choice(('Pfizer', 'Moderna')) + '-' + random.choice(string.ascii_uppercase) \
               + random.choice(string.ascii_uppercase) + str(random.randint(1000, 9999))

    vaccine_name1 = vaccine_name()
    vaccine_date1 = get_random_date(VACCINE_START, TODAY)

    # initialize second vaccine info
    vaccine_name2, vaccine_date2 = 'None', 'None'

    # randomly select True or False of second vaccine shot
    # if second vaccine is True and fist shot is not today
    if random.choice((True, False)) and vaccine_date1 != TODAY:
        vaccine_name2 = vaccine_name()
        vaccine_date2 = str(get_random_date(vaccine_date1, TODAY))

    vaccine_date1 = str(vaccine_date1)

    # fake is true if this demo account is not in CDC database.
    # 1:9 ratio of true, false
    fake = str(not bool(random.randint(0, 9)))

    # return all information in string
    return DELIM.join(
        [user_account_id, email, hashed_pass, password, salt, patient_num, last_name, first_name, middle,
         dob, hospital, vaccine_name1, vaccine_date1, vaccine_name2, vaccine_date2, fake])


def generate_accounts():
    """Generate and write account based on the ACCOUNT_SIZE."""
    # initialize first, middle, and last names' set
    first_names, middle_initials, last_names = set(), set(), set()
    __get_names(first_names, middle_initials, last_names)
    middle_initials.add('')  # add empty for account that does not have middle

    # make all set to tuple
    first_names, middle_initials, last_names = tuple(first_names), tuple(middle_initials), tuple(last_names)

    with open(ACCOUNTS, 'w') as account_file:
        for acc_id in range(1, ACCOUNT_SIZE + 1):
            acc = __account(random.choice(tuple(first_names)), random.choice(tuple(last_names)),
                            random.choice(tuple(middle_initials)), random.choice(tuple(last_names)), acc_id)
            account_file.write(acc + '\n')  # write to file


if __name__ == '__main__':
    generate_accounts()
