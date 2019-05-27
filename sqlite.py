import sqlite3
from time import strftime, gmtime

conn = sqlite3.connect("myDB.db", check_same_thread=False)


def db_logs(message):
    with open("db_logs.txt", "a") as myfile:
        myfile.write("{} - {}\n".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), message))


def insert_user(the_name, the_password, the_ip_address):
    """Insert a new user on table
    :param the_name: User name
    :param the_password: User password
    :param the_ip_address: User ip address
    """

    if "+" in the_name:
        full_name = the_name.replace("+", " ")

    try:
        c = conn.cursor()
        if full_name and the_password and the_ip_address != '' or not None:
            c.execute("insert into Person (name, password, ipAddress, is_logged) values (?, ?, ?, 1)",
                      (full_name, the_password, the_ip_address))
        conn.commit()
        c.close()
        db_logs("1 row Inserted!")
    except sqlite3.Error as e:
        db_logs(e)


def login_user(the_username, the_password, ip_address):
    """ Log user on system
    :param the_username: User name
    :param the_password: User password
    """

    if "+" in the_username:
        full_name = the_username.replace("+", " ")

    if the_username and the_password != '' or not None:

        user_exists = check_if_user_exists(the_username, the_password)

        if not user_exists and not the_username in user_exists:
            insert_user(the_username, the_password, ip_address)
        else:
            is_logged = get_user_is_logged(the_username, the_password)
            if is_logged == False:
                c = conn.cursor()
                c.execute("UPDATE Person SET is_logged = ?  WHERE name= ? ",
                          (1, full_name))
                c.close()
                db_logs("Está logado")


def get_user_is_logged(the_name, the_password):
    """Get user if is into database
    :param the_name: User name
    :param the_password: Password
    """
    if "+" in the_name:
        full_name = the_name.replace("+", " ")

    try:
        c = conn.cursor()
        if the_name and the_password != '' or not None:
            c.execute("SELECT is_logged FROM Person WHERE name=? and password=?", (full_name, the_password))
            row = c.fetchall()
            get_int_is_logged = str(row)
            vahlah = get_int_is_logged.split("(")[1].split(",")[0]
            new_valah = int(vahlah)

        c.close()
        if new_valah == 1:
            return True
        else:
            return False

    except sqlite3.Error as e:
        db_logs(e)


def check_if_user_exists(the_name, the_password):
    if "+" in the_name:
        full_name = the_name.replace("+", " ")

    try:
        c = conn.cursor()
        c.execute("SELECT name FROM Person WHERE name=?", (full_name,))
        row = c.fetchall()
        c.close()
        return row
    except sqlite3.Error as e:
        db_logs(e)
