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
# reference: https://browsersize.com/
# reference: https://stackoverflow.com/questions/23381324/how-can-i-control-chromedriver-open-window-size
def start_driver(headless = True):
	# setup webdriver settings
	options = webdriver.ChromeOptions() # hiding startup info that pollutes terminal
	options.headless = headless # headless or not, passed as arg
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	# make window size bigger to see all buttons
	options.add_argument("--window-size=1600,1200")
	# start webdriver
	return webdriver.Chrome(options=options)

# prompt() - prompts the host to enter the room link
def prompt():
	# should probably be a tkinter window, don't know how packaging works with cmd line
	return

# link_builder() - builds web link from og link to skip local app prompt
# future: add password support (for locked rooms)
def link_builder(room_link):
	# replaces /j/ with /wc/join/ to open web client directly
	web_link = re.sub("/j/", "/wc/join/", room_link)
	return web_link

# login() - logs into the room
# reference: https://crossbrowsertesting.com/blog/test-automation/automate-login-with-selenium/
# reference: https://stackoverflow.com/questions/19035186/how-to-select-element-using-xpath-syntax-on-selenium-for-python
# future: add password support (for locked rooms)
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

# click_participants() - click on the participants button
# originally always left open, made this to allow for closing to avoid interference
# refactor: combine this with click_chat() to make general menu opener
def click_participants(driver):
	time.sleep(2)
	try: # try to click it right away
		# find it using the participants icon
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		print("\tFailed. Trying again, please wait...\n")
		time.sleep(7)
		driver.find_element_by_class_name("footer-button__participants-icon").click()
	return

# open_participants() - opens the participants menu, loads all members
def open_participants(driver):
	print("\tOpening participants list...\n")
	click_participants(driver)
	print("\tOpened participants list.\n")
	return

# close_participants() - opens the participants menu, loads all members
def close_participants(driver):
	print("\tClosing participants list...\n")
	click_participants(driver)
	print("\tClosed participants list.\n")
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

# identify_host() - identifies the name of the host
def identify_host(driver):
	# creates target variable to hold element that is current subject of focus
	target = driver.find_element_by_xpath(
		"//*[contains(text(), '(Host)')]") # find the host's webElement
		# "//*[text()='(Host)']") # find the host's webElement
	# tried to accomodate for fake hosts, but had issues--not worth time in hackathon
	if (target.get_attribute("class") != "participants-item__name-label"):
		print("\tSome jerk named themself host to screw with this program.",
			"Make them change their name.\n")
		raise ValueError("Too complicated to handle fake hosts during hackathon.\n")
	target = target.find_element_by_xpath("./..") # go to parent element
	# get other child element of parent; contains host's name
	target = target.find_element_by_class_name("participants-item__display-name")
	# get innerHTML of actual host's name
	recipient_name = target.get_attribute("innerHTML")
	print("\tThe name of the host is:", recipient_name, "\n")
	return recipient_name

# click_chat(driver) - opens or closes chat window
# refactor: combine this with open_participants to make general menu opener
def click_chat(driver):
	time.sleep(2)
	# had to handle making window size bigger because participants list cut off button
	# see driver_start() for solution
	try: # try to click it right away
		# find it using the chat icon
		driver.find_element_by_class_name("footer-button__chat-icon").click()
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		print("\tFailed. Trying again, please wait...\n")
		time.sleep(7)
		driver.find_element_by_class_name("footer-button__chat-icon").click()
	return # successfully clicked (hopefully)

# open_chat() -  opens chat popup
def open_chat(driver):
	print("\tOpening chat menu...\n")
	click_chat(driver) # click on the chat button
	print("\tOpened chat menu.\n")
	return

# close_chat() - closes chat popup
def close_chat(driver):
	print("\tClosing chat menu...\n")
	click_chat(driver) # click on the chat button
	print("\tClosed chat menu.\n")
	return

# choose_recipient() - selects the chosen recipient from the dropdown
def choose_recipient(driver, recipient_name):
	print("\tFinding target recipient.\n")
	# open the dropdown menu
	try: # try to find it right away
		# find the dropdown menu
		dropdown = driver.find_element_by_class_name(
			# "chat-receiver-list__chat-control-receiver ax-outline-blue-important dropdown-toggle btn btn-default")
			"chat-receiver-list__chat-control-receiver")
	except: # if it isn't clickable (sometimes takes a sec to load properly)
		print("\tFailed. Trying again, please wait...\n")
		time.sleep(7)
		dropdown = driver.find_element_by_class_name(
			# "chat-receiver-list__chat-control-receiver ax-outline-blue-important dropdown-toggle btn btn-default")
			"chat-receiver-list__chat-control-receiver")
	dropdown.click() # click the dropdown menu
	time.sleep(2) # lazy way to wait for it to load
	# now find and click on the actual recipient
	# first, focus on the actual dropdown menu of potential recipients
	dropdown = driver.find_element_by_class_name("chat-receiver-list__scrollbar-height")
	# find the element with our recipient's name
	# dropdown.find_element_by_xpath('//dd[@data-value="' + recipient_name + '"])').click()
	# build our string for xpath (probably a better way, but oh well)
	xpath_string = "//a[contains(text(), '" + recipient_name + "')]"
	# print("testing name:\n", xpath_string)
	dropdown_element = dropdown.find_element_by_xpath(xpath_string)
	# now go up a level to the clickable parent
	dropdown_element = dropdown_element.find_element_by_xpath("./..")
	# now actually click the element so we can send 'em a message
	dropdown_element.click()
	# time.sleep(1) # just to be sure (testing)
	return

# type_message() - types out message in chatbox and sends it
def type_message(driver, message):
	# grab chatbox by its class name
	chatbox = driver.find_element_by_class_name("chat-box__chat-textarea")
	# type out the given message in the chatbox
	chatbox.send_keys(message)
	# hit enter in the chatbox to send the message
	chatbox.send_keys(u'\ue007')
	return

# send_message() - have the bot send someone (by default the host) a message
# random string of numbers for default host string accounts for "funny" students
# who might name themselves "host." This string is never visible, so they'd have to guess
# reference: https://stackoverflow.com/questions/12323403/how-do-i-find-an-element-that-contains-specific-text-in-selenium-webdriver-pyth
def send_message(driver, recipient = "host_69974030947301", message = "I'm a bot!"):
	open_chat(driver) # open the chat menu, to enable sending a message
	recipient_name = "" # temporary storage for recipient name
	# participants-item__name-label
	if (recipient == "host_69974030947301"): # if the recipient is default
		# call identify_host() to get host's name
		recipient_name = identify_host(driver) # set host's name to recipient name
	else:
		recipient_name = recipient # set recipient_name to input name
	choose_recipient(driver, recipient_name)
	type_message(driver, message)
	print("\tSending message to:", recipient_name, "\n")
	close_chat(driver) # close the chat menu, since you're done sending a message
	return recipient_name

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

# leave_meeting() - leaves the meeting
# primarily to save sanity during testing--there are currently so many old bots logged in
# broken: clicks getting intercepted(??) for some reason, non-essential feature
def leave_meeting(driver):
	print("\tLeaving meeting...\n")
	driver.find_element_by_class_name("footer__leave-btn").click()
	time.sleep(2) # wait a sec, doesn't need to be great
	# hit tab twice to go to button, could be done better
	# go away, it's just a sanity saver
	# actions = ActionChains(driver)
	# actions.send_keys(Keys.TAB).perform() # press tab key
	# time.sleep(1)
	# actions.send_keys(Keys.TAB).perform() # press tab key again
	# time.sleep(1)
	# actions.send_keys(Keys.TAB).perform() # press tab key again
	# time.sleep(1)
	# actions.send_keys(Keys.ENTER).perform() # press enter key
	# target = driver.find_element_by_xpath("//*[contains(text(), 'Leave Meeting')]")
	print("\tSuccessfully left the meeting. See you next time!\n")
	return

def main(argv):
	print("\n\t--- Zoom Education Suite | Host Client ---\n")
	# testing
	# link_builder() testing
	# print("original link: ", argv[1])
	# print("\n new link: ", link_builder(argv[1]))
	# start the webdriver (True = headless mode)
	driver = start_driver(False)
	# run program
	login(driver, argv[1])
	open_participants(driver)
	count_reaction(driver)
	take_attendance(driver)
	who_participates(driver)
	call_on(driver)
	send_message(driver) # opens and closes chat within the func
	time.sleep(2)
	# leave_meeting() is broken, but non-essential
	# leave_meeting(driver)
	time.sleep(10)
	print("\tFinished.\n")

if __name__ == '__main__':
	main(sys.argv)