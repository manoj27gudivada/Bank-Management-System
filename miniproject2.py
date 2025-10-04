import mysql.connector as db
from tabulate import tabulate as tab
from datetime import datetime
conn = db.connect(
    host='localhost',
    user='root',
    password='Manoj@7893',
    database='banksystem'
)
cursor = conn.cursor(buffered=True)
def register_user():
    now = datetime.now()
    txn_id = "TXN" + now.strftime("%Y%m%d%H%M%S")
    while True: # Loop for name input
        name = input("Enter Name: ")
        if name.replace(" ", "").isalpha():
            cursor.execute('select name from user where name=%s',(name,))
            result=cursor.fetchone()
            if result:
                print("Name already exists in the database:", result[0])
                print('please enter valid name')
            else:
                print('name successfully added:',name)
                break
                
        else:
            print("Invalid Please enter a valid Name (only alphabets allowed)")

    while True: # Loop for PIN input
        pin = input("Enter 4-digit PIN (must be exactly 4 digits): ")
        if len(pin) == 4 and pin.isdigit():
            break
        else:
            print("Invalid pin,Please enter exactly 4 digits")

    while True:
        valid_account_types = ["Saving", "Current"]
        account_type = input("Enter Account Type (Saving/Current): ").strip().capitalize()
        if account_type in valid_account_types:
            break
        else:
            print("Invalid input. Please enter either 'Saving' or 'Current'.")

    while True: # Loop for phone number input and validation
        phn_no = input("Enter your phone number (10 digits, must start with 6/7/8/9): ")
        if len(phn_no) == 10 and phn_no.isdigit() and phn_no[0] in ['6', '7', '8', '9']:
            cursor.execute("SELECT phn_no FROM user WHERE phn_no = %s", (phn_no,))
            data = cursor.fetchone()

            if data:
                print("This phone number is already registered. Please enter a different number.")
            else:
                break
        else:
            print("Invalid phone number. Please enter a valid 10-digit number starting with 6, 7, 8, or 9.")
    while True: # Loop for initial deposit amount
        balance = input("Enter the Initial Deposit Amount : ")
        if balance.isdigit():
            if int(balance)>=500:
                balance = int(balance)
                break
            else:
                print("The amount must be greater than 500.")
        else:
            print("Please Enter the balance in integer format : ")
    cursor.execute("INSERT INTO user (name, pin, account_type, balance,phn_no) VALUES (%s, %s, %s, %s, %s)",(name, pin, account_type, balance,phn_no))
    conn.commit()

    # Retrieve account number after insertion
    cursor.execute("""
        SELECT account_no
        FROM user
        WHERE name=%s AND pin=%s
        ORDER BY account_no DESC
        LIMIT 1 
    """, (name, pin))

    account_no = cursor.fetchone()[0]
    cursor.execute("select balance from user where account_no = %s",(account_no,))
    bal = cursor.fetchone()
    cursor.execute("INSERT INTO transactions (transaction_id, account_no, transaction_type, transaction_amount,Available_balance)\
                                VALUES (%s, %s, %s, %s, %s)",(txn_id,account_no,'Credit',balance,bal[0]))
    print("Registration Successful! Your Account No:", account_no)

def user_login():
    global acc_no
    try:
        # Step 1: Account number input
        acc_no = int(input("Enter your account number : ").strip())
        cursor.execute("SELECT * FROM user WHERE account_no = %s", (acc_no,))
        data = cursor.fetchone()

        if not data:
            print(" No account found with that number.")
            choice = input("Do you want to open a new account? (Yes/No): ").lower()
            if choice == "yes":
                register_user()
            else: # If user doesn't want to open a new account
                print("Okk Tq")
            return   # stop login if no account
        
        print("Account found!")

        # Step 2: PIN input
        pin_input = input("Enter your 4-digit PIN : ").strip()
        if not (pin_input.isdigit() and len(pin_input) == 4):
            print("PIN must be exactly 4 digits (numbers only).")
            return

        cursor.execute("SELECT * FROM user WHERE account_no = %s AND pin = %s", (acc_no, pin_input))
        user = cursor.fetchone()

        if user:
            print(f"Welcome {user[0]}!") # Assuming user[0] is the name
            user_functions()
        else:
            print("Invalid Credentials. Please check the details you entered.")

    except ValueError:
        print("Invalid input. Account number must contain only digits.")
    except Exception as e:
        print("Unexpected error occurred:", e)

def user_functions():
    while True:
        print("""
                ============ User Menu =============\n
                1. View details
                2. balance check
                3. Pin Change
                4. Credit
                5. Debit
                6. Account Transfer
                7. Statement
                8. Logout \n
                =========== Choose One =============
                """)
        choice = input("Enter what do you want : ")
        if choice == "1": # Viewdetails
            cursor.execute("SELECT * FROM user WHERE account_no = %s", (acc_no,))
            row = cursor.fetchone()
            headers = [desc[0] for desc in cursor.description]  # Get column names
            if row:
                print(tab([row], headers=headers, tablefmt="fancy_grid"))
            else:
                print("No record found.")

            conn.commit()
        elif choice == "2": # Balance Check
            cursor.execute("select name,balance from user where account_no = %s", (acc_no,))
            data = cursor.fetchone()
            headers = [desc[0] for desc in cursor.description]
            if data:
                print(tab([data],headers=headers,tablefmt="fancy_grid"))
            else:
                print("No Record Found")
            conn.commit()
        elif choice == "3":  # Pin change
            attempts = 3  
            while attempts > 0:
                pin = input("Enter your previous pin: ")
                cursor.execute("SELECT pin FROM user WHERE account_no = %s", (acc_no,))
                data = cursor.fetchone()

                if data and str(pin) == str(data[0]):
                    while True:
                        new_pin = input("Enter new pin (4 digits): ")
                        if len(new_pin) != 4 or not new_pin.isdigit():
                            print("PIN must be exactly 4 digits (only numbers). Try again.")
                            continue
                        if new_pin == pin:
                            print("New PIN cannot be the same as the old PIN.")
                            continue

                        confirm_pin = input("Confirm new pin: ")
                        if new_pin != confirm_pin:
                            print("PINs do not match. Please try again.")
                            continue

                        cursor.execute("UPDATE user SET pin = %s WHERE account_no = %s", (new_pin, acc_no))
                        conn.commit()
                        print("PIN successfully updated. Please login again.")
                        print("Please Go Back and Re-login")
                        logged_in = False
                        return
                else:
                    attempts -= 1
                    print(f"Incorrect previous PIN. {attempts} attempt(s) left.")

            print("Too many incorrect attempts. Returning to menu.")


        elif choice == "4":  # Credit amount
            while True:
                new_bal_input = input("Enter the amount to add: ")
                if new_bal_input.isdigit():
                    new_bal = int(new_bal_input)
                    if new_bal > 0:
                        now = datetime.now()
                        txn_id = "TXN" + now.strftime("%Y%m%d%H%M%S") # Generate unique transaction ID
                        cursor.execute("SELECT balance FROM user WHERE account_no = %s", (acc_no,))
                        bal = cursor.fetchone()
                        for i in bal:
                            cursor.execute("UPDATE user SET balance = %s WHERE account_no = %s", (i + new_bal, acc_no))
                            conn.commit()
                            cursor.execute("SELECT balance FROM user WHERE account_no = %s", (acc_no,))
                            dat = cursor.fetchone()
                            for j in dat:
                                cursor.execute("""INSERT INTO transactions 
                                    (transaction_id, account_no, transaction_type, transaction_amount, Available_balance)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (txn_id, acc_no, 'Credit', new_bal, j))

                        conn.commit()

                        cursor.execute("SELECT name, balance FROM user WHERE account_no = %s", (acc_no,))
                        row = cursor.fetchone()
                        headers = [desc[0] for desc in cursor.description]

                        if row:
                            print("The amount has been successfully credited. Available balance:")
                            print(tab([row], headers=headers, tablefmt="fancy_grid"))
                        else:
                            print("No record found.")

                        break  # Exit the loop after successful credit
                    else:
                        print("The entered amount must be greater than 0.")
                else:
                    print("Invalid input. Please enter a positive numeric amount.") # Error for non-numeric input

        elif choice == "5":  # Debit
            while True:
                deb_input = input("Enter the amount to be debited from your account: ")
                if deb_input.isdigit():
                    deb_amnt = int(deb_input)
                    if deb_amnt > 0:
                        now = datetime.now()
                        txn_id = "TXN" + now.strftime("%Y%m%d%H%M%S")
                        cursor.execute("SELECT balance FROM user WHERE account_no = %s", (acc_no,)) # Fetch current balance
                        result = cursor.fetchone()
                        if result:
                            current_balance = result[0]
                            if current_balance >= deb_amnt:
                                new_balance = current_balance - deb_amnt
                                cursor.execute("UPDATE user SET balance = %s WHERE account_no = %s", (new_balance, acc_no))
                                cursor.execute("""INSERT INTO transactions (
                                    transaction_id, account_no, transaction_type, transaction_amount, Available_balance)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (txn_id, acc_no, 'Debit', deb_amnt, new_balance))
                                conn.commit()
                                print("The amount has been debited successfully.")
                                print("your current balance is:")
                                print(tab([[new_balance]], headers=['Balance'], tablefmt="fancy_grid"))
                                break  # Exit loop after successful debit 
                            else:
                                print("Insufficient balance.")
                                print(f"your current balance is: ₹{current_balance}")
                        else:
                            print("Account not found.")
                            break
                    else:
                        print("Please enter an amount greater than 0.")
                else:
                    print("Invalid input. Please enter a numeric amount.")
        
        elif choice == "6":  # Account Transfer
            while True:
                target_input = input("Enter the account number to transfer the amount (or type 'cancel' to go back): ")
                if target_input.lower() == 'cancel':
                    print("Transfer cancelled.")
                    break
                if not target_input.isdigit():
                    print("Invalid input. Account number must contain only digits.")
                    continue

                target_account = int(target_input)

                if target_account == acc_no:
                    print("Cannot transfer to your own account.")
                    continue

                # Check if the target account exists
                cursor.execute("SELECT account_no FROM user WHERE account_no = %s", (target_account,))
                acc = cursor.fetchone()
                if not acc:
                    print("Target account does not exist.")
                    continue

                # Ask for the transfer amount
                amount_input = input("Enter amount to transfer: ")
                if not amount_input.isdigit() or int(amount_input) <= 0:
                    print("Invalid amount. Please enter a positive number.")
                    continue

                amount = int(amount_input)

                # Get sender's balance
                cursor.execute("SELECT balance FROM user WHERE account_no = %s", (acc_no,))
                sender_row = cursor.fetchone()
                if not sender_row:
                    print("Your account could not be found.")
                    break

                sender_bal = sender_row[0]
                if sender_bal < amount:
                    print("Insufficient balance to transfer.")
                    continue

                # Generate unique transaction IDs
                now = datetime.now()
                timestamp = now.strftime("%Y%m%d%H%M%S%f")
                txn_id_sender = f"TXN{timestamp}S"
                txn_id_receiver = f"TXN{timestamp}R"

                # Deduct from sender
                new_sender_bal = sender_bal - amount
                cursor.execute("UPDATE user SET balance = %s WHERE account_no = %s", (new_sender_bal, acc_no))
                cursor.execute("""
                    INSERT INTO transactions (transaction_id, account_no, transaction_type, transaction_amount, Available_balance)
                    VALUES (%s, %s, %s, %s, %s)
                """, (txn_id_sender, acc_no, 'Transfer', amount, new_sender_bal))

                # Add to receiver
                cursor.execute("SELECT balance FROM user WHERE account_no = %s", (target_account,))
                receiver_bal = cursor.fetchone()[0]
                new_receiver_bal = receiver_bal + amount
                cursor.execute("UPDATE user SET balance = %s WHERE account_no = %s", (new_receiver_bal, target_account))

                cursor.execute("""
                    INSERT INTO transactions (transaction_id, account_no, transaction_type, transaction_amount, Available_balance)
                    VALUES (%s, %s, %s, %s, %s)
                """, (txn_id_receiver, target_account, 'Transfer', amount, new_receiver_bal))

                # Commit transaction
                conn.commit()

                print("Transfer successful.")
                print(f"your new balance: {new_sender_bal}")
                headers = ['Available Balance']
                print(tab([[new_sender_bal]], headers=headers, tablefmt="fancy_grid"))
                break

        
        elif choice == "7" :
            cursor.execute("select * from transactions where account_no = %s",(acc_no,))
            stmt = cursor.fetchall()
            headers = ['Transaction_id','Account_no','Transaction_type','Transaction_ammount','Transaction_time','Available_balance']
            print(tab(stmt, headers=headers, tablefmt="f ancy_grid")) 
            conn.commit()
        elif choice=="8":
            break
        elif choice.isalpha():
            print("Please check the choice you have entered.")
        else:
            print("Please choose the correct details from the above choice.")

def admin_login():
    user_name = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()
    if not user_name or not password:
        print("Username and password cannot be empty.")
        return False
    try:
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (user_name, password))
        data = cursor.fetchone()
        if data:
            print("You have successfully logged in as admin.")
            admin_menu()  # Call the menu function after successful login
            return True # Indicate successful login
        else:
            print("Invalid username or password.")
    except Exception as e:
        print(f"Error during login: {e}") # Handle database or other errors
    return False # Indicate failed login

def admin_menu():
        while True:
            print("""
            ============ Admin Menu ============ \n
            1. View All Users
            2. Complete Account Details of a person
            3. View Particular Transaction of user
            4. View Transaction of particular day
            5. Credit Ammount into particular account
            6. Debit ammount from particular account
            7. Delete the particular account
            8. Logout \n
            ============ Choose One ============
            """)
            
            choice = input("Enter your choice: ")

            if choice == "1": # View all users
                cursor.execute("SELECT name,account_type,balance,account_no,date_of_create FROM user")
                data = cursor.fetchall()
                headers = ['Name','Account_type','Balance','Account_no','date_of_create']
                print(tab(data, headers=headers, tablefmt="fancy_grid")) # Display all users
                conn.commit()
            elif choice == "2":  # complete account details of a person
                attempts = 3  # Limit of 3 attempts
                while attempts > 0:
                    acc_no_input = input("Enter the Account number to check the details of a person: ")
                    if acc_no_input.isdigit():
                        acc_no = int(acc_no_input)
                        cursor.execute("SELECT * FROM user WHERE account_no = %s", (acc_no,))
                        data = cursor.fetchone()
                        if data:  # If user exists
                            headers = ['Name', 'PIN', 'Account_type', 'Balance', 'Account_no', 'Date_of_create', "Phone_no"] # Headers for user details
                            print(tab([data], headers=headers, tablefmt="fancy_grid"))
                            break  # Exit the loop after showing the account details
                        else:
                            print("\nNo user found in our logs. Please try again.")
                    else:
                        print("Invalid input! Please enter a valid account number containing only digits.")
                    attempts -= 1
                if attempts == 0:
                    print("You've exceeded the maximum number of attempts. Please try again later.")
                conn.commit()

            elif choice == "3":  # particular transaction of a user
                while True:
                    acc_no_input = input("Enter the account number to check the transaction: ")
                    if acc_no_input.isdigit():
                        acc_no = int(acc_no_input)
                        cursor.execute("SELECT * FROM transactions WHERE account_no = %s", (acc_no,))
                        data = cursor.fetchall()
                        if data:
                            headers = ['Transaction_ID', 'Account_Number', 'Type of Transaction', 'Amount of Transaction', 'Date_of_Transaction', "Available_Balance"] # Headers for transactions
                            print(tab(data, headers=headers, tablefmt="fancy_grid"))
                            break  
                        else:
                            print("\nNo transactions found for this account. Please check the account number.")
                            break  
                    else:
                        print("Invalid input! Please enter a valid account number containing only digits.")
                conn.commit()

            elif choice == "4":  # view transaction of a particular day
                while True:
                    print("1. All Users Transactions    2. One User Transaction   3. Exit")
                    ch = input("Enter your Choice: ")
                    if ch == "1":
                        day = input("Enter the date you want to see the transactions (YYYY-MM-DD): ")
                        try:
                            datetime.strptime(day, "%Y-%m-%d") # Validate date format
                            cursor.execute("SELECT transaction_id, account_no, transaction_type, transaction_amount, transaction_time "
                                           "FROM transactions WHERE DATE(transaction_time) = %s", (day,))
                            data = cursor.fetchall()
                            if data:
                                headers = ['Transaction_id', 'account_no', 'transaction_type', 'transaction_amount', 'transaction_time']
                                print(tab(data, headers=headers, tablefmt="fancy_grid"))
                            else:
                                print("No transactions found for this date.\n")
                        except ValueError:
                            print("Invalid date format! Please enter the date in the format YYYY-MM-DD.\n")
                        conn.commit()
                    elif ch == "2":
                        acc_no_input = input("Enter the user account number to check: ")
                        if acc_no_input.isdigit():
                            acc_no = int(acc_no_input)
                            day = input("Enter the date the user wants to see the transaction (YYYY-MM-DD): ")
                            try: # Validate date format
                                datetime.strptime(day, "%Y-%m-%d")
                                cursor.execute("SELECT * FROM transactions WHERE account_no = %s AND DATE(transaction_time) = %s", (acc_no, day))
                                data = cursor.fetchall()  
                                if data:
                                    headers = ['Transaction_id', 'account_no', 'transaction_type', 'transaction_amount', 'transaction_time']
                                    print(tab(data, headers=headers, tablefmt="fancy_grid"))
                                else:
                                    print("No transactions found for this account on the specified date.\n")
                            except ValueError:
                                print("Invalid date format! Please enter the date in the format YYYY-MM-DD.\n")
                            conn.commit()
                        else:
                            print("Invalid account number! Please enter a valid account number containing only digits.\n")
                    elif ch == "3":
                        break
                    else:
                        print("Invalid choice! Please select a valid option from the menu.\n")

            elif choice == "5":  # Credit amount into a particular account
                while True:
                    acc_no_input = input("Enter account number: ")
                    if acc_no_input.isdigit():
                        acc_no = int(acc_no_input)
                        cursor.execute("SELECT account_no FROM user WHERE account_no = %s", (acc_no,))
                        data = cursor.fetchone()
                        if data:  
                            amount_input = input("Enter amount to add into the user account: ")
                            if amount_input.isdigit() and int(amount_input) > 0:
                                amount = int(amount_input)
                                cursor.execute("SELECT balance FROM user WHERE account_no = %s", (acc_no,))
                                balance_data = cursor.fetchone()
                                current_balance = balance_data[0] # Get current balance
                                new_balance = current_balance + amount
                                cursor.execute("UPDATE user SET balance = %s WHERE account_no = %s", (new_balance, acc_no))
                                now = datetime.now()
                                txn_id = "TXN" + now.strftime("%Y%m%d%H%M%S") + "D"
                                cursor.execute("""
                                    INSERT INTO transactions (transaction_id, account_no, transaction_type, transaction_amount, Available_balance)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (txn_id, acc_no, 'Credit', amount, new_balance))
                                conn.commit()
                                print("The amount is successfully credited into the account.")
                                print(f"the available balance is: {new_balance}")
                                headers = ['Available Balance'] # Headers for balance display
                                print(tab([[new_balance]], headers=headers, tablefmt="fancy_grid"))
                                break  # Exit the loop after successful transaction  
                            else:
                                print("Invalid amount. Please enter a valid positive number.")
                        else:
                            print("Invalid account number, please check again.")
                            break  # Exit if account is invalid
                    else:
                        print("Invalid account number. Please enter a valid numeric account number.")
                        break  # Exit if account number is invalid

            elif choice == "6":  # Debit amount from a particular account
                while True:
                    acc_no_input = input("Enter an account number: ")
                    if acc_no_input.isdigit():
                        acc_no = int(acc_no_input)
                        cursor.execute("SELECT account_no FROM user WHERE account_no = %s", (acc_no,))
                        data = cursor.fetchone()
                        if data:
                            amount_input = input("Enter the amount to withdraw: ")
                            if amount_input.isdigit() and int(amount_input) > 0:
                                amount = int(amount_input)
                                cursor.execute("SELECT balance FROM user WHERE account_no = %s", (acc_no,))
                                bal = cursor.fetchone()
                                if bal and bal[0] >= amount:  # Check if balance is sufficient for debit
                                    new_balance = bal[0] - amount
                                    cursor.execute("UPDATE user SET balance = %s WHERE account_no = %s", (new_balance, acc_no))
                                    txn_id = "TXN" + datetime.now().strftime("%Y%m%d%H%M%S")
                                    cursor.execute("""
                                        INSERT INTO transactions (transaction_id, account_no, transaction_type, transaction_amount, Available_balance)
                                        VALUES (%s, %s, %s, %s, %s)
                                    """, (txn_id, acc_no, 'Debit', amount, new_balance))
                                    conn.commit()
                                    print("The amount has been debited successfully from your account.")
                                    print(f"the available balance is: {new_balance}")
                                    headers = ['Available Balance'] # Headers for balance display
                                    print(tab([[new_balance]], headers=headers, tablefmt="fancy_grid"))
                                    break  # Exit after successful transaction
                                else:
                                    print("Insufficient balance.")
                                    print("the current balance in your account is: ")
                                    print(f"{bal[0]}")
                                    break  # Exit after failure due to insufficient balance
                            else:
                                print("Invalid amount. Please enter a valid positive number.")
                        else:
                            print("Invalid account number. Please check again.")
                            break  # Exit if account is invalid
                    else:
                        print("Invalid account number. Please enter a valid numeric account number.")
                        break  # Exit if account number is invalid
            
            elif choice == "7":  # Delete particular account
                while True:
                    acc_no_input = input("Enter account number to delete: ")
                    
                    # Validate that account number is numeric (or a specific format, if necessary)
                    if acc_no_input.isdigit():  
                        acc_no = int(acc_no_input)
                        cursor.execute("SELECT * FROM user WHERE account_no = %s", (acc_no,))
                        user = cursor.fetchone()

                        if user:  # If account exists
                            confirm = input(f"Are you sure you want to delete account {acc_no}? (yes/no): ").lower()

                            if confirm == "yes":
                                # Delete related transactions first, then the account
                                cursor.execute("DELETE FROM transactions WHERE account_no = %s", (acc_no,))
                                cursor.execute("DELETE FROM user WHERE account_no = %s", (acc_no,))
                                
                                # Commit changes
                                conn.commit()
                                print(f"Account {acc_no} and all its transactions have been deleted successfully.")
                                break  # Exit the loop after deletion
                            else:
                                print("Account deletion cancelled.")
                                break  # Exit if user cancels deletion
                        else:
                            print("Account number not found! Please check the number and try again.")
                            
                    else:
                        print("Invalid account number. Please enter a valid numeric account number.")
                    
                    # Optional: Ask if user wants to try again on failure or exit
                    retry = input("Do you want to try again? (yes/no): ").lower()
                    if retry != "yes":
                        break  
            elif choice == "8":  # Logout
                print("Logging off....")
                break  # Exit loop to log out
            else:
                print("Please Check the above data and enter it.") # Invalid choice for admin menu
            

def main():
    while True:
        print("\n1. User Register  2. user login  3. Admin login  4. Exit")
        choice = input("Enter Choice: ")
        if choice == '1':
            register_user()
        elif choice == '2':
            user_login()
        elif choice == "3":
            admin_login()
        elif choice == '4':
            print("Thank You Visit Again.")
            break
        elif choice.isalpha():
            print("Please check the input you have entered.")
        else:
            print("Please choose the correct details from the above choice.")
if __name__ == "__main__":
    main()
