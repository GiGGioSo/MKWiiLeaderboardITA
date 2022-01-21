import requests
import json
import gspread
from gspread.utils import rowcol_to_a1
import datetime
import time

# Google Sheet : https://docs.google.com/spreadsheets/d/19qNyxZstZ2htq48dLRoupDBu74ZJOFw66vb8RXhN6XE/edit#gid=583825868

start_time = time.time()
last_checkpoint = start_time

TIME_WAIT_AFTER_GET = 1
TIME_WAIT_AFTER_HEAD = 1/10
TIME_WAIT_AFTER_GS = 1/5
TIME_WAIT_PRINT_REQUESTS = 1
NUMBER_OF_REQUESTS = 0
TOTAL_REQUESTS = 0

RTs = [ "1AE1A7D894960B38E09E7494373378D87305A163", 
        "90720A7D57A7C76E2347782F6BDE5D22342FB7DD", 
        "0E380357AFFCFD8722329994885699D9927F8276", 
        "1896AEA49617A571C66FF778D8F2ABBE9E5D7479", 
        "7752BB51EDBC4A95377C0A05B0E0DA1503786625", 
        "E4BF364CB0C5899907585D731621CA930A4EF85C", 
        "B02ED72E00B400647BDA6845BE387C47D251F9D1", 
        "D1A453B43D6920A78565E65A4597E353B177ABD0", 
        "72D0241C75BE4A5EBD242B9D8D89B1D6FD56BE8F", 
        "52F01AE3AED1E0FA4C7459A648494863E83A548C", 
        "48EBD9D64413C2B98D2B92E5EFC9B15ECD76FEE6", 
        "ACC0883AE0CE7879C6EFBA20CFE5B5909BF7841B", 
        "38486C4F706395772BD988C1AC5FA30D27CAE098", 
        "B13C515475D7DA207DFD5BADD886986147B906FF", 
        "B9821B14A89381F9C015669353CB24D7DB1BB25D", 
        "FFE518915E5FAAA889057C8A3D3E439868574508", 
        "8014488A60F4428EEF52D01F8C5861CA9565E1CA", 
        "8C854B087417A92425110CC71E23C944D6997806", 
        "071D697C4DDB66D3B210F36C7BF878502E79845B", 
        "49514E8F74FEA50E77273C0297086D67E58123E8", 
        "BA9BCFB3731A6CB17DBA219A8D37EA4D52332256", 
        "E8ED31605CC7D6660691998F024EED6BA8B4A33F", 
        "BC038E163D21D9A1181B60CF90B4D03EFAD9E0C5", 
        "418099824AF6BF1CD7F8BB44F61E3A9CC3007DAE", 
        "4EC538065FDC8ACF49674300CBDEC5B80CC05A0D",
        "A4BEA41BE83D816F793F3FAD97D268F71AD99BF9",
        "692D566B05434D8C66A55BDFF486698E0FC96095",
        "1941A29AD2E7B7BBA8A29E6440C95EF5CF76B01D", 
        "077111B996E5C4F47D20EC29C2938504B53A8E76", 
        "F9A62BEF04CC8F499633E4023ACC7675A92771F0", 
        "B036864CF0016BE0581449EF29FB52B2E58D78A4", 
        "15B303B288F4707E5D0AF28367C8CE51CDEAB490"]
TRACK_INDEXES = {
    'Circuito di Luigi': [6, "1AE1A7D894960B38E09E7494373378D87305A163"],
    'Prateria verde': [14, "90720A7D57A7C76E2347782F6BDE5D22342FB7DD"],
    'Gola Fungo': [22, "0E380357AFFCFD8722329994885699D9927F8276"],
    'Gola Fungo (glitch)': [30, "0E380357AFFCFD8722329994885699D9927F8276"], 
    'Fabbrica di Toad': [38, "1896AEA49617A571C66FF778D8F2ABBE9E5D7479"],
    'Fabbrica di Toad (SC)': [46, "1896AEA49617A571C66FF778D8F2ABBE9E5D7479"], 
    'Circuito di Mario': [54, "7752BB51EDBC4A95377C0A05B0E0DA1503786625"], 
    'Circuito di Mario (glitch)': [62, "7752BB51EDBC4A95377C0A05B0E0DA1503786625"], 
    'Outlet Cocco': [70, "E4BF364CB0C5899907585D731621CA930A4EF85C"],
    'Outlet Cocco (SC)': [78, "E4BF364CB0C5899907585D731621CA930A4EF85C"], 
    'Outlet Cocco (glitch)': [86, "E4BF364CB0C5899907585D731621CA930A4EF85C"], 
    'Pista snowboard DK': [94, "B02ED72E00B400647BDA6845BE387C47D251F9D1"], 
    "Miniera d'oro di Wario": [102, "D1A453B43D6920A78565E65A4597E353B177ABD0"], 
    "Miniera d'oro di Wario (glitch)": [110, "D1A453B43D6920A78565E65A4597E353B177ABD0"], 
    'Circuito di Daisy': [118, "72D0241C75BE4A5EBD242B9D8D89B1D6FD56BE8F"], 
    'Punta Koopa': [126, "52F01AE3AED1E0FA4C7459A648494863E83A548C"],
    'Punta Koopa (glitch)': [134, "52F01AE3AED1E0FA4C7459A648494863E83A548C"],
    'Pista degli aceri': [142, "48EBD9D64413C2B98D2B92E5EFC9B15ECD76FEE6"], 
    'Pista degli aceri (glitch)': [150, "48EBD9D64413C2B98D2B92E5EFC9B15ECD76FEE6"],
    'Vulcano brontolone': [158, "ACC0883AE0CE7879C6EFBA20CFE5B5909BF7841B"], 
    'Vulcano brontolone (SC)': [166, "ACC0883AE0CE7879C6EFBA20CFE5B5909BF7841B"], 
    'Vulcano brontolone (glitch)': [174, "ACC0883AE0CE7879C6EFBA20CFE5B5909BF7841B"],
    'Rovine desertiche': [182, "38486C4F706395772BD988C1AC5FA30D27CAE098"],
    'Autostrada lunare': [190, "B13C515475D7DA207DFD5BADD886986147B906FF"], 
    'Castello di Bowser': [198, "B9821B14A89381F9C015669353CB24D7DB1BB25D"], 
    'Castello di Bowser (SC)': [206, "B9821B14A89381F9C015669353CB24D7DB1BB25D"],
    'Pista Arcobaleno': [214, "FFE518915E5FAAA889057C8A3D3E439868574508"], 
    'Pista Arcobaleno (glitch)': [222, "FFE518915E5FAAA889057C8A3D3E439868574508"], 
    'GCN Spiaggia di Peach': [230, "8014488A60F4428EEF52D01F8C5861CA9565E1CA"], 
    'GCN Spiaggia di Peach (glitch)': [238, "8014488A60F4428EEF52D01F8C5861CA9565E1CA"], 
    'DS Cascate di Yoshi': [246, "8C854B087417A92425110CC71E23C944D6997806"], 
    'SNES Valle fantasma 2': [254, "071D697C4DDB66D3B210F36C7BF878502E79845B"],
    'SNES Valle fantasma 2 (glitch)': [262, "071D697C4DDB66D3B210F36C7BF878502E79845B"],
    'N64 Pista di Mario': [270, "49514E8F74FEA50E77273C0297086D67E58123E8"], 
    'N64 Circuito gelato': [278, "BA9BCFB3731A6CB17DBA219A8D37EA4D52332256"], 
    'N64 Circuito gelato (glitch)': [286, "BA9BCFB3731A6CB17DBA219A8D37EA4D52332256"], 
    'GBA Spiaggia Tipo Timido': [294, "E8ED31605CC7D6660691998F024EED6BA8B4A33F"], 
    'DS Borgo Delfino': [302, "BC038E163D21D9A1181B60CF90B4D03EFAD9E0C5"],
    'GCN Stadio di Waluigi': [310, "418099824AF6BF1CD7F8BB44F61E3A9CC3007DAE"], 
    'GCN Stadio di Waluigi (glitch)': [318, "418099824AF6BF1CD7F8BB44F61E3A9CC3007DAE"],
    'DS Deserto Picchiasol': [326, "4EC538065FDC8ACF49674300CBDEC5B80CC05A0D"],
    'DS Deserto Picchiasol (SC)': [334, "4EC538065FDC8ACF49674300CBDEC5B80CC05A0D"],
    'GBA Castello di Bowser 3': [342, "A4BEA41BE83D816F793F3FAD97D268F71AD99BF9"], 
    'GBA Castello di Bowser 3 (SC)': [350, "A4BEA41BE83D816F793F3FAD97D268F71AD99BF9"], 
    'N64 Viale Giungla DK': [358, "692D566B05434D8C66A55BDFF486698E0FC96095"], 
    'N64 Viale Giungla DK (glitch)': [366, "692D566B05434D8C66A55BDFF486698E0FC96095"], 
    'GCN Circuito di Mario': [374, "1941A29AD2E7B7BBA8A29E6440C95EF5CF76B01D"], 
    'SNES Circuito di Mario 3': [382, "077111B996E5C4F47D20EC29C2938504B53A8E76"], 
    'DS Giardino di Peach': [390, "F9A62BEF04CC8F499633E4023ACC7675A92771F0"], 
    'GCN Montagne di DK': [398, "B036864CF0016BE0581449EF29FB52B2E58D78A4"], 
    'GCN Montagne di DK (SC)': [406, "B036864CF0016BE0581449EF29FB52B2E58D78A4"], 
    'N64 Castello di Bowser': [414, "15B303B288F4707E5D0AF28367C8CE51CDEAB490"], 
    'N64 Castello di Bowser (glitch)': [422, "15B303B288F4707E5D0AF28367C8CE51CDEAB490"]
    }

base_url = "https://tt.chadsoft.co.uk/"
modifiers_url = "?times=pb" #To get only the PBs
sa = gspread.service_account(filename="account_service_ghosts.json")
sh = sa.open("Cose Per Automatizzare Tempi TT")
wks = sh.worksheet("ProvaDatabase")
print("SUCCESSFULLY CONNECTED TO GOOGLE SHEETS IN %.2f SECONDS" % (time.time() - start_time))
NUMBER_OF_REQUESTS += 3

def head_chadsoftAPI_request(ID):
    player_url = "players/" + ID[:2] + "/" + ID[2:] + ".json" #API structure to get Player info
    final_url = base_url + player_url + modifiers_url
    r = requests.head(final_url)
    time.sleep(TIME_WAIT_AFTER_HEAD)
    return r.headers

def get_chadsoftAPI_request(ID):
    player_url = "players/" + ID[:2] + "/" + ID[2:] + ".json" #API structure to get Player info
    final_url = base_url + player_url + modifiers_url
    r = requests.get(final_url)
    time.sleep(TIME_WAIT_AFTER_GET)
    return r.text

def cd_get_last_modified(ID):
    return get_datetime_from_cd_date(head_chadsoftAPI_request(ID)["Last-Modified"])

def get_datetime_from_cd_date(cd_date):
    cd_date = cd_date.split()
    hr_raw = [int(x) for x in cd_date[4].split(":")]
    if cd_date[2] == "Jan":
        cd_date[2] = 1
    elif cd_date[2] == "Feb":
        cd_date[2] = 2
    elif cd_date[2] == "Mar":
        cd_date[2] = 3
    elif cd_date[2] == "Apr":
        cd_date[2] = 4
    elif cd_date[2] == "May":
        cd_date[2] = 5
    elif cd_date[2] == "Jun":
        cd_date[2] = 6
    elif cd_date[2] == "Jul":
        cd_date[2] = 7
    elif cd_date[2] == "Aug":
        cd_date[2] = 8
    elif cd_date[2] == "Sep":
        cd_date[2] = 9
    elif cd_date[2] == "Oct":
        cd_date[2] = 10
    elif cd_date[2] == "Nov":
        cd_date[2] = 11
    elif cd_date[2] == "Dec":
        cd_date[2] = 12
    else:
        print("[ERROR] '"+cd_date[2]+"' is an invalid month")

    return datetime.datetime(int(cd_date[3]), cd_date[2], int(cd_date[1]), hr_raw[0], hr_raw[1], hr_raw[2])

def gs_get_last_modified_s():
    global NUMBER_OF_REQUESTS
    NUMBER_OF_REQUESTS += 1
    end_LMs = wks.find("END_OF_LMs")
    time.sleep(TIME_WAIT_AFTER_GS)
    NUMBER_OF_REQUESTS += 1
    values = wks.get('B3:C'+str(end_LMs.row-1))
    time.sleep(TIME_WAIT_AFTER_GS)
    for l in values:
        if len(l) == 1:
            l.append('NO_DATE')
    return values

# Deprecated
def gs_get_cell_value(row, column):
    global NUMBER_OF_REQUESTS
    NUMBER_OF_REQUESTS += 1
    time.sleep(TIME_WAIT_AFTER_GS)
    value = wks.cell(row, column).value
    if value == None:
        return ''
    else:
        return value

def gs_get_row_values(row):
    global NUMBER_OF_REQUESTS
    NUMBER_OF_REQUESTS += 1
    time.sleep(TIME_WAIT_AFTER_GS)
    return wks.row_values(row)

def gs_set_new_ghost(row, column, time_, date, split, ghost, vehicleId, driverId, controller):
    global NUMBER_OF_REQUESTS
    NUMBER_OF_REQUESTS += 1
    time.sleep(TIME_WAIT_AFTER_GS*2)
    range = rowcol_to_a1(row, column) + ':' + rowcol_to_a1(row, column+6)
    ghost = get_ghost_link(ghost)
    time_ = str(time_)
    
    wks.update(range, [[time_, date, split, ghost, get_vehicle(vehicleId), get_driver(driverId), get_controller(controller)]])

def get_ghost_link(ghost):
    ghost = "https://www.chadsoft.co.uk/time-trials" + ghost[:-3] + "html"
    return ghost

def get_vehicle(ID):
    if ID == 0: 
        return "Standard Kart S"  
    if ID == 1: 
        return "Standard Kart M"  
    if ID == 2: 
        return "Standard Kart L"  
    if ID == 3: 
        return "Booster Seat"  
    if ID == 4: 
        return "Classic Dragster"  
    if ID == 5: 
        return "Offroader"  
    if ID == 6: 
        return "Mini Beast"  
    if ID == 7: 
        return "Wild Wing"  
    if ID == 8: 
        return "Flame Flyer"  
    if ID == 9: 
        return "Cheep Charger"  
    if ID == 10: 
        return "Super Blooper"  
    if ID == 11: 
        return "Piranha Prowler"  
    if ID == 12: 
        return "Tiny Titan"  
    if ID == 13: 
        return "Daytripper"  
    if ID == 14: 
        return "Jetsetter"  
    if ID == 15: 
        return "Blue Falcon"  
    if ID == 16: 
        return "Sprinter"  
    if ID == 17: 
        return "Honeycoupe"  
    if ID == 18: 
        return "Standard Bike S"  
    if ID == 19: 
        return "Standard Bike M"  
    if ID == 20: 
        return "Standard Bike L"  
    if ID == 21: 
        return "Bullet Bike"  
    if ID == 22: 
        return "Mach Bike"  
    if ID == 23: 
        return "Flame Runner"  
    if ID == 24: 
        return "Bit Bike"  
    if ID == 25: 
        return "Sugarscoot"  
    if ID == 26: 
        return "Wario Bike"  
    if ID == 27: 
        return "Quacker"  
    if ID == 28: 
        return "Zip Zip"  
    if ID == 29: 
        return "Shooting Star"  
    if ID == 30: 
        return "Magikruiser"  
    if ID == 31: 
        return "Sneakster"  
    if ID == 32: 
        return "Spear"  
    if ID == 33: 
        return "Jet Bubble"  
    if ID == 34: 
        return "Dolphin Dasher"  
    if ID == 35: 
        return "Phantom"  
    else: 
        return "" 

def get_driver(ID):
    if ID == 0: 
        return "Mario"
    if ID == 1: 
        return "Baby Peach"
    if ID == 2: 
        return "Waluigi"
    if ID == 3: 
        return "Bowser"
    if ID == 4: 
        return "Baby Daisy"
    if ID == 5: 
        return "Dry Bones"
    if ID == 6: 
        return "Baby Mario"
    if ID == 7: 
        return "Luigi"
    if ID == 8: 
        return "Toad"
    if ID == 9: 
        return "Donkey Kong"
    if ID == 10: 
        return "Yoshi"
    if ID == 11: 
        return "Wario"
    if ID == 12: 
        return "Baby Luigi"
    if ID == 13: 
        return "Toadette"
    if ID == 14: 
        return "Koopa"
    if ID == 15: 
        return "Daisy"
    if ID == 16: 
        return "Peach"
    if ID == 17: 
        return "Birdo"
    if ID == 18: 
        return "Diddy Kong"
    if ID == 19: 
        return "King Boo"
    if ID == 20: 
        return "Bowser Jr."
    if ID == 21: 
        return "Dry Bowser"
    if ID == 22: 
        return "Funky Kong"
    if ID == 23: 
        return "Rosalina"
    if ID == 24: 
        return "Small Mii A Male"
    if ID == 25: 
        return "Small Mii A Female"
    if ID == 26: 
        return "Small Mii B Male"
    if ID == 27: 
        return "Small Mii B Female"
    if ID == 30: 
        return "Medium Mii A Male"
    if ID == 31: 
        return "Medium Mii A Female"
    if ID == 32: 
        return "Medium Mii B Male"
    if ID == 33: 
        return "Medium Mii B Female"
    if ID == 36: 
        return "Large Mii A Male"
    if ID == 37: 
        return "Large Mii A Female"
    if ID == 38: 
        return "Large Mii B Male"
    if ID == 39: 
        return "Large Mii B Female"
    else: 
        return ""

def get_controller(ID):
    if ID == 0: 
        return "Wii Wheel" 
    if ID == 1: 
        return "Nunchuk" 
    if ID == 2: 
        return "Classic"
    if ID == 3: 
        return "GameCube"
    if ID == 15: 
        return "???" 
    else: 
        return ""

def get_index_of_track(ID, categoryId):
    if   ID == TRACK_INDEXES["Circuito di Luigi"][1]:
        return TRACK_INDEXES["Circuito di Luigi"][0]
    elif ID == TRACK_INDEXES["Prateria verde"][1]:
        return TRACK_INDEXES["Prateria verde"][0]
    elif ID == TRACK_INDEXES["Gola Fungo"][1] and (categoryId == 2 or categoryId == 16):
        return TRACK_INDEXES["Gola Fungo"][0]
    elif ID == TRACK_INDEXES["Gola Fungo (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Gola Fungo (glitch)"][0]
    elif ID == TRACK_INDEXES["Fabbrica di Toad"][1] and categoryId == 2:
        return TRACK_INDEXES["Fabbrica di Toad"][0]
    elif ID == TRACK_INDEXES["Fabbrica di Toad (SC)"][1] and categoryId == 16:
        return TRACK_INDEXES["Fabbrica di Toad (SC)"][0]
    elif ID == TRACK_INDEXES["Circuito di Mario"][1] and categoryId == 0:
        return TRACK_INDEXES["Circuito di Mario"][0]
    elif ID == TRACK_INDEXES["Circuito di Mario (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Circuito di Mario (glitch)"][0]
    elif ID == TRACK_INDEXES["Outlet Cocco"][1] and categoryId == 2:
        return TRACK_INDEXES["Outlet Cocco"][0]
    elif ID == TRACK_INDEXES["Outlet Cocco (SC)"][1] and categoryId == 16:
        return TRACK_INDEXES["Outlet Cocco (SC)"][0]
    elif ID == TRACK_INDEXES["Outlet Cocco (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Outlet Cocco (glitch)"][0]
    elif ID == TRACK_INDEXES["Pista snowboard DK"][1]:
        return TRACK_INDEXES["Pista snowboard DK"][0]
    elif ID == TRACK_INDEXES["Miniera d'oro di Wario"][1] and categoryId == 0:
        return TRACK_INDEXES["Miniera d'oro di Wario"][0]
    elif ID == TRACK_INDEXES["Miniera d'oro di Wario (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Miniera d'oro di Wario (glitch)"][0]
    elif ID == TRACK_INDEXES["Circuito di Daisy"][1]:
        return TRACK_INDEXES["Circuito di Daisy"][0]
    elif ID == TRACK_INDEXES["Punta Koopa"][1] and categoryId == 0:
        return TRACK_INDEXES["Punta Koopa"][0]
    elif ID == TRACK_INDEXES["Punta Koopa (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Punta Koopa (glitch)"][0]
    elif ID == TRACK_INDEXES["Pista degli aceri"][1] and categoryId == 0:
        return TRACK_INDEXES["Pista degli aceri"][0]
    elif ID == TRACK_INDEXES["Pista degli aceri (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Pista degli aceri (glitch)"][0]
    elif ID == TRACK_INDEXES["Vulcano brontolone"][1] and categoryId == 2:
        return TRACK_INDEXES["Vulcano brontolone"][0]
    elif ID == TRACK_INDEXES["Vulcano brontolone (SC)"][1] and categoryId == 16:
        return TRACK_INDEXES["Vulcano brontolone (SC)"][0]
    elif ID == TRACK_INDEXES["Vulcano brontolone (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Vulcano brontolone (glitch)"][0]
    elif ID == TRACK_INDEXES["Rovine desertiche"][1]:
        return TRACK_INDEXES["Rovine desertiche"][0]
    elif ID == TRACK_INDEXES["Autostrada lunare"][1]:
        return TRACK_INDEXES["Autostrada lunare"][0]
    elif ID == TRACK_INDEXES["Castello di Bowser"][1] and categoryId == 2:
        return TRACK_INDEXES["Castello di Bowser"][0]
    elif ID == TRACK_INDEXES["Castello di Bowser (SC)"][1] and categoryId == 16:
        return TRACK_INDEXES["Castello di Bowser (SC)"][0]
    elif ID == TRACK_INDEXES["Pista Arcobaleno"][1] and categoryId == 0:
        return TRACK_INDEXES["Pista Arcobaleno"][0]
    elif ID == TRACK_INDEXES["Pista Arcobaleno (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["Pista Arcobaleno (glitch)"][0]
    elif ID == TRACK_INDEXES["GCN Spiaggia di Peach"][1] and categoryId == 0:
        return TRACK_INDEXES["GCN Spiaggia di Peach"][0]
    elif ID == TRACK_INDEXES["GCN Spiaggia di Peach (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["GCN Spiaggia di Peach (glitch)"][0]
    elif ID == TRACK_INDEXES["DS Cascate di Yoshi"][1]:
        return TRACK_INDEXES["DS Cascate di Yoshi"][0]
    elif ID == TRACK_INDEXES["SNES Valle fantasma 2"][1] and categoryId == 0:
        return TRACK_INDEXES["SNES Valle fantasma 2"][0]
    elif ID == TRACK_INDEXES["SNES Valle fantasma 2 (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["SNES Valle fantasma 2 (glitch)"][0]
    elif ID == TRACK_INDEXES["N64 Pista di Mario"][1]:
        return TRACK_INDEXES["N64 Pista di Mario"][0]
    elif ID == TRACK_INDEXES["N64 Circuito gelato"][1] and categoryId == 0:
        return TRACK_INDEXES["N64 Circuito gelato"][0]
    elif ID == TRACK_INDEXES["N64 Circuito gelato (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["N64 Circuito gelato (glitch)"][0]
    elif ID == TRACK_INDEXES["GBA Spiaggia Tipo Timido"][1] and categoryId == 0:
        return TRACK_INDEXES["GBA Spiaggia Tipo Timido"][0]
    elif ID == TRACK_INDEXES["DS Borgo Delfino"][1]:
        return TRACK_INDEXES["DS Borgo Delfino"][0]
    elif ID == TRACK_INDEXES["GCN Stadio di Waluigi"][1] and categoryId == 0:
        return TRACK_INDEXES["GCN Stadio di Waluigi"][0]
    elif ID == TRACK_INDEXES["GCN Stadio di Waluigi (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["GCN Stadio di Waluigi (glitch)"][0]
    elif ID == TRACK_INDEXES["DS Deserto Picchiasol"][1] and categoryId == 2:
        return TRACK_INDEXES["DS Deserto Picchiasol"][0]
    elif ID == TRACK_INDEXES["DS Deserto Picchiasol (SC)"][1] and categoryId == 16:
        return TRACK_INDEXES["DS Deserto Picchiasol (SC)"][0]
    elif ID == TRACK_INDEXES["GBA Castello di Bowser 3"][1] and categoryId == 2:
        return TRACK_INDEXES["GBA Castello di Bowser 3"][0]
    elif ID == TRACK_INDEXES["GBA Castello di Bowser 3 (SC)"][1] and categoryId == 16:
        return TRACK_INDEXES["GBA Castello di Bowser 3 (SC)"][0]
    elif ID == TRACK_INDEXES["N64 Viale Giungla DK"][1] and (categoryId == 2 or categoryId == 16):
        return TRACK_INDEXES["N64 Viale Giungla DK"][0]
    elif ID == TRACK_INDEXES["N64 Viale Giungla DK (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["N64 Viale Giungla DK (glitch)"][0]
    elif ID == TRACK_INDEXES["GCN Circuito di Mario"][1] and categoryId == 0:
        return TRACK_INDEXES["GCN Circuito di Mario"][0]
    elif ID == TRACK_INDEXES["SNES Circuito di Mario 3"][1]:
        return TRACK_INDEXES["SNES Circuito di Mario 3"][0]
    elif ID == TRACK_INDEXES["DS Giardino di Peach"][1]:
        return TRACK_INDEXES["DS Giardino di Peach"][0]
    elif ID == TRACK_INDEXES["GCN Montagne di DK"][1] and categoryId == 2:
        return TRACK_INDEXES["GCN Montagne di DK"][0]
    elif ID == TRACK_INDEXES["GCN Montagne di DK (SC)"][1] and categoryId == 16:
        return TRACK_INDEXES["GCN Montagne di DK (SC)"][0]
    elif ID == TRACK_INDEXES["N64 Castello di Bowser"][1] and categoryId == 2:
        return TRACK_INDEXES["N64 Castello di Bowser"][0]
    elif ID == TRACK_INDEXES["N64 Castello di Bowser"][1] and categoryId == 16:
        return "INVALID_TRACK_CATEGORY"   
    elif ID == TRACK_INDEXES["N64 Castello di Bowser (glitch)"][1] and categoryId == 1:
        return TRACK_INDEXES["N64 Castello di Bowser (glitch)"][0]
    else:
        print("[ERROR] ID:", ID, ", categoryID:", categoryId, "were not recognised")

def get_category(ID):
    if ID == -1 or ID == 0 or ID == 2:
        return "No-SC"
    elif ID == 1:
        return "Glitch"
    elif ID == 16:
        return "SC"
    else:
        return f"unknown{ID}"

def main():
    global last_checkpoint
    global TOTAL_REQUESTS
    global NUMBER_OF_REQUESTS
    global wks
    gs_LMs = dict(gs_get_last_modified_s())
    row = 3 #Current row
    for ID, LM in gs_LMs.items():
        # START DEBUG
        elapsed = time.time() - last_checkpoint
        if elapsed > 1:
            last_checkpoint = time.time()
            TOTAL_REQUESTS += NUMBER_OF_REQUESTS
            print("TOTAL REQUESTS:", TOTAL_REQUESTS, "IN %.2f" % (last_checkpoint-start_time) + ";   REQUESTS IN THE LAST %.2f" % elapsed, "SECOND/S:", NUMBER_OF_REQUESTS)
            NUMBER_OF_REQUESTS = 0
        # END DEBUG
        cd_LM = cd_get_last_modified(ID)
        print("[CHECKING] ID:", ID)
        if LM == 'NO_DATE' or datetime.datetime.fromisoformat(LM) < cd_LM:
            print("  [OUTDATED DATA FOUND] fetching player JSON from Chadsoft...")
            player_data = json.loads(get_chadsoftAPI_request(ID))
            ghosts = player_data["ghosts"]
            gs_row_values = gs_get_row_values(row)
            for g in ghosts:
                # START DEBUG
                elapsed = time.time() - last_checkpoint
                if elapsed > 1:
                    last_checkpoint = time.time()
                    TOTAL_REQUESTS += NUMBER_OF_REQUESTS
                    print("TOTAL REQUESTS:", TOTAL_REQUESTS, "IN %.2f" % (last_checkpoint-start_time) + ";   REQUESTS IN THE LAST %.2f" % elapsed, "SECOND/S:", NUMBER_OF_REQUESTS)
                    NUMBER_OF_REQUESTS = 0
                # END DEBUG
                if g["200cc"] == False and g["trackId"] in RTs:
                    trackId = g["trackId"]
                    new_time = g["finishTimeSimple"]
                    try:
                        categoryId = g["categoryId"]
                    except:
                        categoryId = -1
                    gs_track_column = get_index_of_track(trackId, categoryId)
                    if gs_track_column == "INVALID_TRACK_CATEGORY":
                        print("  [SKIPPING INVALID TRACK CATEGORY]", g["trackName"] + "; category:", get_category(categoryId))
                        continue
                    #old_time = gs_get_cell_value(row, gs_track_column) # Get all data the row data, then use the gs_track_column value to get the right one 
                    try:
                        old_time = gs_row_values[gs_track_column]
                    except IndexError:
                        old_time = ""
                    new_min = int(new_time.split(':')[0])
                    new_sec = int(new_time.split(':')[1].split('.')[0])
                    new_ms = int(new_time.split(':')[1].split('.')[1])
                    new_time = datetime.timedelta(minutes=new_min, seconds=new_sec, milliseconds=new_ms)
                    try:
                        old_min = int(old_time.split(':')[0])
                        old_sec = int(old_time.split(':')[1].split('.')[0])
                        old_ms = int(old_time.split(':')[1].split('.')[1])
                        old_time = datetime.timedelta(minutes=old_min, seconds=old_sec, milliseconds=old_ms)
                    except:
                        old_time = datetime.timedelta()
                    if old_time == datetime.timedelta() or new_time < old_time:
                        new_time = str(new_time).split(':')[1:]
                        if len(new_time[1]) == 2:
                            new_time[1] += ".000"
                            new_time = new_time[0] + ':' + new_time[1]
                        else:
                            new_time = new_time[0] + ':' + new_time[1][:-3]
                        print("  (NEW GHOSTS FOUND)", g["trackName"] + "; category:", get_category(categoryId) + "; time:", new_time)
                        gs_set_new_ghost(row, gs_track_column, new_time, g["dateSet"][:-1], g["bestSplitSimple"], g["href"], g["vehicleId"], g["driverId"], g["controller"])
            shifted_LM = cd_LM + datetime.timedelta(hours=1)
            wks.update_cell(row, 3, shifted_LM.isoformat())
        row += 1

if __name__ == "__main__":
    main()