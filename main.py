import requests
import json
import numpy as np


class CheckVitus:
    def __init__(self):
        self.all_items = []      # exchange: float:{name: str, list: list(dict), quantity: int}
        self.quantity = None        # number of item with price below exchange rate
        self.vitus_dct = None       # {name: vitus cost}
        self.item_list = None       # one item full API response
        self.exchange_rate = None   # vitus/plat exchange
        self.process_data()

    # main
    def process_data(self):
        self.load()
        for name, value in self.vitus_dct.items():
            self.get_data(name)
            self.refactor()
            self.slice(value)
            self.calc(value)
            self.all_items.append({self.exchange_rate: {'name': name, 'list': self.item_list, 'quantity': self.quantity}})
            self.item_list = None

    # open js file
    def load(self):
        with open('vitus_mod.json', 'r') as fp:
            self.vitus_dct = json.load(fp)

    @staticmethod
    def filter_dict(dictionary, key, value):
        return True if dictionary[key] == value else False

    # get item list from wf.market and filter rank and offline player
    def get_data(self, name):
        item = requests.get(f"https://api.warframe.market/v1/items/{name}/orders")
        lst = [x for x in item.json()["payload"]["orders"] if x["order_type"] == 'sell']
        lst = [x for x in lst if self.filter_dict(x, 'mod_rank', 0)]
        lst = [x for x in lst if self.filter_dict(x['user'], 'status', 'ingame')]
        self.item_list = sorted(lst, key=lambda k: k['platinum'])

    # filter useless info
    def refactor(self):
        self.item_list = [
            {
                'quantity': dct.get('quantity'),
                'platinum': dct.get('platinum'),
                'mod_rank': dct.get('mod_rank'),
                'seller': dct['user'].get('ingame_name')
            } for dct in self.item_list
        ]

    def slice(self, value):
        plat, last = (value * 0.75), 0
        for i, dct in enumerate(self.item_list[3:], start=3):
            if i > 4:
                if dct['platinum'] < plat:
                    return
                elif dct['platinum'] != last:
                    self.item_list = self.item_list[:i - 1]
                    return
            last = dct['platinum']

    def calc(self, value):
        below = 0
        platinum = np.array([dct.get('platinum') for dct in self.item_list if self.filter_dict(dct, 'mod_rank', 0)])
        quantity = np.array([dct.get('quantity') for dct in self.item_list if self.filter_dict(dct, 'mod_rank', 0)])
        average = sum(platinum * quantity) / sum(quantity)
        self.exchange_rate = average / value
        for price, number in zip(platinum, quantity):
            if price / value < self.exchange_rate:
                below += number
            else:
                self.quantity = below
                return





def main():
    CheckVitus()


if __name__ == '__main__':
    main()
