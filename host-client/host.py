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
	try: # try to click it right away
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		print("\tFailed. Trying again, please wait...\n")
		time.sleep(5)
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	print("\tOpened participants list.\n")
	return

# count_reaction() - counts the number of a chosen reaction at a given time
def count_reaction(driver, reaction_name = "participants-icon__participants-raisehand"):
	hands_raised = driver.find_elements_by_class_name(reaction_name)
	print("number of hands raised: ", len(hands_raised))
	return

def main(argv):
	print("\n\t--- Zoom Education Suite | Host Client ---")
	# testing
	# link_builder() testing
	# print("original link: ", argv[1])
	# print("\n new link: ", link_builder(argv[1]))
	# setup web driver settings
	# start webdriver
	options = webdriver.ChromeOptions() # hiding startup info that pollutes terminal
	options.headless = False
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	driver = webdriver.Chrome(options=options)
	# run program
	login(driver, argv[1])
	open_participants(driver)
	count_reaction(driver)
	time.sleep(10)

if __name__ == '__main__':
	main(sys.argv)