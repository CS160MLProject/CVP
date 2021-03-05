import random
import string
import datetime

from cvp.features.transform import generate_hash

NAMES = 'cvp/data/Names.txt'
ACCOUNTS = 'cvp/data/accounts.txt'
OLDEST_DOB = datetime.date(1910, 1, 1)
VACCINE_START = datetime.date(2020, 11, 1)
TODAY = datetime.date.today()
DELIM = ' '
ACCOUNT_SIZE = 10


def get_names(first_names, middle_initials, last_names):
    with open(NAMES) as name_file:
        while name := name_file.readline():
            if len(name) < 2: continue  # filter empty line
            f, m, l = name.split()
            first_names.add(f)
            middle_initials.add(m)
            last_names.add(l)


def account(first, last, middle_i, hospital, userAccountID):
    user_account_id = str(userAccountID)
    domain = '@patient.abc.com'
    email = first.lower() + '.' + last.lower() + domain
    password = first.lower() + last.lower()
    hashed_pass, salt = generate_hash(password)
    patient_num = str(random.randint(1, 9999))
    last_name = last.capitalize()
    first_name = first.capitalize()
    # middle
    date_range = (TODAY - OLDEST_DOB).days
    rd_date = random.randrange(date_range)
    dob = str(OLDEST_DOB + datetime.timedelta(days=rd_date))
    hospital = hospital + random.choice(('MedicalCenter', 'Hospital'))

    def vaccine_name():
        return random.choice(('Pfizer', 'Moderna')) + '-' + random.choice(string.ascii_uppercase) \
                           + random.choice(string.ascii_uppercase) + str(random.randint(1000, 9999))

    vaccine_name1 = vaccine_name()
    date_range = (TODAY - VACCINE_START).days
    rd_date = random.randrange(date_range)
    vaccine_date1 = VACCINE_START + datetime.timedelta(days=rd_date)

    vaccine_name2, vaccine_date2 = 'None', 'None'

    if second_vaccine := random.choice((True, False)) and vaccine_date1 != TODAY:
        vaccine_name2 = vaccine_name()
        date_range = (TODAY - vaccine_date1).days
        rd_date = random.randrange(date_range)
        vaccine_date2 = str(vaccine_date1 + datetime.timedelta(days=rd_date))

    vaccine_date1 = str(vaccine_date1)
    fake = str(not bool(random.randint(0, 9)))

    return DELIM.join(
        [user_account_id, email, hashed_pass, password, salt, patient_num, last_name, first_name, middle_i,
         dob, hospital, vaccine_name1, vaccine_date1, vaccine_name2, vaccine_date2, fake])
    # return DELIM.join([userAccountID, email, password, patient_num, last_name, first_name, middle_i,
    #                    dob, hospital, vaccine_name1, vaccine_date1, vaccine_name2, vaccine_date2, fake])


def generate_accounts():
    first_names, middle_initials, last_names = set(), set(), set()
    get_names(first_names, middle_initials, last_names)
    middle_initials.add('')
    first_names, middle_initials, last_names = tuple(first_names), tuple(middle_initials), tuple(last_names)

    with open(ACCOUNTS, 'w') as account_file:
        for id in range(1, ACCOUNT_SIZE + 1):
            acc = account(random.choice(first_names), random.choice(last_names),
                          random.choice(middle_initials), random.choice(last_names), id)
            print(acc)
            account_file.write(acc + '\n')


if __name__ == '__main__':
    generate_accounts()
