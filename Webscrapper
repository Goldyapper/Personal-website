def fetch_data(name):
    # URL of the website to fetch data from
    url = "https://tardis.wiki/wiki/" + name + "_(audio_story)"

    try:
		
        # Send a GET request to the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Access the content of the response
        soup = BeautifulSoup(response.text, 'html.parser')
        season = parts = doctor = main_character = companions = featuring = enemy = writer = director = ''
		
        for item in soup.select('div.pi-item'): # a for loop that runs through at elements in the table
            label = item.select_one('h3.pi-data-label')
            #print(label)
            #Parts Data retrival
            if label and 'Number of parts:' in label.text:
                value = item.select_one('div.pi-data-value')
                if value:
                    parts = value.text.strip()
            
            #Doctor Data retrival
            if label and 'Doctor:' in label.text:
                values = item.select('div.pi-data-value a')
                doctor = [d.text for d in values]
				
            #Main character Data retrival
            if label and 'Main character(s):' in label.text:
                values = item.select('div.pi-data-value a')
                main_character = [m.text for m in values]

            #companion retrival    
            if label and 'Companion(s):' in label.text:
                values = item.select('div.pi-data-value a')
                companions = [c.text for c in values]
            
            #Featuring retrival    
            if label and 'Featuring' in label.text:
                values = item.select('div.pi-data-value a')
                featuring = [f.text for f in values]
			
            #Enemy retrival
            if label and 'Main enemy' in label.text:
                values = item.select('div.pi-data-value a')
                enemy = [e.text for e in values]
			
            #Writers Retrival
            if label and 'Writers'  in label.text:
                values = item.select('div.pi-data-value a')
                writer = [w.text for w in values]
			
			#Writer Retrival
            if label and 'Writer'  in label.text:
                values = item.select('div.pi-data-value a')
                writer = [w.text for w in values]
			
            #Director Retrival
            if label and 'Director' in label.text:
                values = item.select('div.pi-data-value a')
                director = [d.text for d in values]
			
            #Season Retrival
            if label and 'Part of' in label.text:
                values = item.select('div.pi-data-value a')
                season = [s.text for s in values]
				
        
        if season and parts and doctor and main_character and companions and featuring and enemy and writer and director == '':
            return KeyError
        else:
            return season, parts,doctor,main_character,companions,featuring,enemy,writer,director

    except requests.exceptions.RequestException as e:
        #print(f"An error occurred: {e}")
        return ('N/A',)*9  # Return a default tuple
	
def doctorconverter(doctor,featuring):
	doctor_number_map = {
	'Fugitive Doctor': 'Fugutive Dr',
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
	for doctors in doctor:
		doctor = [doctor_number_map.get(d, d) for d in doctor]
	
	for doctors in featuring:
		featuring = [doctor_number_map.get(d, d) for d in featuring]
	
	return doctor,featuring