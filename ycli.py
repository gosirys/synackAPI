#!/usr/bin/env python3

# CLI - based on modded API:
# https://github.com/gexpose/synackAPI

from synack import synack
import psycopg2
import subprocess
import os
import sys
import json
import re
from datetime import datetime
import time



args_no = len(sys.argv)

action = str(sys.argv[1])
codename = str(sys.argv[2])

pollSleep = 60

#print(f"zz :"+codename)


# if action != "pull":
#     if args_no < 2:

#         print(f"[-] Missing <codename> argument. Exiting ..")
#         sys.exit(1)
# # else:
# #     codename = str(sys.argv[2].lower())


s1 = synack()
s1.headless = True
s1.configFile = "~/.synack/synack.conf"
s1.connectToPlatform()
s1.getSessionToken()




#ta_root = os.getenv('TA')




if action == "pull":

    while True:
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")

        print("\n[+] "+timestampStr+" - Polling ..")

        s1.getAllTargets()

        new_notifications = s1.pollNotifications()
        
        if len(str(new_notifications)) != 0:

            #print("[+] Got new notifications ..")

            notification_str = str(new_notifications)

            new_targets_found = re.findall("(?<='subject': ')([^']+)', 'subject_type': 'listing', 'action': 'onboarded'",notification_str)

            if new_targets_found:

                print("[+] New target(s) onboarded!\n")

                s1.registerAll()

                print("\n")
                rows = notification_str.split("}}")
                for row in rows:
                    match = re.search("subject': '([^']+)', 'subject_type': 'listing', 'action': 'onboarded', 'url': '[^']+', 'created_at': '[^']+', 'read': [^,]+, 'meta': {'onboard_details': {'action': 'onboard', 'category': '([^']+)', 'codename': '[^']+', 'blitz': [^,]+, 'average_payout': '[^']+', 'last_submitted': '[^']+', 'date_updated': '[^']+'}, 'workspace_required': (True|False)", row) 
                    
                    if match:

                        name = match.group(1)
                        cat = match.group(2)
                        cat_rn = cat

                        if cat == "host":
                            cat_rn = "Host"
                        elif cat == "web application":
                            cat_rn = "Web"

                        if cat == "host" or cat == "web application":

                            if match.group(3) != "True":
                                print("[+] "+name, ' ['+cat_rn+'] is a new target. Fetching data ..\n') 
         
                                s1.fetch_data(name)

                        else:
                            print("\t[-] Target "+name+" is "+cat_rn+". Skipping ..\n")


                print("\n[+] Fetching concluded, resetting notifications ..")

                s1.write_data("json","Notifications","z","notifications.json",notification_str)

                s1.markNotificationsRead()


            # else:
            #     print("\t[-] No new targets onboarded.")

        #else:
            #print("[-] No new notifications ..")


        time.sleep(pollSleep)



elif action == "getData":
    s1.getAllTargets()
    s1.registerAll()
    print("[+] Fetching data for target "+codename+" ..\n")
    s1.fetch_data(codename)
    print("\n[+] All data saved on FS. bye!\n")


