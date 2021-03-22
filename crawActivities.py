import os
import dotenv
import requests
import json
import csv
import time
import datetime
import selenium.webdriver
import sys

def get_tokens():
    """Gets token either from file or by using refresh token if old one is expired.

    :return: Active tokens for use with Strava API
    :rtype: JSON Object
    """
    # USER PROOFING make sure that strava_tokens.json exists with proper
    # refresh token and if not prompt user to use get_initial_token()
    # Get the tokens from file to connect to Strava
    with open("/Users/kellyfoulk/Documents/code/backpackingtrainer/strava_tokens.json") as json_file:
        strava_tokens = json.load(json_file)
    # If access_token has expired then
    # use the refresh_token to get the new access_token
    if strava_tokens["expires_at"] < time.time():
        # Make Strava auth API call with current refresh token
        response = refresh_tokens(strava_tokens)
        # Save response as json in new variable
        new_strava_tokens = response.json()
        # Save new tokens to file
        with open("/Users/kellyfoulk/Documents/code/backpackingtrainer/strava_tokens.json", "w") as outfile:
            json.dump(new_strava_tokens, outfile)
        # Use new Strava tokens from now
        strava_tokens = new_strava_tokens
    return strava_tokens


def refresh_tokens(strava_tokens):
    """Uses strava refresh token to get a new set of tokens."""
    r = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": strava_tokens["refresh_token"],
            },
        )
    return r


def get_page_of_activities(strava_tokens):
    """Downloads specified page of strava activities.

    :param last_activity_date: Start time of most recent activity in activities table. None if table is empty.
    :type last_activity_date: DateTime str or None

    :param page: Page number for activities to get.
    :type page: int

    :param strava_tokens: Active tokens for use with Strava API
    :type: JSON Object

    :return: Response object with JSON dict of activities.
    :rtype: Response Object
    """

    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens["access_token"]

    tstamp = int(os.getenv('LAST_UPLOAD_DATE'))

    return requests.get(
        url
        + "?access_token="
        + access_token
        + "&after="
        + str(tstamp)
    )


def print_to_csv(filename, r):
    """
    Use Strava data to create CSV to upload

    :param filename: Name of CSV file to create
    :type: str

    :param r: array of SummaryActivity objects
    :type: json object
    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Activity Date', 'Distance in Miles', 'Activity Type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for x in range(len(r)):
            # Code to use actual date:
            date = datetime.datetime.strptime(r[x]["start_date_local"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            
            # Code to set all the activities' dates to the day I import them:
            # date = datetime.datetime.today().strftime('%Y-%m-%d')

            # change meters to miles
            distance = round(r[x]["distance"]/1609.34, 2)
            # make sure activity type is not "Hike"
            if r[x]["type"] == 'Hike':
                act_type = 'Walk'
            else:
                act_type = r[x]["type"]
            writer.writerow({'Activity Date': date, 'Distance in Miles': distance, 'Activity Type': act_type})


def upload_csv(file):
    """
    Uses Selenium to upload a file of activities to CRAW.

    :param file: Name of CSV file to upload
    :type: str
    """
    # create webdriver
    driver = selenium.webdriver.Chrome()

    # open CRAW activity upload page
    driver.get(
        "https://runsignup.com/Race/Results/95983/ActivityEntry?registrationId="
        + os.getenv("REGISTRATION_ID")
        + "&eventId="
        + os.getenv("EVENT_ID")
    )

    time.sleep(3)

    # get element for entering email address to authenticate
    element = driver.find_element_by_name("email")
    # type in email
    element.send_keys(os.getenv("EMAIL"))
    element.submit()
    time.sleep(5)
    # select import activities by CSV button
    upload_button = driver.find_element_by_name("activities_file")
    # upload CSV
    file = "/Users/kellyfoulk/Documents/code/crawUpload/daily_upload.csv"
    upload_button.send_keys(file)

    time.sleep(10)   # make sure website is caught up

    # delete pesky empty first item that will cause an error
    delete = driver.find_element_by_xpath("//button[@value='delete']")
    delete.click()

    time.sleep(5)   # make sure website is caught up

    # hit submit
    driver.find_element_by_name("activity[1][comment]").submit()
    time.sleep(3)   # make sure website is caught up

    # check to make sure upload was successful
    if not driver.find_element_by_id("vrActivitiesSuccess").is_displayed():
        driver.quit()
        sys.exit("Craw rejected the CSV upload.")

    driver.quit()


def update_last_upload_date():
    """
    Updates date of last upload in .env file to the current date and time
    """
    date = str(int(time.time()))
    dotenv.set_key("/Users/kellyfoulk/Documents/code/crawUpload/.env", "LAST_UPLOAD_DATE", date)
    print(f"Updated env to {date}")


if __name__ == "__main__":
    # add date for cronlog
    print(datetime.datetime.now())
    # Get environment variables
    dotenv.load_dotenv()

    # strava
    strava_tokens = get_tokens()
    r = get_page_of_activities(strava_tokens)
    
    # if strava worked and there are new activities, upload them
    if r.status_code == 200:
        r = r.json()
        if r:
            filename = "/Users/kellyfoulk/Documents/code/crawUpload/daily_upload.csv"
            print_to_csv(filename, r)
            upload_csv(filename)
        else:
            print("There were no new activities.")
    else:
        sys.exit(f"Was not able to fetch activity array from Strava. Status code: {r.status_code}")
    
    update_last_upload_date()
