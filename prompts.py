#                   Salutations

say_welcome = "Welcome to ABC Money Transfers<br><br>" \
              "1. Create account<br>" \
              "2. Log in<br>" \
              "3. Exit"

say_goodbye = "Session expired. Say 'hi' to begin."


#                   Create Account

ask_name = "Enter your name:"

ask_surname = "Enter your surname:"

ask_phone_no = "Enter your phone number:"

ask_natId = "Enter your national Id:"

ask_pin = "Enter your PIN:"

acc_creation_succ = """Account Created Successfully"""


#                       Login

ask_login_no = "Enter your phone number:"

ask_login_pin = "Enter your PIN:"

login_failure = "Your phone number or PIN is incorrect.<br><br>" \
                "Enter your phone number:"


#                       Transaction

ask_agent = "Choose name of Agent:<br><br>" \
            "1. Mukuru<br>" \
            "2. InnBucks<br>" \
            "3. World Remit<br>" \
            "4. Access Forex"

ask_reference = "Enter reference number:"

ask_amount = "Enter USD amount:"

ask_dob = "Enter your Date of Birth (DDmmYYYY):"

ask_address = "Enter your pickup address:"

txn_success = "Collection accepted.<br>" \
              "Delivery in progress.<br>" \
              "Please await delivery at: "

txn_failure = f"Some details you entered are incorrect.<br><br>" \
              f"{ask_agent}"

already_collected = f"This transfer has already been collected.<br><br>" \
                    f"{ask_agent}"
