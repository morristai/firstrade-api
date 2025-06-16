import json
from typing import List, Union
from firstrade.positions import Stock, Option


def parse_positions(data_input: Union[str, dict]) -> List[Union[Stock, Option]]:
    """
    Parse a JSON string or dictionary of positions into a list of Stock or Option objects.

    Args:
        data_input (Union[str, dict]): Raw JSON string or parsed dictionary containing positions data.

    Returns:
        List[Union[Stock, Option]]: List of instantiated Stock or Option objects.

    Raises:
        json.JSONDecodeError: If the JSON string is invalid (when input is a string).
        KeyError: If required fields are missing in the data.
        TypeError: If the input is neither a string nor a dictionary.
    """
    try:
        # Handle input type
        if isinstance(data_input, str):
            # Parse JSON string into a Python dictionary
            data = json.loads(data_input)
        elif isinstance(data_input, dict):
            # Input is already a dictionary
            data = data_input
        else:
            raise TypeError(f"Input must be str or dict, not {type(data_input).__name__}")

        # Ensure the 'items' key exists
        if 'items' not in data:
            raise KeyError("Data must contain an 'items' key")

        positions = []

        # Common fields for both Stock and Option
        common_fields = [
            'quantity', 'symbol', 'sec_type', 'market_value', 'cost', 'unit_cost',
            'adj_cost', 'adj_unit_cost', 'adj_gainloss', 'adj_gainloss_percent',
            'company_name', 'last', 'bid', 'ask', 'vol', 'close', 'change',
            'change_percent', 'time', 'purchase_date', 'day_held'
        ]

        # Stock-specific fields
        stock_fields = [
            'eps', 'pe', 'div_share', 'yield', 'ex_div_date', 'div_date',
            'market_cap', 'beta', 'annual_div_rate', 'avg_vol', '52w_high',
            '52w_low', 'has_lots', 'open_px', 'day_high', 'day_low'
        ]

        # Option-specific fields
        option_fields = [
            'asksize', 'bidsize', 'today_share', 'today_exe_price', 'drip', 'loan'
        ]

        for item in data['items']:
            # Extract common fields, providing defaults for missing ones
            common_kwargs = {field: item.get(field,
                                             0 if field in ['quantity', 'market_value', 'cost', 'unit_cost', 'adj_cost',
                                                            'adj_unit_cost', 'adj_gainloss', 'adj_gainloss_percent',
                                                            'last', 'bid', 'ask', 'vol', 'close', 'change',
                                                            'change_percent', 'day_held'] else '' if field in ['symbol',
                                                                                                               'company_name',
                                                                                                               'time',
                                                                                                               'purchase_date'] else 1 if field == 'sec_type' else None)
                             for field in common_fields}

            if item.get('sec_type') == 1:  # Stock
                # Extract stock-specific fields
                stock_kwargs = {field: item.get(field,
                                                0 if field in ['eps', 'pe', 'div_share', 'yield', 'market_cap', 'beta',
                                                               'annual_div_rate', 'avg_vol', '52w_high', '52w_low',
                                                               'open_px', 'day_high', 'day_low'] else '' if field in [
                                                    'ex_div_date',
                                                    'div_date'] else False if field == 'has_lots' else None) for field
                                in stock_fields}

                # Combine common and stock-specific kwargs
                kwargs = {**common_kwargs, **stock_kwargs}

                # Rename fields to match Stock class parameter names
                kwargs['yield_'] = kwargs.pop('yield')
                kwargs['_52w_high'] = kwargs.pop('52w_high')
                kwargs['_52w_low'] = kwargs.pop('52w_low')

                # Instantiate Stock
                position = Stock(**kwargs)

            else:  # Option (sec_type == 2)
                # Extract option-specific fields
                option_kwargs = {field: item.get(field, 0 if field in ['asksize', 'bidsize', 'today_share',
                                                                       'today_exe_price'] else False if field in [
                    'drip', 'loan'] else None) for field in option_fields}

                # Combine common and option-specific kwargs
                kwargs = {**common_kwargs, **option_kwargs}

                # Instantiate Option
                position = Option(**kwargs)

            positions.append(position)

        return positions

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON string: {str(e)}", e.doc, e.pos)
    except Exception as e:
        raise Exception(f"Error parsing positions: {str(e)}")
