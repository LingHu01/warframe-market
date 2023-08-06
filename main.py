import requests
import json
import numpy as np

class CheckVitus:
    def __init__(self):
        self.vitus_dct = None
        self.item_list = None
        self.process()

    def process(self):  # main
        self.load()
        for name, value in self.vitus_dct.items():
            self.get_data(name)
            self.slice(value)
            self.elaborate_data(value)
            self.item_list = None

    def load(self):  # open js file
        with open('vitus_mod.json', 'r') as fp:
            self.vitus_dct = json.load(fp)

    def get_data(self, name):  # get item list from wf.market and filter rank and offline player
        def filter_dict(dictionary, key, value):
            return True if dictionary[key] == value else False

        item = requests.get(f"https://api.warframe.market/v1/items/{name}/orders")
        lst = [x for x in item.json()["payload"]["orders"] if x["order_type"] == 'sell']
        lst = [x for x in lst if filter_dict(x['user'], 'status', 'ingame')]
        self.item_list = sorted(lst, key=lambda k: k['platinum'])

    def slice(self, value):
        plat, last = (value * 0.75), 0
        for i, dct in enumerate(self.item_list[3:], start=3):
            if i > 4:
                if dct['platinum'] < plat:
                    return
                elif dct['platinum'] != last:
                    self.item_list = self.item_list[:i-1]
                    return
            last = dct['platinum']

    def elaborate_data(self, value):
        platinum = np.array([dct.get('platinum') for dct in self.item_list])
        quantity = np.array([dct.get('quantity') for dct in self.item_list])
        average = sum(platinum * quantity) / len(quantity)
        print(average)



def main():
    CheckVitus()

if __name__ == '__main__':
    main()
