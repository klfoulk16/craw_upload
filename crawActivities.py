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

    # today minus total number of seconds in a day
    tstamp = int(os.getenv('LAST_UPLOAD_DATE'))

    #tstamp = 1611816430

    return requests.get(
        url
        + "?access_token="
        + access_token
        + "&after="
        + str(tstamp)
    )


def print_to_csv(filename):
    dotenv.load_dotenv()
    strava_tokens = get_tokens()
    r = get_page_of_activities(strava_tokens)
    if r.status_code == 200:
        r = r.json()
        if r:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Activity Date', 'Distance in Miles', 'Activity Type']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for x in range(len(r)):
                    # old code used actual date
                    # date = datetime.datetime.strptime(r[x]["start_date_local"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                    # to avoid errors importing tuesday's stuff on wednesday 
                    # if there was something that was missed
                    # let's set all the dates to the day we're importing them
                    date = datetime.datetime.today().strftime('%Y-%m-%d')
                    # change meters to miles
                    distance = round(r[x]["distance"]/1609.34, 2)
                    # make sure activity type is not "Hike"
                    if r[x]["type"] == 'Hike':
                        act_type = 'Walk'
                    else:
                        act_type = r[x]["type"]
                    writer.writerow({'Activity Date': date, 'Distance in Miles': distance, 'Activity Type': act_type})
        else:
            print("There were no new activities.")
            update_last_upload_date()
            sys.exit()
    else:
        sys.exit(f"Was not able to fetch activity array from Strava. Status code: {r.status_code}")


def mock_to_csv(filename):
    r = [{'resource_state': 2, 'athlete': {'id': 69777155, 'resource_state': 1}, 'name': 'Afternoon Hike', 'distance': 1757.3, 'moving_time': 1010, 'elapsed_time': 1063, 'total_elevation_gain': 8.6, 'type': 'Hike', 'id': 4719328717, 'external_id': '8C063405-C9AC-434B-9A8A-36732B37D01D-activity.fit', 'upload_id': 5038054720, 'start_date': '2021-02-01T22:37:26Z', 'start_date_local': '2021-02-01T17:37:26Z', 'timezone': '(GMT-05:00) America/New_York', 'utc_offset': -18000.0, 'start_latlng': [39.60467, -76.167497], 'end_latlng': [39.604805, -76.167373], 'location_city': None, 'location_state': None, 'location_country': None, 'start_latitude': 39.60467, 'start_longitude': -76.167497, 'achievement_count': 0, 'kudos_count': 0, 'comment_count': 0, 'athlete_count': 1, 'photo_count': 0, 'map': {'id': 'a4719328717', 'summary_polyline': 'ehvpFzm{oMXFABBBLAFICQPg@NQJEFGDSFKf@YPQPAXWYTUFa@VINIDMPITKDONELKl@OJQ?EH?PDAAQBEFCL?NOPcAJILCFUJSJEJKd@[`@QJMUT]L_@\\]RKPCRCBKBONI^?RINIBI@OEEKBGBA@BGH?DIDCC@GDELBBJ?CEEi@Kf@Bs@UTC', 'resource_state': 2}, 'trainer': False, 'commute': False, 'manual': False, 'private': True, 'visibility': 'only_me', 'flagged': False, 'gear_id': 'g7561258', 'from_accepted_tag': False, 'upload_id_str': '5038054720', 'average_speed': 0.75, 'max_speed': 8.5, 'has_heartrate': False, 'heartrate_opt_out': False, 'display_hide_heartrate_option': False, 'elev_high': 93.6, 'elev_low': 88.9, 'pr_count': 0, 'total_photo_count': 0, 'has_kudoed': False}]
    if r:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Activity Date', 'Distance in Miles', 'Activity Type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for x in range(len(r)):
                # old code used actual date, but now I'm just going to use 
                # "today's" date to avoid any timing errors (dreaded tuesday)
                # date = datetime.datetime.strptime(r[x]["start_date_local"],
                # "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                date = datetime.datetime.today().strftime('%Y-%m-%d')
                # change meters to miles
                distance = round(r[x]["distance"]/1609.34, 2)
                # make sure activity type is not "Hike"
                if r[x]["type"] == 'Hike':
                    act_type = 'Walk'
                else:
                    act_type = r[x]["type"]
                writer.writerow({'Activity Date': date, 'Distance in Miles': distance, 'Activity Type': act_type})
    else:
        print("Was not able to fetch summary activity array.")


def upload_csv(file):
    # # create webdriver
    driver = selenium.webdriver.Chrome()

    # open CRAW activity upload page
    # get geeksforgeeks.org
    driver.get("https://runsignup.com/Race/Results/95983/ActivityEntry?registrationId=***REMOVED***&eventId=***REMOVED***")

    # # potentially handle login issues
    # #type in email address
    # # get element 
    element = driver.find_element_by_name("email")

    # # send keys 
    element.send_keys("***REMOVED***")
    element.submit()

    # # select import activities by CSV
    # #upload_button = driver.find_element_by_id("uploadActivities")
    upload_button = driver.find_element_by_name("activities_file")

    # # upload CSV
    file = "/Users/kellyfoulk/Documents/code/crawUpload/daily_upload.csv"
    upload_button.send_keys(file)

    # # delete pesky first item
    delete = driver.find_element_by_xpath("//button[@value='delete']")
    delete.click()
    time.sleep(1)

    # # hit submit
    driver.find_element_by_name("activity[1][comment]").submit()
    time.sleep(1)

    # check to make sure upload was successful
    if not driver.find_element_by_id("vrActivitiesSuccess").is_displayed():
        driver.quit()
        sys.exit("Craw rejected the CSV upload.")

    driver.quit()


def update_last_upload_date():
    """Updates date of last upload in .env file to the current date and time"""
    date = str(int(time.time()))
    dotenv.set_key("/Users/kellyfoulk/Documents/code/crawUpload/.env", "LAST_UPLOAD_DATE", date)
    print(f"Updated env to {date}")


if __name__ == "__main__":
    # add date for cronlog
    print(datetime.datetime.now())
    # Get environment variables
    dotenv.load_dotenv()
    filename = "/Users/kellyfoulk/Documents/code/crawUpload/daily_upload.csv"
    print_to_csv(filename)
    #mock_to_csv(filename)
    upload_csv(filename)
    update_last_upload_date()
