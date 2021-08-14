import sqlite3
import argparse
import sys

parser = argparse.ArgumentParser(description="This program prints recipes \
consisting of the ingredients you provide.")
parser.add_argument("database", help="Database name")
parser.add_argument("--ingredients")
parser.add_argument("--meals")
args = parser.parse_args()

if not args.ingredients:
    database = sys.argv[-1]
else:
    database = args.database


def sql_fetchall(select_command):
    cursor.execute(select_command)
    return cursor.fetchall()


def sql_execution(command):
    cursor.execute(command)
    return connection.commit()


connection = sqlite3.connect(database)
cursor = connection.cursor()


if args.ingredients and args.meals is not None:
    curr = connection.cursor()
    quantity, temp, quantity_out = [], [], []
    for ingredient in args.ingredients.split(","):
        quantity.append(set(number[0] for number in curr.execute(
            f"SELECT recipe_id FROM quantity WHERE ingredient_id in (SELECT ingredient_id FROM ingredients WHERE ingredient_name = '{ingredient}')").fetchall()))
    quantity = set.intersection(*quantity)
    for meal in args.meals.split(","):
        temp.append(set(number[0] for number in curr.execute(
            f"SELECT recipe_id FROM serve WHERE meal_id in (SELECT meal_id FROM meals WHERE meal_name = '{meal}')").fetchall()))
    if len(args.meals.split(",")) == 1:
        quantity_out = set.intersection(*temp)
    else:
        for item in [*temp]:
            for q in item:
                if q in quantity:
                    quantity_out.append(q)

    recipes = ", ".join(
        [curr.execute(f"SELECT recipe_name FROM recipes WHERE recipe_id = '{id_}'").fetchone()[0] for id_ in
         set.intersection(quantity, quantity_out)])

    print(f"Recipes selected for you: {recipes}" if recipes else "There are no such recipes in the database.")
    connection.close()
    sys.exit()


cursor.execute('''CREATE TABLE IF NOT EXISTS ingredients (
                  ingredient_id INTEGER PRIMARY KEY,
                  ingredient_name TEXT NOT NULL UNIQUE)
;''')
connection.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS measures (
                  measure_id INTEGER PRIMARY KEY,
                  measure_name TEXT UNIQUE)
;''')
connection.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS meals(
                  meal_id INTEGER PRIMARY KEY,
                  meal_name TEXT NOT NULL UNIQUE)
;''')
connection.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                  recipe_id INTEGER PRIMARY KEY,
                  recipe_name TEXT NOT NULL,
                  recipe_description TEXT)
;''')
connection.commit()


cursor.execute('''CREATE TABLE IF NOT EXISTS serve (serve_id INTEGER PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                meal_id INTEGER NOT NULL,
                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                FOREIGN KEY(meal_id) REFERENCES meals(meal_id))
;''')
connection.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS quantity (quantity_id INTEGER PRIMARY KEY,
                quantity INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                measure_id INTEGER NOT NULL,                
                ingredient_id INTEGER NOT NULL,
                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                FOREIGN KEY(measure_id) REFERENCES measures(measure_id),
                FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id))
;''')
connection.commit()

cursor.execute('PRAGMA foreign_keys = ON;')
connection.commit()

data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}


for element in data['meals']:
    cursor.execute(f'INSERT INTO meals (meal_name) VALUES ("{element}");')
connection.commit()

cursor.execute('''SELECT
    meal_id,
    meal_name
FROM
    meals;''')

result = cursor.fetchall()
print(result)

for ingredient in data["ingredients"]:
    cursor.execute(f'INSERT INTO ingredients (ingredient_name) VALUES ("{ingredient}");')
connection.commit()

for measure in data["measures"]:
    cursor.execute(f'INSERT INTO measures (measure_name) VALUES ("{measure}");')
connection.commit()
print('Pass the empty recipe name to exit.')
while True:
    recipe_name = input('Recipe name: ')
    if recipe_name == '':
        break
    else:
        recipe_description = input('Recipe description: ')
        print('1) breakfast  2) brunch  3) lunch  4) supper')
        serve = input('Enter proposed meals separated by a space: ').split()
        recipe_id = cursor.execute(f"INSERT INTO recipes(recipe_name, recipe_description)\
                 VALUES('{recipe_name}', '{recipe_description}')").lastrowid
        connection.commit()
        for meal in serve:
            cursor.execute(f'INSERT INTO serve (meal_id, recipe_id) VALUES ({int(meal)}, {recipe_id});')
        connection.commit()
        while True:
            quantity = input('Input quantity of ingredient <press enter to stop>: ').split()
            if len(quantity) == 0:
                break
            else:
                if len(quantity) == 2:
                    measure_id = cursor.execute('''SELECT
                                                measure_id
                                        FROM
                                                measures
                                        WHERE 
                                                measure_name == "";
                                        ''').fetchall()
                    ingredient_id = cursor.execute(f'''SELECT
                                                ingredient_id
                                        FROM
                                                ingredients
                                        WHERE 
                                                ingredient_name == '{quantity[1]}';
                                        ''').fetchall()
                    connection.commit()
                    quantity_of_ingredients = int(quantity[0])
                    print(quantity_of_ingredients, recipe_id, measure_id, ingredient_id)
                    cursor.execute(f'INSERT INTO quantity (quantity, recipe_id, measure_id, ingredient_id) VALUES ({quantity_of_ingredients}, {recipe_id}, {measure_id[0][0]}, {ingredient_id[0][0]});')
                    connection.commit()
                    continue
                elif len(quantity) == 3:
                    if quantity[1] not in data["measures"]:
                        print('The measure is not conclusive!')
                        continue
                    if quantity[2] == 'blue':
                        ingredient = 'blueberry'
                    elif quantity[2] == 'black':
                        ingredient = 'blackberry'
                    else:
                        ingredient = quantity[2]
                    if ingredient not in data["ingredients"]:
                        print('The ingredient is not conclusive!')
                        continue
                    measure_id = cursor.execute(f'''SELECT
                                                 measure_id
                                          FROM
                                                 measures
                                          WHERE 
                                                 measure_name == '{quantity[1]}';
                                          ''').fetchall()
                    connection.commit()
                    ingredient_id = cursor.execute(f'''SELECT
                                                 ingredient_id
                                          FROM
                                                 ingredients
                                          WHERE 
                                                 ingredient_name == '{ingredient}';
                                          ''').fetchall()
                    connection.commit()

                    quantity_of_ingredients = int(quantity[0])
                    print(quantity_of_ingredients, recipe_id, measure_id, ingredient_id)
                    cursor.execute(f'INSERT INTO quantity (quantity, recipe_id, measure_id, ingredient_id) VALUES ({quantity_of_ingredients}, {recipe_id}, {measure_id[0][0]}, {ingredient_id[0][0]});')
                    connection.commit()
                    continue
        continue
connection.close()
