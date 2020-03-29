# Zoom Host Client - Zoom Education Suite - HooHacks2020 - maxtheaxe
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
# from bs4 import BeautifulSoup as bs
import sys
import re
import urllib.request as urlr
import time

# start_driver() - starts the webdriver and returns it
def start_driver(headless = True):
	# setup webdriver settings
	options = webdriver.ChromeOptions() # hiding startup info that pollutes terminal
	options.headless = headless # headless or not, passed as arg
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	# start webdriver
	return webdriver.Chrome(options=options)

# prompt() - prompts the host to enter the room link
def prompt():
	# should probably be a tkinter window, don't know how packaging works with cmd line
	return

# link_builder() - builds web link from og link to skip local app prompt
def link_builder(room_link):
	# replaces /j/ with /wc/join/ to open web client directly
	web_link = re.sub("/j/", "/wc/join/", room_link)
	return web_link

# login() - logs into the room
# reference: https://crossbrowsertesting.com/blog/test-automation/automate-login-with-selenium/
# reference: https://stackoverflow.com/questions/19035186/how-to-select-element-using-xpath-syntax-on-selenium-for-python
def login(driver, room_link):
	print("\tLogging in...\n")
	web_link = link_builder(room_link) # convert to web client link
	try: # try opening the given link, logging in
		driver.get(web_link) # open zoom meeting login page
		driver.find_element_by_id('inputname').send_keys("zoom edu bot") # enter bot name
		# might need to account for room passwords if using private rooms
		driver.find_element_by_id('joinBtn').click() # click login button
		# driver.send_keys(u'\ue007') # press enter key (alt login method)
	except: # bad link, try again
		print("\tError: Login Failed. Check the link and try again.\n")
		sys.exit()
	try: # wait and make sure we're logged in, loaded into the room
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'footer__leave-btn')))
		if EC.visibility_of(driver.find_element_by_class_name("footer__leave-btn")):
			print("\tSuccessfully logged in.\n")
	except: # something went wrong, we weren't able to load into the room
		print("\tError: Login Failed. Verify that you're connecting to the right room.\n")
		sys.exit()

# open_participants() - opens the participants menu, loads all members
def open_participants(driver):
	print("\tOpening participants list...\n")
	time.sleep(2)
	try: # try to click it right away
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		print("\tFailed. Trying again, please wait...\n")
		time.sleep(7)
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	print("\tOpened participants list.\n")
	return

# count_reaction() - counts the number of a chosen reaction at a given time
def count_reaction(driver, reaction_name = "participants-icon__participants-raisehand"):
	react_list = driver.find_elements_by_class_name(reaction_name)
	print("\tNumber of hands raised: " , len(react_list), "\n") # print total
	return len(react_list) # return number of reactions

# take_attendance() - take attendance of who is there at current time
# I'd have avoided the second list creation, but attendee list was polluted by bot names
# could add filtering out prof later, but requires searching addditional elements
def take_attendance(driver):
	# collect all attendees into list by looking for spans with the following class
	attendee_list = driver.find_elements_by_class_name("participants-item__display-name")
	new_attendee_list = [] # for storing refined list (filters out self)
	for i in range(len(attendee_list)): # for each webElement in list of attendees
		if (attendee_list[i].get_attribute("innerHTML") != "zoom edu bot"): # if not bot
			# then refine to name and add to the new list
			new_attendee_list.append(attendee_list[i].get_attribute("innerHTML"))
	print("\tStudents: ", new_attendee_list)
	return new_attendee_list # return attendee list

def main(argv):
	print("\n\t--- Zoom Education Suite | Host Client ---\n")
	# testing
	# link_builder() testing
	# print("original link: ", argv[1])
	# print("\n new link: ", link_builder(argv[1]))
	# start the webdriver (not in headless mode)
	driver = start_driver(True)
	# run program
	login(driver, argv[1])
	open_participants(driver)
	count_reaction(driver)
	take_attendance(driver)
	time.sleep(10)
	print("\n\tFinished.\n")

if __name__ == '__main__':
	main(sys.argv)