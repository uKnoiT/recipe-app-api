'''
Test custom Django management commands
'''
from unittest.mock import patch
    # 'patch' will mock(change/patch) the behavior of db and then simulate(create duplicate/desired response) the response if db wont give any response or any undesired response

from psycopg2 import OperationalError as Psycopg2Error
    # we get operational err from pkg 'psycopg2' while trying to connect with db when db isn't yet ready to use,
    # so we will use exception 'OperationalError' as 'Psycopg2Error' to handle those errs

from django.core.management import call_command
    # 'call_command' is a django helper function use to call a django management command
from django.db.utils import OperationalError
    # we may get any other operational err from db depending on what stage of startup process it is at when trying to connect with it,
    # so we will use exception 'OperationalError' to handle those errs
from django.test import SimpleTestCase
    # 'SimpleTestCase' is a base test class which will be used for creating unit test cases for testing commands
    # also, it is helpful to test empty db by simulating(creating) the behavior of a non empty db


@patch('core.management.commands.wait_for_db.Command.check')
    # 'patch' is a python decorator function
    # declaring it just above the cls declaration so that all the (test) functions inside below cls 'CommandTests' can use it
    # it has path to management commands file 'app/core/management/commands/wait_for_db.py', and
    # succeeding that is our class 'Command' inherited from django class 'BaseCommand' and using its fnc 'check()'
    # method 'check' will check the status of db, and may return an exception(i.e., an err)
    # so, fn 'patch' will mock(change/patch) method 'check' to simulate(generate desired response) its response
# since no db is integrated, so we cant check the db yet, so we are creating the desired response by ourself and using fn 'patched_check' to return that response when testing the db for its readiness
class CommandTests(SimpleTestCase):
    '''Test Commands'''
    # our class 'CommandTests' inherited from inbuilt django class 'SimpleTestCase'

    def test_wait_for_db_ready(self, patched_check):
        # this test case is for condition - when db is ready
        # print('p_c type',type(patched_check))
        # patched(changed) 'check' fn is passed here as an argument 'patched_check'
        # this argument is created by above decorator fn 'patch'
        '''Test waiting for db if db is ready'''
        patched_check.return_value = True
            # we set fn 'patched_check' variable 'return_value' to True
            # so, when 'patched_check' is called in test case(here), it just simply return True

        call_command('wait_for_db')
            # fn 'call_command' will execute code(commands) written in file 'app/core/management/commands/wait_for_db.py'
            # 'call_command' check if db is ready or not
            # also, 'call_command' automatically check if code(commands) written correctly or not by executing it

        patched_check.assert_called_once_with(databases=['default'])
            # it ensure that 'patched_check' is called only once, with parameter 'databases=['default']'
            # it means it is called with default db i.e., postgres inside fn 'test_wait_for_db_ready'

    @patch('time.sleep')
        # declaring 'patch' here so that only below fn 'test_wait_for_db_delay' can use it
        # so, whenever any exception is thrown on checking the db, the unit testing wait for sometime until it call the below test case fn again to chk the db
        # to prevent the unnecessary calls to the db
        # so, bcz of waiting/sleeping of unit test for some period due to exception, it slows down the unit testing process
        # so, to make unit test not wait/sleep after getting an exception we will mock(change/patch) python 'sleep' method
        # so now, 'patched_sleep' will give a non value(value not fit as an acceptable time)
        # so now, unit testing wont pause/sleep and continuously call the below test case fn
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        # this test case is for condition - when db is not ready
        # the arguments in the fn shud be in this order only
        # arg for lowest patch shud be at leftmost (after self) and accordingly it goes
        '''Test waiting for db when getting Operational Err'''
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
            # to raise an exception when db is not ready, we will do this
            # variable 'side_effect' holds the list of various different items which will be handled according to their type
            # the ith time current fn is called (in startup process), ith item in the list is processed
            # if the item is an exception then fn 'patched_check' will raise that exception,
            # and if its a boolean then that boolean will be returned by fn 'patched_check'
            # we can set the quantity of the exceptions according to our needs in the order we want
            # currently the list holds Ist 2 items as 'Psycopg2Error' exceptions, then 3 'OperationalError' exceptions, and then 1 boolean value
            # 'Psycopg2Error' exception is a postgres exception for when postgres db is not started, so adding this exception first
            # 'OperationalError' exception is a django exception for when postgres db is started, but its not setup completely i.e., dev db not created yet, so adding it after 'Psycopg2Error'
            # and last is the boolean value 'True' for

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
            # it will chk that fn 'patched_check' is called exactly 6 times bcz the 'side_effect' list has 6 items,
            # and on ith call the ith item from 'side_effect' will be returned
            # so, at 6th time it will return True
            # bcz otherwise 'patched_check' will be called again and again until it return True
        patched_check.assert_called_with(databases=['default'])
            # it ensure that 'patched_check' is called with parameter 'databases=['default']' every time
            # it means it is called with default db i.e., postgres inside fn 'test_wait_for_db_delay'
