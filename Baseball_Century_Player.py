#%%
# Import Libraries
import pandas as pd
from pandas.errors import EmptyDataError
import time
import uuid
import math
from random import sample
from selenium import webdriver
from selenium.webdriver.common.by import By

def Click_Button(elem_str):
    time.sleep(1)
    elem = DRIVER.find_element(By.NAME, elem_str)
    DRIVER.execute_script("arguments[0].scrollIntoView()", elem)
    elem.click()

def Find_Batter_Info(web_elem):
    b_info = web_elem.find_elements(By.XPATH, './child::*')[0].text
    b_attrs = web_elem.find_elements(By.XPATH, './child::*')[1].text
    name = b_info.split('\n')[0]
    age = int(b_info.split('\n')[-1].split(' ')[-1])
    contact = int(b_attrs.split('\n')[0].split(' ')[-1])
    power = int(b_attrs.split('\n')[1].split(' ')[-1])
    total = contact + power
    ab = int(b_attrs.split('\n')[3].split(' ')[-1])
    h = int(b_attrs.split('\n')[4].split(' ')[-1])
    hr = int(b_attrs.split('\n')[5].split(' ')[-1])

    return [name, 'B', age, contact, power, total, ab, h, hr]

def Find_Pitcher_Info(web_elem):
    p_info = web_elem.find_elements(By.XPATH, './child::*')[0].text
    p_attrs = web_elem.find_elements(By.XPATH, './child::*')[1].text
    name = p_info.split('\n')[0]
    age = int(p_info.split('\n')[-1].split(' ')[-1])
    stamina = int(p_attrs.split('\n')[0].split(' ')[-1])
    stuff = int(p_attrs.split('\n')[1].split(' ')[-1])
    total = stamina + stuff
    w = int(p_attrs.split('\n')[3].split(' ')[-1].split('-')[0])
    l = int(p_attrs.split('\n')[3].split(' ')[-1].split('-')[1])

    return [name, 'P', age, stamina, stuff, total, w, l]

#%%
# Load Batter and Pitcher DataFrames
try:
    bdf = pd.read_csv('CSVs\Batter_DataFrame.csv', index_col=0)
except EmptyDataError:
    bdf = pd.DataFrame(columns=['Sim_ID','Season','Name','Pos','Age','Contact','Power','Total','AB','H','HR'])

try:
    pdf = pd.read_csv('CSVs\Pitcher_DataFrame.csv', index_col=0)
except EmptyDataError:
    pdf = pd.DataFrame(columns=['Sim_ID','Season','Name','Pos','Age','Stamina','Stuff','Total','W','L'])    

try:
    tmdf = pd.read_csv('CSVs\Team_DataFrame.csv', index_col=0)
except EmptyDataError:
    tmdf = pd.DataFrame(columns=['Sim_ID','Season','W','L','Finish','GB'])

#%%
# Create Unique Sim ID
simid = int(math.log(uuid.uuid1().int)*1000)

#%%
# Initialize Web Driver and Data Frames
DRIVER = webdriver.Chrome()

#%%
# Go to Baseball Century Game
DRIVER.get('https://www.baseballcentury.com')

#%%
# Click through initial game setup
DRIVER.find_elements(By.NAME, 'selectteam')[0].click()
Click_Button('getmanager')
Click_Button('pickteam')
Click_Button('springtraining')

#%%
# Simulate 151 Seasons (MAX ALLOWED)
for szn in range(151):
    # Get the Player Checkboxes for current players on the roster
    # and the new Players that are available to be part of the
    # roster during spring training
    player_checkboxes = []
    for x in range(1,13,1):
        player_checkboxes.append(DRIVER.find_element(By.NAME, f'checkbox{x}'))
    b_check = [player_checkboxes[0], player_checkboxes[1], player_checkboxes[2],
                player_checkboxes[3], player_checkboxes[4], player_checkboxes[9],
                player_checkboxes[10]]
    p_check = [player_checkboxes[5], player_checkboxes[6], player_checkboxes[7],
                player_checkboxes[8], player_checkboxes[11]]

    DRIVER.execute_script("arguments[0].scrollIntoView()", player_checkboxes[11])

    # Randomly Choose the 5 batters and 4 pitchers to be on the roster for the season
    b_chc = sample(range(7), 5)
    p_chc = sample(range(5), 4)

    for y in range(7):
        if (y in b_chc and not b_check[y].is_selected()) or (y not in b_chc and b_check[y].is_selected()):
            b_check[y].click()

    for z in range(5):
        if (z in p_chc and not p_check[z].is_selected()) or (z not in p_chc and p_check[z].is_selected()):
            p_check[z].click()

    time.sleep(0.5)

    Click_Button('finalroster')

    time.sleep(1)
    season = int(DRIVER.find_element(By.NAME, 'weekpreview').get_attribute('value').split(' ')[-2])

    # Sim Through the 5 months of the season
    for times in range(5):
        Click_Button('weekpreview')
        Click_Button('weekplay')

    # Retrieve Batter and Pitcher Stats and Info
    batter_elems = []
    for x in range(1,6,1):
        batter_elems.append(DRIVER.find_element(By.XPATH, f'/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/form/p[5]/table/tbody/tr/td[{x}]/div/div'))

    for batter in batter_elems:
        batter_info = [simid, season] + Find_Batter_Info(batter)
        bdf.loc[len(bdf)] = batter_info

    pitcher_elems = []
    for x in range(1,5,1):
        pitcher_elems.append(DRIVER.find_element(By.XPATH, f'/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/form/p[6]/table/tbody/tr/td[{x}]/div/div'))

    for pitcher in pitcher_elems:
        pitcher_info = [simid, season] + Find_Pitcher_Info(pitcher)
        pdf.loc[len(pdf)] = pitcher_info

    Click_Button('seasonover')

    # Retrieve Team Stats and Info
    finish = int(DRIVER.find_element(By.NAME, f'teamfinish_reg{szn+1}').get_attribute("value"))
    tm_stats = DRIVER.find_element(By.XPATH, f'/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/form/table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr[{finish+1}]').text
    tm_win = tm_stats.split(' ')[1]
    tm_loss = tm_stats.split(' ')[2]
    tm_gb = tm_stats.split(' ')[3]
    tmdf.loc[len(tmdf)] = [simid, season, tm_win, tm_loss, finish, tm_gb]

    Click_Button('seeregister')
    Click_Button('newseason')
#%%
# Exit Driver
DRIVER.quit()

#%%
# Save to CSV files
bdf.to_csv('CSVs\Batter_DataFrame.csv')
pdf.to_csv('CSVs\Pitcher_DataFrame.csv')
tmdf.to_csv('CSVs\Team_DataFrame.csv')

# %%