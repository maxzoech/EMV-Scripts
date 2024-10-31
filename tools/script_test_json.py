import requests
import json

r = requests.get('https://www.ebi.ac.uk/pdbe/api/emdb/entry/all/EMD-0521')
dict = json.loads(r.text)

resolution = float(dict['EMD-0521'][0]['processing']['reconstruction']['resolution_by_author'])
print (resolution)

sampling = float(dict['EMD-0521'][0]['map']['pixel_spacing']['y']['value'])
print (sampling)

size = int(dict['EMD-0521'][0]['map']['dimensions']['column'])
print (size)

or_x = -(int(dict['EMD-0521'][0]['map']['origin']['column']))
or_y = -(int(dict['EMD-0521'][0]['map']['origin']['section']))
or_z = -(int(dict['EMD-0521'][0]['map']['origin']['row']))
origin=(or_x, or_y, or_z)
print (origin)


       
