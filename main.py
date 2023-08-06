import requests
import json

class CheckVitus:
    def __init__(self):
        self.vitus = None
        self.sell_item = None
        self.till_15 = None
        self.load()
        self.process()

    def process(self):  # main
        for name, value in self.vitus.items():
            self.get_data(name)
            self.check(name, value)

    def load(self):  # open js file
        with open('vitus_mod.json', 'r') as fp:
            self.vitus = json.load(fp)

    def get_data(self, name):  # get item list from wf.market and filter rank and offline player
        def filter_dict(dictionary, key, value):
            return True if dictionary[key] == value else False

        item = requests.get(f"https://api.warframe.market/v1/items/{name}/orders")
        lst = [x for x in item.json()["payload"]["orders"] if x["order_type"] == 'sell']
        lst = [x for x in lst if filter_dict(x, 'mod_rank', 0)]
        lst = [x for x in lst if filter_dict(x['user'], 'status', 'ingame')]
        self.sell_item = lst

    def check(self, name, value):
        plat = value * 0.75
        sorted_lst = sorted(self.sell_item, key=lambda k: k['platinum'])
        quantity, peoples = 0, 0
        for i, x in enumerate(sorted_lst):
            if x['platinum'] <= plat:
                peoples += 1
                quantity += x['quantity']
            elif x['platinum'] > 15 and i == 5:
                return self.print_result(name, sorted_lst[:i], quantity, peoples)

    @staticmethod
    def print_result(name, lst, quantity, people):
        print(f"{' '.join(name.split('_'))}: {quantity} are sold by {people} people")
        for x in lst:
            print(f"quantity: {x['quantity']:4d}, platinum: {x['platinum']:3d}, name: {x['user']['ingame_name']}")
        print()

def main():
    CheckVitus()

if __name__ == '__main__':
    main()
