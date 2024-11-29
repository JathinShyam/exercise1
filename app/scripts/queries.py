from django.db import transaction
from django.db.models import Min, Max
from app.models import Country, CustomUser, State, City
# CustomUser

def run():

    # Insert data individually
    user = CustomUser.objects.create(email="example1@example.com", password="password")
    def insert_data():
        # Check if the country already exists
        country, created = Country.objects.get_or_create(
            name='India',
            defaults={
                'country_code': 'IN',
                'curr_symbol': '₹',
                'phone_code': '+91'
            },
            my_user = user
        )

        if created:
            print("Country 'India' created.")
        else:
            print("Country 'India' already exists.")

        # Create a state
        state, created = State.objects.get_or_create(
            name='Gujarat',
            defaults={
                'state_code': 'GJ',
                'gst_code': '24GUJGST',
                'country': country
            }
        )

        if created:
            print("State 'Gujarat' created.")
        else:
            print("State 'Gujarat' already exists.")

        # Create a state
        state, created = State.objects.get_or_create(
            name='Telangana',
            defaults={
                'state_code': 'TS',
                'gst_code': '24GUFJGST',
                'country': country
            }
        )

        if created:
            print("State 'Telangana' created.")
        else:
            print("State 'Telangana' already exists.")
        
        # Create a state
        state, created = State.objects.get_or_create(
            name='Tamil Nadu',
            defaults={
                'state_code': 'TN',
                'gst_code': '24GAUJGST',
                'country': country
            }
        )

        if created:
            print("State 'Tamil Nadu' created.")
        else:
            print("State 'Tamil Nadu' already exists.")
        
        # Create a state
        state, created = State.objects.get_or_create(
            name='Maharashtra',
            defaults={
                'state_code': 'MH',
                'gst_code': '24GUJTGST',
                'country': country
            }
        )

        if created:
            print("State 'Maharashtra' created.")
        else:
            print("State 'Maharashtra' already exists.")
        

        # Create a city
        City.objects.get_or_create(
            name='Surat',
            defaults={
                'city_code': 'SUR',
                'phone_code': '+91-261',
                'population': 5000000,
                'avg_age': 30.5,
                'num_of_adult_males': 2500000,
                'num_of_adult_females': 2500000,
                'state': state
            }
        )
        print("Individual data insertion complete")

    def bulk_insert_data():
        # Check if the country already exists
        if not Country.objects.filter(name='India').exists():
            countries = [
                Country(
                    name='India',
                    country_code='IN',
                    curr_symbol='₹',
                    phone_code='+91',
                    my_user = user
                ),
                Country(
                    name='United States',
                    country_code='US',
                    curr_symbol='$',
                    phone_code='+1',
                    my_user = user
                ),
                Country(
                    name='United Kingdom',
                    country_code='UK',
                    curr_symbol='£',
                    phone_code='+44',
                    my_user = user
                ),
                Country(
                    name='Australia',
                    country_code='AU',
                    curr_symbol='$',
                    phone_code='+61',
                    my_user = user
                ),
                Country(
                    name='Canada',
                    country_code='CA',
                    curr_symbol='$',
                    phone_code='+1',
                    my_user = user
                ),
                Country(
                    name='Germany',
                    country_code='DE',
                    curr_symbol='€',
                    phone_code='+49',
                    my_user = user
                )
                
            ]
            Country.objects.bulk_create(countries)
            print("Bulk insert countries complete.")
        else:
            print("Country 'India' already exists, skipping bulk insert.")

        # Bulk create states
        india = Country.objects.get(name='India')
        states = [
            State(
                name='Gujarat',
                state_code='GJ',
                gst_code='24GUJGST',
                country=india
            ),
            State(
                name='Maharashtra',
                state_code='MH',
                gst_code='27MAHGST',
                country=india
            ),
            State(
                name='Tamil Nadu',
                state_code='TN',
                gst_code='33TNGST',
                country=india
            ),
            State(
                name='Telangana',
                state_code='TS',
                gst_code='36TLGST',
                country=india
            ),
            State(
                name='Karnataka',
                state_code='KA',
                gst_code='29KAGST',
                country=india
            ),
            State(
                name='Andhra Pradesh',
                state_code='AP',
                gst_code='37APGST',
                country=india
            ),
            State(
                name='Kerala',
                state_code='KL',
                gst_code='32KLGST',
                country=india
            )
        ]
        State.objects.bulk_create(states, ignore_conflicts=True)
        print("Bulk insert states complete.")

        # Bulk create cities
        gujarat = State.objects.get(name='Gujarat')
        cities = [
            City(
                name='Surat',
                city_code='SUR',
                phone_code='+91-261',
                population=10010,
                avg_age=30.5,
                num_of_adult_males=2500000,
                num_of_adult_females=2500000,
                state=gujarat
            ),
            City(
                name='Ahmedabad',
                city_code='AMD',
                phone_code='+91-079',
                population=6000000,
                avg_age=32.5,
                num_of_adult_males=3000000,
                num_of_adult_females=3000000,
                state=gujarat
            ),
            City(
                name='Hyderabad',
                city_code='HYD',
                phone_code='+91-089',
                population=6100000,
                avg_age=32.5,
                num_of_adult_males=3000000,
                num_of_adult_females=3000000,
                state=gujarat
            ),
            City(
                name='Nellore',
                city_code='NLR',
                phone_code='+91-179',
                population=9000000,
                avg_age=32.5,
                num_of_adult_males=3000000,
                num_of_adult_females=3000000,
                state=gujarat
            ),
            City(
                name='Warangal',
                city_code='WRL',
                phone_code='+91-119',
                population=90000,
                avg_age=32.5,
                num_of_adult_males=3000000,
                num_of_adult_females=3000000,
                state=gujarat
            ),
            City(
                name='Vijayawada',
                city_code='VJA',
                phone_code='+91-129',
                population=900000,
                avg_age=32.5,  
            )
        ]
        City.objects.bulk_create(cities, ignore_conflicts=True)
        print("Bulk insert cities complete.")

    # Bulk Update Data
    def bulk_update_data():
        # Update multiple countries at once
        countries = Country.objects.all()
        for country in countries:
            country.curr_symbol = country.curr_symbol.upper()
        Country.objects.bulk_update(countries, ['curr_symbol'])

        # Update multiple states
        states = State.objects.all()
        for state in states:
            state.state_code = state.state_code.lower()
        State.objects.bulk_update(states, ['state_code'])

        # Update multiple cities
        cities = City.objects.all()
        for city in cities:
            city.avg_age = round(city.avg_age + 0.5, 2)
        City.objects.bulk_update(cities, ['avg_age'])
        print("Bulk update complete")

    # Fetch all Countries, States, and Cities
    def fetch_all_data():
        countries = Country.objects.all()
        print("All Countries:")
        for country in countries:
            print(f"- {country.name}")

        states = State.objects.all()
        print("\nAll States:")
        for state in states:
            print(f"- {state.name} (Country: {state.country.name})")

        cities = City.objects.all()
        print("\nAll Cities:")
        for city in cities:
            print(f"- {city.name} (State: {city.state.name}, Country: {city.state.country.name})")

    # Fetch all cities of a State
    def fetch_state_cities():
        gujarat = State.objects.get(name='Gujarat')
        gujarat_cities = City.objects.filter(state=gujarat)
        print(f"\nCities in {gujarat.name}:")
        for city in gujarat_cities:
            print(f"- {city.name}")

    # Fetch all states of a Country
    def fetch_country_states():
        india = Country.objects.get(name='India')
        india_states = State.objects.filter(country=india)
        print(f"\nStates in {india.name}:")
        for state in india_states:
            print(f"- {state.name}")

    # Fetch all Cities of a Country name
    def fetch_country_cities():
        india_cities = City.objects.filter(state__country__name='India')
        print("\nCities in India:")
        for city in india_cities:
            print(f"- {city.name}")

    # Fetch City of a Country with Minimum and Maximum Population
    def fetch_population_extremes():
        india_population = City.objects.filter(
            state__country__name='India'
        ).aggregate(
            min_population=Min('population'),
            max_population=Max('population')
        )
        print("\nPopulation Extremes in India:")
        print(f"Minimum Population: {india_population['min_population']}")
        print(f"Maximum Population: {india_population['max_population']}")

        # Find the actual cities with min and max population
        min_pop_city = City.objects.filter(
            state__country__name='India', 
            population=india_population['min_population']
        ).first()
        max_pop_city = City.objects.filter(
            state__country__name='India', 
            population=india_population['max_population']
        ).first()

        if min_pop_city:
            print(f"Minimum Population: {min_pop_city.population}")
        else:
            print("No city found with minimum population")

        if max_pop_city:
            print(f"Maximum Population: {max_pop_city.population}")
        else:
            print("No city found with maximun population")

        if min_pop_city:
            print(f"City with Minimum Population: {min_pop_city.name}")
        else:
            print("No city found with minimum population")

        if max_pop_city:
            print(f"City with Maximum Population: {max_pop_city.name}")
        else:
            print("No city found with maximum population")

    # Execute all query methods
    insert_data()
    bulk_insert_data()
    bulk_update_data()
    fetch_all_data()
    fetch_state_cities()
    fetch_country_states()
    fetch_country_cities()
    fetch_population_extremes()

# This method will be automatically called when running the script
if __name__ == "__main__":
    run()