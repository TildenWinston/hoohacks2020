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
import random

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
	# find elements of given reaction class (hand raise by default)
	react_list = driver.find_elements_by_class_name(reaction_name)
	print("\tNumber of hands raised: " , len(react_list), "\n") # print total
	return len(react_list) # return number of reactions

# who_participates() - checks who is currently participating (via reactions)
# reference: https://stackoverflow.com/questions/18079765/how-to-find-parent-elements-by-python-webdriver
def who_participates(driver, reaction_name = "participants-icon__participants-raisehand"):
	participant_list = [] # empty list to hold participants
	# find elements of given reaction class (hand raise by default)
	react_list = driver.find_elements_by_class_name(reaction_name)
	for i in range(len(react_list)): # for each reaction element (belongs to a person)
		# go to grandparent element, so we can check the name (store in curr element)
		react_list[i] = react_list[i].find_element_by_xpath("../..")
		# get the name element (store in curr element)
		react_list[i] = react_list[i].find_element_by_class_name("participants-item__display-name")
		# refine to name string (store in curr element)
		react_list[i] = react_list[i].get_attribute("innerHTML")
	print("\tPeople raising hands: " , react_list, "\n") # print total
	return react_list # return list of people reacting

# call_on() - calls on the first person to raise their hand; if it can't tell, randomizes
def call_on(driver):
	hand_raiser_list = who_participates(driver) # check who is raising their hand rn
	if (len(hand_raiser_list) == 0): # if no-one is raising their hand
		print("\tYou can't call on anyone if no-one is raising their hand!\n")
		return # return no-one
	elif (len(hand_raiser_list) == 1): # if one person is raising their hand
		print("\tThey raised their hand first, so you called on:",
			hand_raiser_list[0], "\n") # print selection
		return hand_raiser_list[0] # return the one person raising their hand
	else: # if more than one person is raising their hand
		chosen_person = random.choice(hand_raiser_list) # choose someone randomly
		print("\tYou didn't see who was first, so you guessed and called on:",
			chosen_person, "\n") # print selection
		return chosen_person # return your "guess" at who was first

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
	print("\tStudents: ", new_attendee_list, "\n") # print list of attendee names
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
	who_participates(driver)
	call_on(driver)
	time.sleep(10)
	print("\tFinished.\n")

if __name__ == '__main__':
	main(sys.argv)