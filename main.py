import folium
import requests
import webbrowser
import matplotlib.pyplot as plt
import numpy as np
import time
from pynput import mouse
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from selenium import webdriver


def f(x,y):
    try:
        str = f"{x},{y}"

        curl = 'https://api.opentopodata.org/v1/aster30m?locations=' + str
        m = requests.get(curl)
        print(x,y)
        time.sleep(0.8)
        n = float(m.json().get('results')[0].get('elevation'))
        return n
    except:
        print (m.json())
        time.sleep(0.1)
        n = float(m.json().get('results')[0].get('elevation'))
        return n

map = folium.Map(location=[20,0], tiles="OpenStreetMap", zoom_start=2)


# add latitude and longitude tool to map
map.add_child(folium.LatLngPopup())

# display map
map.save("map2.html")

points = [[0.,0.],[0.,0.]]

def isBrowserOpen(driver):
        isOpen=1
        try:
            driver.title
        except WebDriverException:
            isOpen=0
        return isOpen

def on_click(x, y, button, pressed):
    # print('{0} at {1}'.format(
    #     'Pressed' if pressed else 'Released', leaflet-popup-content
    #     (x, y)))
    if not pressed:
        if(isBrowserOpen(driver) and button==mouse.Button.left):
            html = driver.page_source
            soup = BeautifulSoup(html , "lxml")
            elems = soup.find_all("div", class_="leaflet-popup-content")
            for elem in elems:
                str = elem.text.split(":")
                Lon = float(str[2])
                str = str[1].split("L")
                Lat = float(str[0])
                if(points[0] != [Lat,Lon] and points[1] != [Lat,Lon] ):
                    points[0]=points[1]
                    points[1]=[Lat, Lon]
                    print(Lat, Lon)
        else:
            print("Stoop")
            return False
        # raise ValueError
    if not pressed:
        # Stop listener
        return False

driver = webdriver.Chrome(executable_path=r"./chromedriver.exe")
try:
    url="file:///C:/Users/390/Desktop/sppr_sem/openmap/map2.html"
    driver.get(url=url)
    while(isBrowserOpen(driver)):
        with mouse.Listener(on_click=on_click) as listener:
            try:
                listener.join()
            except ValueError:
                print("skksk")
                listener.stop()
                break
    print(points)
    # time.sleep(20)
except Exception as e:
    pass
finally:
    driver.quit()



# Creating dataset
x_fin = []
y_fin = []
z_fin = []


A = []
B = []
A.append(points[0])
B.append(points[1])
n = 8
step_x = abs(abs(A[0][0]) - abs(B[0][0]))/n
step_y = abs(abs(A[0][1]) - abs(B[0][1]))/n
min_x = min(A[0][0] ,B[0][0])
min_y = min(A[0][1],B[0][1])
max_x = max(A[0][0] ,B[0][0])
max_y = max(A[0][1],B[0][1])
x_line = []
y_line = []
z_line = []
x_cur=min_x
y_cur=min_y
for j in range(n):
    x_line.append(x_cur)
    y_line.append(y_cur)
    z_line.append(f(x_cur,y_cur))
    for i in range(n):
        x_cur+=step_x
        x_line.append(x_cur)
        y_line.append(y_cur)
        z_line.append(f(x_cur, y_cur))
    y_cur+=step_y
    x_cur=min_x

x_line=np.array(x_line)
y_line=np.array(y_line)
z_line=np.array(z_line)


# Creating figure
fig = plt.figure(figsize=(14, 9))
ax = plt.axes(projection='3d')

# Creating plot
ax.plot_trisurf(x_line, y_line, z_line, linewidth=0, antialiased=False)

plt.xlim(min_x,max_x)
plt.ylim(min_y,max_y)
# show plot
plt.show()
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = f"""
[out:json];

way
  ({min_x},{min_y},{max_x},{max_y});

out;

"""
response = requests.get(overpass_url,
                        params={'data': overpass_query})
data = response.json()
#print(data.json().get("elements"))
list_el = []
count = 0
count_buildings = 0
count_higways = 0
count_nature = 0
count_water = 0
count_landuse = 0
for elem in data.get("elements"):
    tags = elem.get("tags")
    if tags is not None:
        #print(tags.keys())
        if "building" in tags:
            count_buildings += len(elem.get("nodes"))
        if "highway" in tags:
            count_higways += len(elem.get("nodes"))
        if "natural" in tags:
            if tags['natural'] in ['wetland', 'water', 'strait', 'spring']:
                count_water += len(elem.get("nodes"))
            else:
                count_nature += len(elem.get("nodes"))
        if "landuse" in tags:
            if tags['landuse'] in ['allotments', 'farmland', 'flowerbed', 'forest', 'meadow', 'orchard', 'plant_nursery', 'vineyard','cemetery','grass', 'recreation_ground','village_green']:
                count_landuse += len(elem.get("nodes"))
count = count_buildings + count_nature + count_landuse + count_water + count_higways
print(count,count_buildings,count_nature,count_landuse,count_water,count_higways)
#print(json.dumps(data.get("elements"), indent=2))

labels = 'Постройки', 'Растительность','Водичка', 'landuse','dorogi'
sizes = [count_buildings, count_nature, count_water, count_landuse,count_higways]

fig1, ax1 = plt.subplots()
explode = (0, 0, 0, 0, 0)
ax1.pie(sizes, explode=explode, labels=labels,autopct='%1.1f%%',
        shadow=True, startangle=90)

plt.show()





