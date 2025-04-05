import requests
import string
from bs4 import BeautifulSoup
import RAKE


# Function to fetch recipe from the Terraria Wiki
def fetch_recipe(recipe_name):
  url = f"https://terraria.wiki.gg/wiki/{recipe_name}"
  response = requests.get(url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the ingredient list
    ingredient_list = soup.find('tr', {'data-rowid': '1'})
    if ingredient_list:
      items = []

      # Find the <td> tag with class 'ingredients' within the <tr> tag
      ingredient_td = ingredient_list.find('td', class_='ingredients')

      if ingredient_td:
        # Extract item names and amounts
        # find all <a> tags within the <td> tag
        ingredient_items = ingredient_td.find_all('a')[1::2]
        # grab <a> elements
        for item in ingredient_items:
          item_title = item.get_text()
          amount_element = item.find_next('span', class_='am')
          if amount_element:
            amount = amount_element.get_text()
          else:
            amount = "1"
            # Concatenate item name and amount
          items.append(f"{item_title} x {amount}")

      # Find the crafting stations
      station_td = soup.find('td', class_='station')
      station_element = station_td.find('a')
      stations = station_element.get('title') if station_element else "Unknown"

      return {"Items": items, "Crafting Station": stations, "URL": url}

    else:
      return "Item is not craftable."
  else:
    return "Failed to fetch recipe."

def format_keyword(keywords):
  if isinstance(keywords, str):
    recipe_name = keywords
  else:
    # Extract the first element of each tuple and join them
    recipe_name = " ".join(keyword[0] for keyword in keywords)

  # Capitalize the first letter of each word
  recipe_name = string.capwords(recipe_name)

  # Replace spaces with underscores
  recipe_name = recipe_name.replace(" ", "_")

  return recipe_name


# RAKE keyword extraction
def item_extract(text_input):
  #stop words that will not be added to keywords
  stop_link = "simple_stopwords.txt"

  # add rake object
  rake_object = RAKE.Rake(stop_link)

  # use rake object to check for keywords in userinput
  keywords = rake_object.run(text_input,
                             minCharacters=5,
                             maxWords=5,
                             minFrequency=1)

  #send keywords to be formatted
  recipe_name = format_keyword(keywords)

  #with the formatted recipe name attempt to find recipe
  recipe_details = fetch_recipe(recipe_name)

  # retrun the result of findings
  return recipe_details


# Command-line chatbot interface
def chatbot(user_input):
  recipe_details = item_extract(user_input)
  
  if isinstance(recipe_details, str):
    response = ""
    #suggested = suggest_item(user_input)
    response += recipe_details
    #response += suggested
    return response
  else:
    response = "Items:\n"
    for i in range(len(recipe_details['Items'])):
      response += f"{recipe_details['Items'][i]}\n"
    response += f"Crafting Stations: {recipe_details['Crafting Station']}\n"
    response += f"Link to Recipe: {recipe_details['URL']}"
    return response
