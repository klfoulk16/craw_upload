# URL: http://127.0.0.1:5000/
# OAuth Key: 30610cbd8711af7d322f746b0edb03f9ffa93a9e
# OAuth Secret: 1f43cb75f55f2d8675955f0132f5fdb1ed020b6a

# Request Token Endpoint: https://test.runsignup.com/oauth/requestToken.php
# OAuth Login URL: https://test.runsignup.com/OAuth/Verify
# Access Token Endpoint: https://test.runsignup.com/oauth/accessToken.php

# import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# create webdriver
driver = webdriver.Chrome(ChromeDriverManager().install())
 
#options = Options()
#options.headless = True
#driver = webdriver.Chrome()
 
# open CRAW activity upload page
# get geeksforgeeks.org
driver.get("https://runsignup.com/Race/Results/95983/ActivityEntry?registrationId=45250570&eventId=420485")

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

# # hit submit

driver.find_element_by_name("activity[1][comment]").submit()

