import requests
from tqdm import tqdm
import os
import json
from random import randint
import argparse
from csv import writer
from time import sleep



data = [
    ("Paris", 2181371),
    ("Marseille", 839043),
    ("Lyon", 472305),
    ("Toulouse", 437715),
    ("Nice", 347060),
    ("Nantes", 282853),
    ("Montpellier", 251634),
    ("Strasbourg", 272975),
    ("Bordeaux", 232260),
    ("Lille", 226014),
    ("Rennes", 209613),
    ("Reims", 183837),
    ("Toulon", 167816),
    ("Saint-Étienne", 177480),
    ("Le Havre", 182580),
    ("Grenoble", 156107),
    ("Dijon", 151504),
    ("Angers", 152337),
    #("Saint-Denis (Réunion)", 138314),
    ("Villeurbanne", 136473),
    ("Nîmes", 144092),
    ("Clermont-Ferrand", 138992),
    ("Aix-en-Provence", 142534),
    ("Le Mans", 144016),
    ("Brest", 144548),
    ("Tours", 136942),
    ("Amiens", 136105),
    ("Limoges", 136539),
    ("Annecy", 51023),
    ("Boulogne-Billancourt", 110251),
    ("Perpignan", 115326),
    ("Metz", 124435),
    ("Besançon", 117080),
    ("Orléans", 113130),
    ("Seine-Saint-Denis", 97875),
    ("Rouen", 107904),
    ("Montreuil", 101587),
    ("Argenteuil", 102683),
    ("Mulhouse", 110514),
    ("Caen", 110399),
    ("Nancy", 105468),
    #("Saint-Paul (Réunion)", 99291),
    ("Roubaix", 97952),
    ("Tourcoing", 92357),
    ("Nanterre", 88316),
    ("Vitry-sur-Seine", 82902),
    ("Créteil", 88939),
    ("Avignon", 92454),
    ("Poitiers", 88776),
    ("Aubervilliers", 73506),
    ("Asnières-sur-Seine", 82351),
    ("Aulnay-sous-Bois", 81600),
    ("Colombes", 82026),
    ("Dunkirk", 69274),
    #("Saint-Pierre (Réunion)", 74480),
    ("Versailles", 87549),
    ("Courbevoie", 84415),
    #("Le Tampon (Réunion)", 69849),
    ("Cherbourg-en-Cotentin", 78549),
    ("Rueil-Malmaison", 77625),
    ("Béziers", 72245),
    ("La Rochelle", 77196),
    ("Champigny-sur-Marne", 74863),
    #("Fort-de-France", 90347),
    ("Pau", 83903),
    ("Saint-Maur-des-Fossés", 75214),
    ("Cannes", 70610),
    ("Antibes", 75820),
    ("Calais", 74888),
    ("Drancy", 66063),
    ("Mérignac", 65469),
    #("Mamoudzou (Mayotte)", 53122),
    ("Saint-Nazaire", 68838),
    ("Ajaccio", 66063),
    ("Colmar", 65713),
    ("Issy-les-Moulineaux", 61471),
    ("Noisy-le-Grand", 61341),
    ("Vénissieux", 57179),
    ("Évry-Courcouronnes", 66851),
    ("Levallois-Perret", 62851),
    ("Cergy", 56873),
    #("Cayenne (French Guiana)", 58004),
    ("Pessac", 57187),
    ("Valence (Drôme)", 65263),
    ("Bourges", 70828),
    ("Ivry-sur-Seine", 55608),
    ("Quimper", 64902),
    ("Clichy", 57162),
    ("La Seyne-sur-Mer", 56768),
    ("Antony", 60552),
    ("Troyes", 61344),
    ("Villeneuve-d'Ascq", 61151),
    ("Montauban", 53941),
    ("Pantin", 53577),
    ("Neuilly-sur-Seine", 61471),
    ("Sarcelles", 58654),
    #("Niort", 58066),
    ("Chambéry", 57543),
    ("Le Blanc-Mesnil", 51109),
    ("Lorient", 58547),
    ("Beauvais", 55481),
    ("Maisons-Alfort",53233),
    ("Meaux",48842),
    ("Narbonne", 50776),
    ("Villejuif",50571),
    ("Chelles",48616),
    ("La Roche-sur-Yon",50717),
    ("Hyères", 55007)
]




city_names = [row[0] for row in data]
city_data_dict = {city_name: [] for city_name in city_names}
city_data_dict_retry = {city_name: [] for city_name in city_names}

def load_cities(): #This function adds all (!) the coordinates from the city files to our dictionary
    for city_name in os.listdir(args.cities):
        city_folder = os.path.join(args.cities, city_name)
        if os.path.isdir(city_folder):
            coordinates = []
            print(f'Loading coordinates from {city_name}...')
            city_file = os.path.join(city_folder, f'{city_name}.txt')
            if os.path.exists(city_file):
                with open(city_file) as f:
                    for line in tqdm(f):
                        lat_str, lng_str = line.strip('()\n').split(', ')
                        latitude = float(lat_str)
                        longitude = float(lng_str)
                        coordinates.append((latitude, longitude))
                city_data_dict[city_name].append(coordinates)
            else:
                print(f"Warning: No coordinates file found for {city_name}")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cities", help="The folder full of addresses per city to read and extract GPS coordinates from", required=True, type=str)
    parser.add_argument("--output", help="The output folder where the images will be stored, (defaults to: images/)", default='images/', type=str)
    parser.add_argument("--key", help="Your Google Street View API Key", type=str, required=True)
    return parser.parse_args()                

args = get_args()
url = 'https://maps.googleapis.com/maps/api/streetview?'
meta_url = 'https://maps.googleapis.com/maps/api/streetview/metadata?'

def main():
    # Open and create all the necessary files & folders
    os.makedirs(args.output, exist_ok=True)
    
    load_cities()
    
    for city in city_data_dict:  # Traverse all cities and then all coordinates for the images
        os.makedirs(os.path.join(args.output, city), exist_ok=True)
        if city_data_dict[city] != []:
            coordinates = city_data_dict[city].pop() 
        else:
            coordinates = []
        for tup in coordinates:
            x = tup[0]
            y = tup[1]
            params = {
                'size': '640x640',
                'location': str(x) + ',' + str(y),
                'heading': str((randint(0, 3) * 90) + randint(-15, 15)),
                'pitch': '20',
                'key': args.key
            }
            meta_params = {'key': args.key,
                           'location': str(x) + ',' + str(y)
            }
            meta_response = requests.get(meta_url, params=meta_params).json()
            if meta_response['status'] == 'REQUEST_DENIED':
                city_data_dict_retry[city].append(tup)
            elif meta_response['status'] == 'OK':
                response = requests.get(url, params)
                image_filename = os.path.join(args.output, city, f'{x},{y}.jpg')
                with open(image_filename, "wb") as file:
                    file.write(response.content)
                sleep(2)
        
        
        coordinates = city_data_dict_retry[city]
        for tup in coordinates:
            x = tup[0]
            y = tup[1]
            params = {
                'size': '640x640',
                'location': str(x) + ',' + str(y),
                'heading': str((randint(0, 3) * 90) + randint(-15, 15)),
                'pitch': '20',
                'key': args.key
            }
            meta_params = {'key': args.key,
                           'location': str(x) + ',' + str(y)
            }
            meta_response = requests.get(meta_url, params=meta_params).json()
            if meta_response['status'] == 'OK':
                response = requests.get(url, params)
                image_filename = os.path.join(args.output, city, f'{x},{y}.jpg')
                with open(image_filename, "wb") as file:
                    file.write(response.content)
                sleep(2)

if __name__ == '__main__':
    main()