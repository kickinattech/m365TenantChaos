'''
    m365_tenanat_chaos
    Do Not Use On Production This Script Will Create and Delete Random Resources
            Parameters:
            -u/--username Enter username to use to login into M365 Tenant.
            -p/--password Enter password to use to login into M365 Tenant.
            -o/--objectname The default text to add to start of objects created with script.
            -b/--banneddomain Domain name to check and stop script
                it matches. Use to check for production domain.
            -m/--maxnumber Maximum number to use in chaos mode.
            -c/--chaosmode Should it run in chaos mode.
            -s/--setupmode Should it run up in setup mode.

            Dependables:
                     AZ and M365 Cli
'''
import subprocess
import string
import random
import json
import argparse
import os
import logging
import time


logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('m365_chaos_tool.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s-%(process)d-%(levelname)s-%(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

parser = argparse.ArgumentParser(
    description="M365 Chaos Logger", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--username",
                    action="store", help="Enter username to use to login \
                     into M365 Tenant.",
                    required=True)
parser.add_argument("-p", "--password",
                    action="store",
                    help="Enter password to use to login into \
                        M365 Tenant.", required=True)
parser.add_argument("-o", "--objectname",
                    action="store",
                    help="The default text to add to start of \
                        objects created with script.",
                    required=True)
parser.add_argument("-b", "--banneddomain",   action="store",
                    help="Domain name to check and stop script it matches.  Use \
                     to check for production domain.",
                    required=True)
parser.add_argument("-m", "--maxnumber",   action="store", default=50,
                    help="Maximum number to use in chaos mode.",
                    required=False)
parser.add_argument("-c", "--chaosmode",  action="store_true",
                    help="Should it run in chaos mode.",
                    required=False)
parser.add_argument("-s", "--setupmode",  action="store_true",
                    help="Should it run up in setup mode.",
                    required=False)
args = parser.parse_args()
config = vars(args)
logger.debug(config)

arg_username = args.username
arg_password = args.password
arg_objectname = args.objectname
arg_banneddomain = args.banneddomain
arg_static = args.chaosmode
arg_maximumnumber = args.maxnumber
arg_setupmode = args.setupmode


class BannedDomainError(LookupError):
    """
    Throws Error On BannedDomainError In M365
    """
    logger.debug("Error: %s", LookupError)


logger.debug("details: %s - %s - %s - %s - %s - %s", arg_username, arg_password, arg_objectname,
             arg_banneddomain, arg_static, arg_setupmode)

# *****************Functions*****************


def get_az_status(
        banneddomain):
    '''
    Returns the status of the m365 client.

            Parameters:
                    None
            Returns:
                      az_account_return (string): The status of the m365 client.
    '''
    logger.debug("Gettting Account Status For Az Cli")
    cmdfull = "account show"
    logger.info("cmdfull is:  az %s ", cmdfull)
    az_account_return = run_az_client(cmdfull, True, True, False)
    logger.debug("Az Status Result: %s", az_account_return.stdout)
    logger.debug("Az status Error Result: %s ", az_account_return.stderr)
    if banneddomain in az_account_return.stdout:
        logger.debug("Banned Domain Found")
        raise BannedDomainError("Banned Domain Found")
    return az_account_return


def get_m365_status(
        banneddomain):
    '''
    Returns the status of the m365 client.

            Parameters:
                    banneddomain (string): Domain name to check and stop script
                     it matches.  Use to check for production domain.
            Returns:
                      m365_status_return output from subproccess.run()
    '''
    logger.debug("Gettting Login Status For M365 Cli")

    m365_status_return = subprocess.run(
        ["m365", "status"], capture_output=True, text=True, check=True)
    logger.debug("M365 Status Result: %s", m365_status_return.stdout)
    logger.debug("M365 status Error Result: %s ", m365_status_return.stderr)
    if banneddomain in m365_status_return.stdout:
        logger.debug("Banned Domain Found In M365 Status")
        raise BannedDomainError("Banned Domain Found In M365 Status")
    return m365_status_return.stdout, m365_status_return.stderr


def login_into_systems(
        m365_username,
        m365_password):
    '''
         Login into third party systems such as AD &
          M365 client.

            Parameters:
                    M365_username (string): Username to use to login into M365.
                    M365_password (string): Password to use to login into M365.
            Returns:
                    None
    '''
    logger.debug(
        "Logging Into M365 Cli Using %s as the username", m365_username)
    m365_login_return = subprocess.run(
        ["m365", "login", "--authType", "password", "-u", m365_username,
         "-p", m365_password], capture_output=True, text=True, check=True)
    logger.debug("M365 Login Result: %s", m365_login_return.stdout)
    logger.debug("MM365 Login Error Result: %s", m365_login_return.stderr)
    m365_status = get_m365_status(arg_banneddomain)
    if arg_username in m365_status[0]:
        logger.debug("M365 Cli Logged In. Current Status: %s", m365_status[0])
    else:
        logger.debug("M365 Cli NOT Logged In. Current Status: %s",
                     m365_status[0])
    logger.debug("Logging Into AD With AZ Command")
    tenant_id = arg_username[arg_username.index('@') + 1:]
    cmdfull = "login -t password -u " + m365_username + " -p " + \
        m365_password + " --allow-no-subscriptions --tenant " + tenant_id
    logger.info("cmdfull is:  az %s ", cmdfull)
    az_account_return = run_az_client(cmdfull, True, True, False)

    logger.debug("M365 Login Result: %s", az_account_return.stdout)
    logger.debug("MM365 Login Error Result: %s", az_account_return.stderr)
    az_status_return = get_az_status(arg_banneddomain)
    logger.debug("Az Status Result: %s", az_status_return.stdout)


def log_out_of_systems():
    '''
    Log out of third party tools such as m365 cli and AZ.

            Parameters:
                    None
            Returns:
                     None
    '''
    logger.debug("Logging Out Of M365")
    m365_loggingout_return = subprocess.run(
        ["m365", "logout"], capture_output=True, text=True, check=True)
    logger.debug("M365 Status Result: %s", m365_loggingout_return.stdout)
    logger.debug("M365 status Error Result: %s ",
                 m365_loggingout_return.stderr)
    logger.debug("Logging Out Of AD")
    cmdfull = "logout"
    logger.info("cmdfull is:  az %s ", cmdfull)
    az_loggingout_return = run_az_client(cmdfull, True, True, False)
    logger.debug("AZ Status Result: %s ", az_loggingout_return.stdout)
    logger.debug("AZ status Error Result: %s", az_loggingout_return.stderr)


def new_groups(
        count,
        group_type):
    '''
         Creates new O365 groups using M365 client.

            Parameters:
                    count(int): How many groups to create as int
                    group_type(string): What type of group to create.
            Returns:
                    None
    '''
    logger.debug("Running New Groups %s times", str(count))
    if count <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        while_count = 1
        logger.debug("count is Greater Than 0")
        while while_count <= count:
            logger.debug("Adding Group The count Is %s of %s  ",
                         str(while_count), str(count))
            # Set Group Type 1 is Public, 2 Is Private & 3 is Random
            if group_type == 1:
                logger.debug("Group Type Is Public")
                is_private_group = False
            elif group_type == 2:
                logger.debug("Group Type Is Private")
                is_private_group = True
            elif group_type == 3:
                is_private_group = random.choice([True, False])
                logger.debug(
                    "Group Type Is Random & Has Been Set To %s", str(is_private_group))
            else:
                raise Exception("Group Type Not Recgonised")
            logger.debug("Adding Group The count Is %s of %s ",
                         str(while_count), str(count))
            letters = string.ascii_lowercase
            random_name = ''.join(random.choice(letters) for i in range(10))
            group_name = arg_objectname + random_name + "-Random-Group"
            logger.info("Creating Group Called %s and Private Is Set To %s",
                        group_name, str(is_private_group).lower())

            cmdfull = "aad o365group add --displayName " + group_name + " --description " \
                + "\"This_is_has_been_added_by_M365_Random_Script\"" + \
                " --mailNickname " + group_name + \
                " --isPrivate " + str(is_private_group).lower()
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_creategroup_return = run_m365client(cmdfull, True, True, True)

            logger.debug("M365 Status Result: %s",
                         m365_creategroup_return.stdout)
            logger.debug("M365 status Error Result: %s ",
                         m365_creategroup_return.stderr)
            while_count = while_count + 1
        logger.debug("Added %s Groups", str(while_count-1))


def new_teams(
        count
):
    '''
         Creates new M365 teams using M365 client.

            Parameters:
                    count(int): How many teams to create as int
            Returns:
                    None
    '''
    logger.debug("Running New Teams %s times",  str(count))
    if count <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        while_count = 1
        logger.debug("count is Greater Than 0")
        while while_count <= count:
            logger.debug("Adding Team The count Is %s of %s ",
                         str(while_count), str(count))
            letters = string.ascii_lowercase
            random_name = ''.join(random.choice(letters) for i in range(10))
            team_name = arg_objectname + random_name + "-Random-teams"
            logger.info("Creating Team Called %s ", team_name)
            cmdfull = "teams team add --name " + team_name + \
                " --description \"This_is_has_been_added_by_M365_Random_Script\"" +\
                " --output text --wait"
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_createteam_return = run_m365client(
                cmdfull, True, True, True)
            logger.debug("M365 Status Result: %s",
                         m365_createteam_return.stdout)
            logger.debug("M365 status Error Result: %s ",
                         m365_createteam_return.stderr)
            while_count = while_count + 1
        logger.debug("Added %s Teams", str(while_count-1))


def remove_teams(
        count):
    '''
    Gets list of O365 teams and removes teams based on the count parmeters.

            Parameters:
                    count(int): How many teams to remove as int

            Returns:
                    no return
    '''
    logger.debug("Running Remove teams %s times ", str(count))
    if count <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        logger.debug("count is Greater Than 0")
        while_count = 1
        while while_count <= count:
            logger.debug("Remove teams The count Is %s of %s ",
                         str(while_count), str(count))
            cmdfull = "teams team list"
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_teamlist_return = run_m365client(cmdfull, True, True, True)
            logger.debug("M365 Status Result: %s", m365_teamlist_return.stdout)
            logger.debug("M365 status Error Result: %s",
                         m365_teamlist_return.stderr)
            team_list = json.loads(m365_teamlist_return.stdout)
            team_list_filtered = [
                x for x in team_list if "-teams" in x['displayName'] and
                arg_objectname in x['displayName']]
            list_total = len(team_list_filtered)

            if list_total == 1:
                logger.debug("Only One App Chaning list_total To 0")
                list_total = 0
            team_id_number = random.randrange(0, list_total)
            team_details = team_list_filtered[team_id_number]
            team_to_remove_name = str(team_details['displayName'])
            team_to_remove_id = str(team_details['id'])
            logger.info("Removing team: %s with the ID of %s ",
                        team_to_remove_name,  team_to_remove_id)

            cmdfull = "teams team remove -i " + team_to_remove_id + " --confirm"
            logger.info("cmdfull is:  m365 %s ", cmdfull)

            m365_removeteam_return = run_m365client(cmdfull, True, True, True)

            logger.debug("M365 Status Result: %s",
                         m365_removeteam_return.stdout)
            logger.debug("M365 status Error Result: %s ",
                         m365_removeteam_return.stderr)
            while_count = while_count + 1
        logger.debug("Removed %s teams", str(while_count-1))


def new_apps(count):
    '''
         Creates new O365 apps using M365 client.

            Parameters:
                    count(int): How many apps to create as int
            Returns:
                    None
    '''
    logger.debug("Running New App %s times", str(count))
    if count <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        logger.debug("count is Greater Than 0")
        while_count = 1
        while while_count <= count:
            logger.debug("Adding App The count Is %s of %s",
                         str(while_count), str(count))
            letters = string.ascii_lowercase
            random_name = ''.join(random.choice(letters) for i in range(10))
            app_name = arg_objectname + random_name + "-Random-App"
            logger.info("Creating App Called %s", app_name)
            cmdfull = "aad app add --name " + app_name + "--withSecret"
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_createapp_return = run_m365client(cmdfull, True, True, True)
            logger.debug("M365 Status Result: %s",
                         m365_createapp_return.stdout)
            logger.debug("M365 status Error Result: %s",
                         m365_createapp_return.stderr)
            while_count = while_count + 1
        logger.debug("Added %s Apps", str(while_count-1))


def remove_apps(
        count):
    '''
         Gets list of apps removes O365 app using M365 client.

            Parameters:
                    count(int): How many apps to remove as int
            Returns:
                    None
    '''
    logger.debug("Running Remove App %s times", str(count))
    if count <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        logger.debug("count is Greater Than 0")
        while_count = 1
        while while_count <= count:
            logger.debug("Remove App The count Is %s of %s ",
                         str(while_count), str(count))
            cmdfull = "ad app list --all"
            logger.info("cmdfull is:  az %s ", cmdfull)
            m365_applist_return = run_az_client(cmdfull, True, True, True)
            logger.debug("AZ Status Result: %s ", m365_applist_return.stdout)
            logger.debug("AZ status Error Result: %s",
                         m365_applist_return.stderr)
            m365_list_unfiltered = json.loads(m365_applist_return.stdout)
            m365_list_filtered = [
                s for s in m365_list_unfiltered if arg_objectname in s['displayName']]
            list_total = len(m365_list_filtered)-1
            if list_total == 0:
                logger.debug("Only One App Chaning list_total To 1")
                list_total = 1
            app_id_number = random.randrange(0, list_total)
            app_details = m365_list_filtered[app_id_number]
            app_to_remove_name = str(app_details['displayName'])
            app_to_remove_id = str(app_details['appId'])
            logger.info("Removing App: %s witht he ID of %s",
                        app_to_remove_name, app_to_remove_id)
            cmdfull = "aad app remove --appId " + app_to_remove_id + " --confirm"
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_removeeapp_return = run_m365client(cmdfull, True, True, True)
            logger.debug("M365 Status Result: %s",
                         m365_removeeapp_return.stdout)
            logger.debug("M365 status Error Result: %s ",
                         m365_removeeapp_return.stderr)
            while_count = while_count + 1
        logger.debug("Removed %s Apps", str(while_count-1))


def remove_groups(
        count):
    '''
    Gets list of O365 groups and removes groups based on the count parmeters.

            Parameters:
                    count(int): How many groups to remove as int

            Returns:
                    no return
    '''
    logger.debug("Running Remove Group %s times", str(count))
    if count <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        logger.debug("count is Greater Than 0")
        while_count = 1
        while while_count <= count:
            logger.debug("Remove Group The count Is %s of %s",
                         str(while_count), str(count))

            cmdfull = "aad o365group list -d " + arg_objectname
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_grouplist_return = run_m365client(cmdfull, True, True, True)
            logger.debug("M365 Status Result: %s",
                         m365_grouplist_return.stdout)
            logger.debug("M365 status Error Result: %s ",
                         m365_grouplist_return.stderr)
            group_list_filtered = json.loads(m365_grouplist_return.stdout)
            list_total = len(group_list_filtered)
            if list_total == 0:
                logger.debug("Only One App Chaning list_total To 1")
                list_total = 1
            group_id_number = random.randrange(0, list_total)
            group_details = group_list_filtered[group_id_number]
            group_to_remove_name = str(group_details['displayName'])
            group_to_remove_id = str(group_details['id'])
            logger.info("Removing Group: %s with the ID of %s",
                        group_to_remove_name, group_to_remove_id)
            cmdfull = "aad o365group remove -i " + group_to_remove_id + " --confirm"
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_removegroup_return = run_m365client(cmdfull, True, True, True)

            logger.debug("M365 Status Result: %s",
                         m365_removegroup_return.stdout)
            logger.debug("M365 status Error Result: %s ",
                         m365_removegroup_return.stderr)
            while_count = while_count + 1
        logger.debug("Removed %s Groups", str(while_count-1))


def add_channels(
        count):
    '''
    Add channels to a random team the count parmeters.

            Parameters:
                    count(int): How many channels to add as int

            Returns:
                    no return
    '''
    logger.debug("Running add channel %s times", str(count))
    if count <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        while_count = 1
        cmdfull = "teams team list"
        logger.info("cmdfull is:  m365 %s ", cmdfull)
        m365_teamlist_return = run_m365client(cmdfull, True, True, True)
        logger.debug("M365 Status Result: %s", m365_teamlist_return.stdout)
        logger.debug("M365 status Error Result: %s ",
                     m365_teamlist_return.stderr)
        team_list = json.loads(m365_teamlist_return.stdout)
        team_list_filtered = [
            x for x in team_list if "-teams" in x['displayName'] and
            arg_objectname in x['displayName']]
        list_total = len(team_list_filtered)

        if list_total == 1:
            logger.debug("Only One App Chaning list_total To 0")
            list_total = 0
        logger.debug("count is Greater Than 0")
        while while_count <= count:
            logger.info("Adding channel The count Is %s of %s ",
                        str(while_count), str(count))

            team_id_number = random.randrange(0, list_total)
            team_details = team_list_filtered[team_id_number]
            team_to_change_name = str(team_details['displayName'])
            team_to_change_id = str(team_details['id'])
            letters = string.ascii_lowercase
            random_name = ''.join(random.choice(letters) for i in range(10))
            channel_name = arg_objectname + random_name + "-Random-channel"
            logger.debug("Creating channel Called %s in %s ",
                         channel_name, team_to_change_name)
            cmdfull = "teams channel add -i " + team_to_change_id + " -n " + channel_name + \
                " --description " + "\"This_is_has_been_added_by_M365_Random_Script\"" + \
                " --output " + "text"
            logger.info("cmdfull is:  m365 %s ", cmdfull)
            m365_createchannel_return = run_m365client(
                cmdfull, True, True, True)
            logger.debug("M365 Status Result: %s",
                         m365_createchannel_return.stdout)
            logger.debug("M365 status Error Result: %s ",
                         m365_createchannel_return.stderr)
            while_count = while_count + 1
        logger.debug("Added %s channels", str(while_count-1))


def get_count_value(
        is_chaosmode,
        maximum_number):
    '''
        Checks if static if not returns random count value else returns static value.

            Parameters:
                    is_chaosmode (Boolen): If going to return a random number or static number
                    maximum_number (int): The maximum number to return if in chaosmode
            Returns:
                    run_count (int): How many times to run the m365 command
    '''
    if is_chaosmode is False:
        if arg_setupmode is False:
            logger.info("Not Running In Setup Mode")
            run_count_return = int(3)
            logger.debug("Running With Fixed Values Of %s",
                         str(run_count_return))
        else:
            logger.info("Running In Setup Mode")
            run_count_return = int(100)
            logger.debug(
                "Running In Setup mode With Fixed Values Of %s", str(run_count_return))
    else:
        run_count_return = random.randrange(1, int(maximum_number))
        logger.debug("Running Chaos Mode With Random Values %s",
                     str(run_count_return))
    return run_count_return


def new_random_files(
        number_of_files_to_create,
        maximum_byte_size,
        file_location):
    '''
        Create random files to number provide..

            Parameters:
                    number_of_files_to_create (int): How many files to create
                    maximum_byte_size (int): The maximum size of the file
                    file_location (str): The location to create the files
            Returns:
                    None
    '''
    directory = os.getcwd()
    logger.debug(directory)
    if not os.path.exists('files'):
        logger.info("Creating Files Folder")
        os.makedirs('files')
    else:
        logger.info("Files Folder Exists Not Creating")
    logger.info("Creating %s files", str(number_of_files_to_create))
    if number_of_files_to_create <= 0:  # pylint: disable=no-else-raise
        raise Exception("count is Less than 0")
    else:
        logger.debug("count is Greater Than 0")
        chars = ''.join([random.choice(string.ascii_letters)
                        for i in range(maximum_byte_size)])

        while_count = 1
        while while_count <= number_of_files_to_create:
            logger.debug("Adding random file the count Is %s of %s",
                         str(while_count), str(number_of_files_to_create))
            letters = string.ascii_lowercase
            random_name = ''.join(random.choice(letters) for i in range(10))

            full_file_path_and_name = file_location + "/" + \
                arg_objectname + random_name + "-Random-File.bit"

            with open(full_file_path_and_name, 'w', encoding="utf-8") as open_file:
                open_file.write(chars)
            while_count = while_count + 1


def run_m365client(
        m365_client_command,
        capture_output_status,
        text_status,
        checks_status,

):
    '''
         Runs the m365 client with parametera provided

            Parameters:
                    m365_client_command (str): The command arguments to run
                    capture_output_status (bool): If to capture the output
                    text_status (bool): If to return the text output
                    checks_status (bool): If to check the status code
            Returns:
                    m365_return (subprocess.CompletedProcess): The return of the m365 client
    '''
    logger.debug("Running M365 client with following parameters: %s",
                 str(m365_client_command))
    argument = f' {m365_client_command}'
    command = f'm365{argument}'.split(' ')
    retry_count = 20
    delay = 10

    m365_status = get_m365_status(arg_banneddomain)
    logger.debug("M365 Status Is %s ", m365_status)
    for _ in range(retry_count):
        logger.debug("Starting M365 The Rety M365 Count Is: %s ", retry_count)
        try:
            m365_cmd_return = subprocess.run(command, capture_output=capture_output_status,
             text=text_status, check=checks_status)
            break
        except subprocess.CalledProcessError as exception:
            logger.debug("M365 status Error Result: %s", exception.stderr)
            logger.debug("M365 Failed- Rety M365 Count: %s ", retry_count)
            retry_count =retry_count - 1
            time.sleep(delay)
    return m365_cmd_return


def run_az_client(
        az_client_command,
        capture_output_status,
        text_status,
        checks_status,

):
    '''
         Runs the m365 client with parametera provided

            Parameters:
                    m365_client_command (str): The command arguments to run
                    capture_output_status (bool): If to capture the output
                    text_status (bool): If to return the text output
                    checks_status (bool): If to check the status code
            Returns:
                    m365_return (subprocess.CompletedProcess): The return of the m365 client
    '''
    logger.debug("Running AZ client with following parameters: %s",
                 str(az_client_command))
    argument = f' {az_client_command}'
    command = f'az{argument}'.split(' ')
    retry_count = 5
    delay = 5

    for _ in range(retry_count):
        logger.debug("Starting AZ The Rety AZ Count Is: %s ", retry_count)
        try:
            az_cmd_return = subprocess.run(command,
                capture_output=capture_output_status, text=text_status, check=checks_status)
            break
        except subprocess.CalledProcessError as exception:
            logger.debug("AZ status Error Result: %s", exception.output)
            logger.debug("AZ Failed- Rety AZ Count: %s ", retry_count)
            time.sleep(delay)
    return az_cmd_return


# *****************Main Script*****************
if str(arg_banneddomain) in str(arg_username):
    raise BannedDomainError("The username containes " +
                            arg_banneddomain + " now stopping script")

if arg_static is False:
    logger.info("Running Chaos Mode With Random Values")
else:
    logger.info("Running With Fixed Values")

m365_version_return = subprocess.run(
    ["m365", "version"], capture_output=True, text=True, check=True)
logger.info("M365 Version Is: %s", m365_version_return.stdout)


logger.info("Logging Out Of Systems in Case User Is Already Logged In")

log_out_of_systems()

logger.info("Logging Into Systems with Script Username & Passwords")
login_into_systems(arg_username, arg_password)

run_count = get_count_value(arg_static, arg_maximumnumber)
add_channels(run_count)

run_count = get_count_value(arg_static, arg_maximumnumber)
new_teams(run_count)

run_count = get_count_value(arg_static, arg_maximumnumber)
new_apps(run_count)

run_count = get_count_value(arg_static, arg_maximumnumber)
new_groups(run_count, 3)

run_count = get_count_value(arg_static, arg_maximumnumber)
add_channels(run_count)

if arg_setupmode is False:
    logger.info("Running Remove Commands As Setup Mode If False")
    run_count = get_count_value(arg_static, arg_maximumnumber)
    remove_teams(run_count)
    run_count = get_count_value(arg_static, arg_maximumnumber)
    remove_apps(run_count)
    run_count = get_count_value(arg_static, arg_maximumnumber)
    remove_groups(run_count)

logger.info(
    "Logging Out Of Systems to Reset 3rd Party Tools Back To Logged Out Status")
log_out_of_systems()
m365_current_status = get_m365_status(arg_banneddomain)
if arg_username in m365_current_status[0]:
    logger.info("M365 Cli Logged In. Current Status: %s",
                m365_current_status[0])
else:
    logger.info("M365 Cli NOT Logged In. Current Status: %s",
                m365_current_status[0])
