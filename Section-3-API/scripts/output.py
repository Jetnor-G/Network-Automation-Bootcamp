import json
json_string='''
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "url": "https://10.100.100.25/api/dcim/sites/2/",
            "display_url": "https://10.100.100.25/dcim/sites/2/",
            "display": "Arena Stadium",
            "name": "Arena Stadium",
            "slug": "arena-stadium",
            "status": {
                "value": "active",
                "label": "Active"
            },
            "region": {
                "id": 2,
                "url": "https://10.100.100.25/api/dcim/regions/2/",
                "display": "Tirana",
                "name": "Tirana",
                "slug": "tirana",
                "description": "",
                "site_count": 0,
                "_depth": 1
            },
            "group": null,
            "tenant": null,
            "facility": "",
            "time_zone": null,
            "description": "",
            "physical_address": "",
            "shipping_address": "",
            "latitude": null,
            "longitude": null,
            "owner": null,
            "comments": "",
            "asns": [],
            "tags": [],
            "custom_fields": {},
            "created": "2026-04-21T08:40:10.916983Z",
            "last_updated": "2026-04-21T08:40:10.917006Z",
            "circuit_count": 0,
            "device_count": 8,
            "prefix_count": 0,
            "rack_count": 0,
            "virtualmachine_count": 0,
            "vlan_count": 0
        },
        {
            "id": 4,
            "url": "https://10.100.100.25/api/dcim/sites/4/",
            "display_url": "https://10.100.100.25/dcim/sites/4/",
            "display": "Arena Stadium 2",
            "name": "Arena Stadium 2",
            "slug": "arena-stadium-2",
            "status": {
                "value": "active",
                "label": "Active"
            },
            "region": {
                "id": 2,
                "url": "https://10.100.100.25/api/dcim/regions/2/",
                "display": "Tirana",
                "name": "Tirana",
                "slug": "tirana",
                "description": "",
                "site_count": 0,
                "_depth": 1
            },
            "group": null,
            "tenant": null,
            "facility": "",
            "time_zone": null,
            "description": "",
            "physical_address": "",
            "shipping_address": "",
            "latitude": null,
            "longitude": null,
            "owner": null,
            "comments": "",
            "asns": [],
            "tags": [],
            "custom_fields": {},
            "created": "2026-04-22T12:32:04.491506Z",
            "last_updated": "2026-04-22T12:32:04.491528Z",
            "circuit_count": 0,
            "device_count": 1,
            "prefix_count": 0,
            "rack_count": 0,
            "virtualmachine_count": 0,
            "vlan_count": 0
        },
        {
            "id": 1,
            "url": "https://10.100.100.25/api/dcim/sites/1/",
            "display_url": "https://10.100.100.25/dcim/sites/1/",
            "display": "Default",
            "name": "Default",
            "slug": "default",
            "status": {
                "value": "active",
                "label": "Active"
            },
            "region": null,
            "group": null,
            "tenant": null,
            "facility": "",
            "time_zone": null,
            "description": "",
            "physical_address": "",
            "shipping_address": "",
            "latitude": null,
            "longitude": null,
            "owner": null,
            "comments": "",
            "asns": [],
            "tags": [],
            "custom_fields": {},
            "created": "2026-04-20T12:35:47.003321Z",
            "last_updated": "2026-04-20T12:35:47.003343Z",
            "circuit_count": 0,
            "device_count": 0,
            "prefix_count": 0,
            "rack_count": 0,
            "virtualmachine_count": 0,
            "vlan_count": 0
        },
        {
            "id": 3,
            "url": "https://10.100.100.25/api/dcim/sites/3/",
            "display_url": "https://10.100.100.25/dcim/sites/3/",
            "display": "Lufthansa Technical Site",
            "name": "Lufthansa Technical Site",
            "slug": "lufthansa-technical-site",
            "status": {
                "value": "active",
                "label": "Active"
            },
            "region": {
                "id": 3,
                "url": "https://10.100.100.25/api/dcim/regions/3/",
                "display": "Tirana sub-region",
                "name": "Tirana sub-region",
                "slug": "tirana-sub-region",
                "description": "",
                "site_count": 0,
                "_depth": 1
            },
            "group": null,
            "tenant": null,
            "facility": "",
            "time_zone": null,
            "description": "",
            "physical_address": "",
            "shipping_address": "",
            "latitude": null,
            "longitude": null,
            "owner": null,
            "comments": "",
            "asns": [],
            "tags": [],
            "custom_fields": {},
            "created": "2026-04-22T12:08:07.737421Z",
            "last_updated": "2026-04-22T12:08:07.737441Z",
            "circuit_count": 0,
            "device_count": 9,
            "prefix_count": 0,
            "rack_count": 0,
            "virtualmachine_count": 0,
            "vlan_count": 0
        }
    ]
}
'''
data = json.loads(json_string)
count = data["count"]
#print(count)
#print(type(count))
results = data["results"]
print(results[0]["region"]['name'])