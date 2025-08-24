"""
Flask application.

Provides a simple api for interacting with the user's database.
This api lets the user search in the database within the range they insert.
"""

from flask import Flask

from rfserver.db.database import DetailDataBaseManager

# create a Flask app
app = Flask(__name__)


@app.route(
    "/search/<float:min_power>/<float:max_power>/<float:min_frequency>/<float:max_frequency>",
    methods=["GET"],
)
def search(
    min_power, max_power, min_frequency, max_frequency
) -> list[tuple[int, float, float, str]]:
    """Search API endpoint.

    Search the database within a specific range.
    It creates an api route that uses the search_power_frequency() method from the DetailDataBaseManager class.
    This route can then be used by the user to provide the variables and get the result.

    Args:
        min_power (float): The minimum power in the range.
        max_power (float): The maximum power in the range.
        min_frequency (float): The minimum frequency in the range.
        max_frequency (float): The maximum frequency in the range.

    Returns:
        list: A list of tuples, were each tuple contains:
            - int: Record ID.
            - float: Power value.
            - float: Frequency value.
            - str: Timestamp of the reading.

    Example:
        Request:
            GET /search/20.12/20.54/103.7/105.1

        Response:
            [
                (90, 103.7, 20.54, '06-06-2025 12:16:18'),
                (91, 104.3, 20.18, '06-06-2025 12:16:18')
            ]
    """
    result = DetailDataBaseManager.search_power_frequency(
        min_power, max_power, min_frequency, max_frequency
    )
    return result


# @app.route('/search', methods=['POST'])
# def search():
#  query = request.get_json()
#  return query
#

if __name__ == "__main__":
    app.run()
# testing :
# $ curl -X POST  http://127.0.0.1:5000/search -H 'Content-Type: application/json' -d '{"freq":"[34.55,5.55]","power":"[123.33,23.33]"}'
