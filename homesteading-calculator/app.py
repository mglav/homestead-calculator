from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Use a more explicit CORS configuration
CORS(app, resources={r"/*": {"origins": "*"}})

# Data represents national averages for the United States
ANIMAL_DATA = {
    'chicken': {
        'grazing_acres': 0.0002, 
        'feed_acres': 0.0001, 
        'feed_cost': 0.25,  # Daily feed cost per animal (national average)
        'yield': '275 eggs/year',
        'yield_numeric': 275,
        'yield_unit': 'eggs/year',
        'water_gallons': 0.05  # Daily water consumption in gallons
    },
    'duck': {
        'grazing_acres': 0.0005, 
        'feed_acres': 0.0003, 
        'feed_cost': 0.35, 
        'yield': '200 eggs/year',
        'yield_numeric': 200,
        'yield_unit': 'eggs/year',
        'water_gallons': 0.2
    },
    'goat_meat': {
        'grazing_acres': 0.5, 
        'feed_acres': 0.2, 
        'feed_cost': 3.5, 
        'yield': '60 lbs meat/year',
        'yield_numeric': 60,
        'yield_unit': 'lbs meat/year',
        'water_gallons': 3
    },
    'goat_dairy': {
        'grazing_acres': 0.4, 
        'feed_acres': 0.25, 
        'feed_cost': 4.0, 
        'yield': '0.75 gal milk/day',
        'yield_numeric': 274,  # 0.75 gal * 365 days
        'yield_unit': 'gallons milk/year',
        'water_gallons': 3
    },
    'sheep': {
        'grazing_acres': 0.2, 
        'feed_acres': 0.1, 
        'feed_cost': 3.0, 
        'yield': '6 lbs wool/year',
        'yield_numeric': 6,
        'yield_unit': 'lbs wool/year',
        'water_gallons': 2
    },
    'cow_beef': {
        'grazing_acres': 2, 
        'feed_acres': 0.8, 
        'feed_cost': 30, 
        'yield': '550 lbs meat',
        'yield_numeric': 550,
        'yield_unit': 'lbs meat',
        'water_gallons': 12
    },
    'cow_dairy': {
        'grazing_acres': 2, 
        'feed_acres': 0.9, 
        'feed_cost': 35, 
        'yield': '6 gal milk/day',
        'yield_numeric': 2190,  # 6 gal * 365 days
        'yield_unit': 'gallons milk/year',
        'water_gallons': 15
    },
    'cow_mini': {
        'grazing_acres': 0.8, 
        'feed_acres': 0.4, 
        'feed_cost': 15, 
        'yield': '2.5 gal milk/day',
        'yield_numeric': 912, # 2.5 gal * 365 days
        'yield_unit': 'gallons milk/year',
        'water_gallons': 8
    },
    'pig': {
        'grazing_acres': 0.3, 
        'feed_acres': 0.15, 
        'feed_cost': 7, 
        'yield': '200 lbs meat',
        'yield_numeric': 200,
        'yield_unit': 'lbs meat',
        'water_gallons': 5
    },
    'rabbit': {
        'grazing_acres': 0.001, 
        'feed_acres': 0.0005, 
        'feed_cost': 0.5, 
        'yield': '20 lbs meat/year',
        'yield_numeric': 20,
        'yield_unit': 'lbs meat/year',
        'water_gallons': 0.1
    },
    'alpaca': {
        'grazing_acres': 0.5, 
        'feed_acres': 0.2, 
        'feed_cost': 3.0, 
        'yield': '5 lbs fiber/year',
        'yield_numeric': 5,
        'yield_unit': 'lbs fiber/year',
        'water_gallons': 2
    }
}

# Add a root route for basic connectivity testing
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'message': 'Homesteading Calculator API is running'
    })

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Log the incoming request data for debugging
        print("Received request data:", request.get_json())
        
        data = request.get_json()
        if not data or 'animals' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing animals data in request'
            }), 400
            
        total_acres = {'min': 0, 'max': 0}
        animal_results = {}
        total_water = 0
        total_yields = {
            'eggs': 0,
            'milk': 0,
            'meat': 0,
            'wool': 0,
            'fiber': 0
        }

        for animal, count in data['animals'].items():
            if animal in ANIMAL_DATA:
                info = ANIMAL_DATA[animal]
                
                # Get land and cost values
                grazing_acres = info['grazing_acres']
                feed_acres = info['feed_acres']
                feed_cost = info['feed_cost']
                
                # Calculate daily and annual costs
                daily_cost = feed_cost * count
                annual_cost = daily_cost * 365
                
                # Calculate costs for different feeding strategies
                # For grazing, assume minimal supplemental feed (10% of full feed cost)
                grazing_daily_cost = daily_cost * 0.1  
                grazing_annual_cost = grazing_daily_cost * 365
                
                # For 50/50, use half of the full feed cost
                fifty_fifty_daily_cost = daily_cost * 0.5
                fifty_fifty_annual_cost = fifty_fifty_daily_cost * 365
                
                animal_results[animal] = {
                    'full_grazing': grazing_acres * count,
                    'fifty_fifty': (grazing_acres + feed_acres) / 2 * count,
                    'full_feeding': feed_acres * count,
                    'cost_grazing': grazing_daily_cost,
                    'cost_fifty_fifty': fifty_fifty_daily_cost,
                    'cost_feeding': daily_cost,
                    'annual_cost_grazing': grazing_annual_cost,
                    'annual_cost_fifty_fifty': fifty_fifty_annual_cost,
                    'annual_cost_feeding': annual_cost,
                    'yield': info['yield'],
                    'yield_numeric': info['yield_numeric'] * count,
                    'yield_unit': info['yield_unit'],
                    'water_gallons': info['water_gallons'] * count
                }
                
                # Add to totals
                total_acres['min'] += feed_acres * count
                total_acres['max'] += grazing_acres * count
                total_water += info['water_gallons'] * count
                
                # Track total yields
                if 'eggs' in info['yield_unit']:
                    total_yields['eggs'] += info['yield_numeric'] * count
                elif 'milk' in info['yield_unit']:
                    total_yields['milk'] += info['yield_numeric'] * count
                elif 'meat' in info['yield_unit']:
                    total_yields['meat'] += info['yield_numeric'] * count
                elif 'wool' in info['yield_unit']:
                    total_yields['wool'] += info['yield_numeric'] * count
                elif 'fiber' in info['yield_unit']:
                    total_yields['fiber'] += info['yield_numeric'] * count

        # Log the response data for debugging
        response_data = {
            'animal_data': animal_results, 
            'min_acreage': total_acres['min'], 
            'max_acreage': total_acres['max'],
            'total_water_daily': total_water,
            'total_water_annual': total_water * 365,
            'is_national_average': True,
            'total_yields': total_yields
        }
        print("Sending response data:", response_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        print("Error in calculate endpoint:", str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Homesteading Calculator API...")
    print("Server will be available at http://127.0.0.1:5000")
    print("Press Ctrl+C to quit")
    app.run(debug=True)