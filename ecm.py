#!/usr/bin/env python
"""
Purpose:

    An ECM pilot can quickly determine which ECM jammers to fit and activate for
    a fight.

Syntax:

    Unix/Linux:
        ./ecm.py <ship_name_1> <ship_name_2> <ship_name_3>...<ship_name_N>

    Windows:
        python ecm.py <ship_name_1> <ship_name_2> <ship_name_3>...<ship_name_N>

Example: 

    rusty@kermit:~/ecm $ ./ecm.py corm merl vni falc

    10 Falcon                    (Gravimetric - Blue       ) Caldari    Force Recon Ship
     5 Vexor Navy Issue          (Magnetometric - Turquoise) Gallente   Cruiser
     2 Cormorant                 (Gravimetric - Blue       ) Caldari    Destroyer
     1 Merlin                    (Gravimetric - Blue       ) Caldari    Frigate

Notes:  
    
    Ship name arguments are case insensitive.

    Ship name arguments may be partial ship names. E.g. 'vex' instead
    of 'vexor'

    A search argument may produce multiple matches. E.g. 'vex' returns
    records for 'Vexor', 'Vexor Navy Issue', etc.

    Some ships have alternate names or abbreviations to aid in
    searching.  E.g. 'vni' instead of 'vexor navy issue'

    The ship database (ecm.csv) is fairly complete. I excluded the rare,
    special edition ships that would not typically be used in combat. I assigned
    each ship a rank (1..10) for their ECM jamming priority. Highest ECM priority
    is given to the ECM and Logistic boats.  Capitals are generally given a low ECM
    priority since more desirable jamming targets are typically available on the
    field. 

    I am very new to flying EVE Online ECM boats - I fly a Griffin. I need your
    help to improve the ship database ECM rankings and also with alternate
    abbreviations for ship names. Your FCs will have ideas about how best to rank
    ships for your own fleet fights. Please do not hesitate to send me your
    database revisions or any other suggestions to improve this tiny console
    script. 

Installation:

    First install python on your computer. If you are using Windows then the
    Active Python community edition is effective and is also free of cost. See
    their site at https://www.activestate.com/activepython

    Download the script (ecm.py) and database (ecm.csv) from the my git project
    at: https://github.com/rustyhobbit/rustyhobbit-ecm.git

    If you are on Unix/Linux, chmod the ecm.py script to make it executable.

    Open a console window in the directory where you downloaded ecm.py and ecm.csv
    and run the ecm.py script with python.

Contact:

    'Rusty Hobbit' via EVEMail or rustyhobbit@gmail.com

License:

    MIT License. Please see the LICENSE file included in this project.


"""

import sys, os, traceback, optparse
import time
import re
import csv
import random
import collections


# sort comparator to sort a ship_record list by ecm_priority
# this is needed because I want to display matching ships in their ecm priority ranking
def sort_by_ecm_priority(ship_record_1, ship_record_2):
    # return -1 if a>b, 0 if a==b, 1 if a<b
    if int(ship_record_1.ecm_priority) > int(ship_record_2.ecm_priority):
        result = -1
    elif int(ship_record_1.ecm_priority) == int(ship_record_2.ecm_priority):
        result = 0
    else:
        result = 1

    return result

# the main thing
def main ():
    global options, args
    
    all_records = []
    line = 1

    # Create a namedtuple - very useful because you can 
    # use dot notation (obj.attr) to reference csv fields
    ShipRecord = collections.namedtuple('ShipRecord', ['ship','ship_class','ecm_race','ecm_priority','alt_name_1','alt_name_2'])

    # load data from csv file
    shipdata = csv.reader(open('ecm.csv', 'rb'))
    for ship, ship_class, ecm_race, ecm_priority, alt_name_1, alt_name_2 in shipdata:
        if line > 1: # don't include the header (line 1)

            # create a namedtuple of the ship record
            ship_record = ShipRecord(ship, ship_class, ecm_race, ecm_priority, alt_name_1, alt_name_2)

            #append ship_record to the list
            all_records.append(ship_record)

        # increment the line counter
        line += 1

    #print '%r' % all_records
    #print "Loaded %r ship records" % (line - 1)

    # create a dict of all args (ship names) so that you
    # can later identify any ship name args that have NO MATCHES
    arg_dict = {}
    for ship_name in args:
        arg_dict[ship_name] = False

    # create list to store matching ship records    
    output_ship_list = []

    # roll through each ship record and look for matching ship names
    # lowercase all comparisons
    for ship_record in all_records:
        found_match = False
        for ship_name in args:
            if ship_record.ship.lower().find(ship_name.lower()) > -1:
                found_match = True
                arg_dict[ship_name] = True
                break
            if ship_record.alt_name_1.lower().find(ship_name.lower()) > -1:
                found_match = True
                arg_dict[ship_name] = True
                break
            if ship_record.alt_name_2.lower().find(ship_name.lower()) > -1:
                found_match = True
                arg_dict[ship_name] = True
                break

        if found_match:
            #print ship_record

            # add ship_record to output_ship_list
            output_ship_list.append(ship_record)

                
    # sort output_ship_list by ecm_priority, descending order
    output_ship_list.sort(sort_by_ecm_priority)

    #print output_ship_list

    for ship_record in output_ship_list:
        jammer_to_use = "unknown"
        if ship_record.ecm_race.lower() == "minmatar":
            jammer_to_use = "Ladar - Red"
        elif ship_record.ecm_race.lower() == "caldari":
            jammer_to_use = "Gravimetric - Blue"
        elif ship_record.ecm_race.lower() == "gallente":
            jammer_to_use = "Magnetometric - Turquoise"
        elif ship_record.ecm_race.lower() == "amarr":
            jammer_to_use = "Radar - Yellow"
        else:
            jammer_to_use = "Unknown - No ECM Race"
            
        print ("{:>2} {:<25} ({:<25}) {:<10} {:<15}".format(ship_record.ecm_priority, ship_record.ship, jammer_to_use, ship_record.ecm_race, ship_record.ship_class))

    print ""

    # display any ship name args that had NO MATCHES
    for key in arg_dict:
        if arg_dict[key] == False:
            print "'%s' - No matching ship name" % (key)


if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id$')
        parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
        (options, args) = parser.parse_args()
        if len(args) < 1:
            parser.error ('An argument is missing')
        if options.verbose: print time.asctime()
        main()
        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME IN MINUTES:',
        if options.verbose: print (time.time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)


