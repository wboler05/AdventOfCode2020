#!/usr/bin/env python3

import argparse, os, sys
import numpy
import re

def load_data(input_filename):
    assert(os.path.exists(input_filename))
    data = None
    with open(input_filename, 'r') as ifile:
        data = [d for d in ifile.read().split('\n') if len(d) > 0]
    return data

def parse_data(data):
    allergen_pattern = r"^(?P<ingredient_list>[\w\s]+)(?:\(contains )(?P<allergen_list>[\w\s,]+)(?:\))$"
    master_ingredients_list = list()
    for row in data:
        m = re.search(allergen_pattern, row)
        if m is not None:
            ingredient_list_str = m.group('ingredient_list')
            allergen_list_str = m.group('allergen_list')
            ingredient_list = [s for s in ingredient_list_str.split(' ') if len(s) > 0]
            allergen_list_str = allergen_list_str.replace(',', ' ')
            allergen_list = [a for a in allergen_list_str.split(' ') if len(a) > 0]
            master_ingredients_list.append(
                (ingredient_list, allergen_list)
            )
        else:
            ingredient_list = [s for s in row.split(' ') if len(s) > 0]
            master_ingredients_list.append(
                (ingredient_list, list())
            )
    return master_ingredients_list


def reduce_ingredients(allergen_dict):

    learned_allergens = dict()

    change = True
    while change:

        change = False

        #print_dicts(allergen_dict, ingredient_dict)

        ingredient_update_list = list()
        for allergen, ad in allergen_dict.items():
            if allergen not in learned_allergens:
                if len(ad['ingredients']) == 1:
                    ingredient = list(ad['ingredients'].keys())[0]
                    learned_allergens[allergen] = ingredient
                    ingredient_update_list.append((ingredient, allergen))

        for ingredient, allergen in ingredient_update_list:
            for alg, ad in allergen_dict.items():
                if alg != allergen:
                    if ingredient in ad['ingredients']:
                        change = True
                        ad['ingredients'].pop(ingredient)

    return learned_allergens


def generate_allergen_dict(ingredient_list):
    allergen_dict = dict()
    for ingredients,allergens in ingredient_list:
        if len(allergens) > 0:
            for allergen in allergens:
                if allergen not in allergen_dict:
                    allergen_dict[allergen] = dict()
                    allergen_dict[allergen]['ingredients'] = dict()
                    allergen_dict[allergen]['count'] = 1
                else:
                    allergen_dict[allergen]['count'] += 1

                for ingredient in ingredients:
                    if ingredient not in allergen_dict[allergen]['ingredients']:
                        allergen_dict[allergen]['ingredients'][ingredient] = 1
                    else:
                        allergen_dict[allergen]['ingredients'][ingredient] += 1
                

    for allergen, ad in allergen_dict.items():
        allergen_count = ad['count']
        ingredient_set = set(ad['ingredients'].keys())
        for ingredient in ingredient_set:
            if ad['ingredients'][ingredient] != allergen_count:
                ad['ingredients'].pop(ingredient)

    allergen_dict = reduce_ingredients(allergen_dict)

    return allergen_dict
    

def get_allergen_data_from_file(input_filename):
    data = load_data(input_filename)
    master_ingredient_list = parse_data(data)
    allergen_dict = generate_allergen_dict(master_ingredient_list)
    return allergen_dict, master_ingredient_list
    

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename', type=str)
    args = parser.parse_args()

    allergen_dict, master_ingredient_list = get_allergen_data_from_file(args.input_filename)

    #non_allergens_dict = count_non_allergens(master_ingredient_list, allergen_dict)

    print("Learned Allergens:")
    for k,v in allergen_dict.items():
        print(" - {}: {}".format(k,v))

    

if __name__ == '__main__':
    main()