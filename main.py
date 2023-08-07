import requests
import json
import numpy as np
from icecream import ic

class CheckVitus:
    def __init__(self):
        self.all_items = []         # exchange: float:{name: str, list: list(dict), below: int}
        self.below_ex = None        # number of item with price below exchange rate
        self.vitus_dct = None       # {name: vitus cost}
        self.item_list = None       # one item full API response
        self.p_below_ex = None      # people selling below exchange rate
        self.exchange_rate = None   # vitus/plat exchange
        print('processing...')
        self.process_data()
        self.print_out()

    # main
    def process_data(self):
        self.load()
        for name, value in self.vitus_dct.items():
            self.get_data(name)
            self.refactor()
            self.slice(value, name)
            self.calc(value)
            self.result(name)
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

    def slice(self, value, name):
        plat, last = (value * 0.75), 0
        for i, dct in enumerate(self.item_list):
            if i > 4:
                if dct['platinum'] < plat:
                    self.item_list = self.item_list[:i]
                    return
                elif dct['platinum'] != last:
                    self.item_list = self.item_list[:i]
                    return
            last = dct['platinum']

    def calc(self, value):
        below_cost, below_person = 0, 0
        platinum = np.array([dct.get('platinum') for dct in self.item_list if self.filter_dict(dct, 'mod_rank', 0)])
        quantity = np.array([dct.get('quantity') for dct in self.item_list if self.filter_dict(dct, 'mod_rank', 0)])
        try:
            average = sum(platinum * quantity) / sum(quantity)
        except ZeroDivisionError:
            average = 0
        except TypeError:
            average = 0

        self.exchange_rate = average / value
        for price, number in zip(platinum, quantity):
            if price / value < self.exchange_rate:
                below_cost += number
                below_cost += 1
            else:
                self.below_ex = below_cost
                self.p_below_ex = below_cost
                return

    def result(self, name):
        self.all_items.append(
            {self.exchange_rate:
                {
                    'name': name,
                    'list': self.item_list,
                    'below_cost': self.below_ex,
                    'p_below_cost': self.p_below_ex
                }
            }
        )

    def print_out(self):
        for dct in sorted(self.all_items, key=lambda y: list(y.keys())[0], reverse=True):
            key, info = dct.items().__iter__().__next__()
            print(
                f"{info['name']:25s}    "
                f"{info['below_cost']:5d} are sold by {info['p_below_cost']:3d} person below {key:4.2f} plat/vitus"
            )
            for x in info['list']:
                print(f"num: {x['quantity']:<4d}     plat: {x['platinum']:3d}        "
                      f"mod rank: {x['mod_rank']:2d}         seller: {x['seller']}")
            print()
            print()


def main():
    CheckVitus()


if __name__ == '__main__':
    main()
