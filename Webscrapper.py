import requests
from bs4 import BeautifulSoup

def smart_capitalize(text):
    exceptions = {'the', 'of', 'for', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'with'}
    words = text.lower().split()
    result = []

    for i, word in enumerate(words):
        if i == 0 or word not in exceptions:
            result.append(word.capitalize())
        else:
            result.append(word)
    
    return ' '.join(result)

def doctorconverter(data):
	doctor_number_map = {
		'Fugitive Doctor': 'Fugitive Dr',
		'First Doctor': '1st Dr',
		'Second Doctor': '2nd Dr',
		'Third Doctor': '3rd Dr',
		'Fourth Doctor': '4th Dr',
		'Fifth Doctor': '5th Dr',
		'Sixth Doctor': '6th Dr',
		'Seventh Doctor': '7th Dr',
		'Eighth Doctor': '8th Dr',
		'War Doctor': 'War Dr',
		'Ninth Doctor': '9th Dr',
		'Tenth Doctor': '10th Dr',
		'Eleventh Doctor': '11th Dr',
		'Twelfth Doctor': '12th Dr',
		'Thirteenth Doctor': '13th Dr',
		'Fourteenth Doctor': '14th Dr',
		'Fifteenth Doctor': '15th Dr'
	}
	formatted_data = [doctor_number_map.get(d, d) for d in data]
	return formatted_data

def fetch_data(name, media_type):
	# URL of the website to fetch data from
	if media_type == "audio":
		media = "_(audio_story)"
	elif media_type == "tv":
		media = "_(TV_story)"
	elif media_type == "novel":
		media = "_(novel)"
	else:
		media = ""

	episode_formatted = smart_capitalize(name).replace(" ","_")
	print(episode_formatted)

	url = "https://tardis.wiki/wiki/" + episode_formatted + media

	try:
		
		# Send a GET request to the website
		response = requests.get(url)
		response.raise_for_status()  # Raise an error for bad status codes

		# Access the content of the response
		soup = BeautifulSoup(response.text, 'html.parser')
		season = parts = ''
		doctor = main_character = companions = featuring = enemy = writer = director = ''
		
		for item in soup.select('div.pi-item'): # a for loop that runs through at elements in the table
			label = item.select_one('h3.pi-data-label')

			value_element = item.select_one('div.pi-data-value')
			
			if not label or not value_element:
				continue

			label_text = label.text.strip()

			# Extract values
			values = [a.text.strip() for a in value_element.select('a')] or [value_element.text.strip()]

			if 'Number of parts:' in label_text:
				parts = value_element.text.strip()

			elif 'Doctor:' in label_text:
				doctor = values

			elif 'Main character' in label_text:
				main_character = values

			elif 'Companion' in label_text:
				companions = values

			elif 'Featuring' in label_text:
				featuring = values

			elif 'Main enemy' in label_text:
				enemy = values

			elif 'Writers' in label_text or 'Writer' in label_text:
				writer = values

			elif 'Director' in label_text:
				director = values

			elif 'Part of' in label_text:
				season = values
		
		# Apply doctor converter
		doctor = doctorconverter(doctor)
		featuring = doctorconverter(featuring)


		if not any([season, parts, doctor, main_character, companions, featuring, enemy, writer, director]):
			raise KeyError("No valid data found on the page.")
		else:
			return season,parts,doctor,main_character,companions,featuring,enemy,writer,director

	except requests.exceptions.RequestException as e:
		#print(f"An error occurred: {e}")
		return ('N/A',)*9  # Return a default tuple
	
	except KeyError as e:
		print(f"Data missing: {e}")
		return ('N/A',)*9 