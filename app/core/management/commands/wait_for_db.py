'''
Django command to wait for the database to be available (db completing startup process)
'''
import time

from psycopg2 import OperationalError as Psycopg2Error
    # exception 'OperationalError' is thrown by pkg 'psycopg2' while trying to connect with db and db isn't yet ready

from django.db.utils import OperationalError
    # this exception 'OperationalError' is thrown by django when db isn't ready
from django.core.management.base import BaseCommand
    # class "BaseCommand's" method 'check' will be used to check the database readiness for connectivity


class Command(BaseCommand):
    '''Django command to wait for database'''
    # our class 'Command' inherited from inbuilt django class 'BaseCommand'

    def handle(self, *args, **options):
        '''Entry point for command'''
        self.stdout.write('Waiting for DB...')
            # 'stdout.write' logging msgs on the console
        db_up = False       # assuming db not available
        while db_up is False:       # run loop while db not available
            try:
                self.check(databases=['default'])
                    # inbuilt base class 'BaseCommand' method 'check' used here
                    # the same method we mocked(changed) in commands test case file 'app/core/tests/test_commands.py'
                    # so, here it is checking the db, if db is available and ready to connect or not
                    # so, if unable to connect with db then immediately it will go to except block
                    # if exception thrown is declared in except block then except block will be executed leaving the rest of the code of try block unexecuted
                    # otherwise the exception will be thrown to the console and prgm will stop
                db_up = True
                    # once db is connected, it become true and loop will stop
            except (Psycopg2Error, OperationalError):
                # these exceptions can be thrown here if unable to connect with db
                # exception will be thrown depending on the stage of db at in starting up process
                self.stdout.write('DB unavailable, waiting 1 sec...')
                time.sleep(1)
                    # it will pause the prgm for 1 sec

        self.stdout.write(self.style.SUCCESS('DB available!'))
            # after db is connected, this line will be executed
            # 'style.SUCCESS' will turn the msg into green
