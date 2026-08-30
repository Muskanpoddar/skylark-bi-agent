import requests


MONDAY_API_URL = "https://api.monday.com/v2"

DEALS_BOARD_ID = 5030964495
WORK_ORDERS_BOARD_ID = 5030964530


class MondayClient:

    def __init__(self, api_token):

        self.api_token = api_token

        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }

    def _request(self, query, variables=None):

        response = requests.post(
            MONDAY_API_URL,
            json={
                "query": query,
                "variables": variables or {}
            },
            headers=self.headers,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if result.get("errors"):
            raise Exception(
                f"Monday API error:\n{result['errors']}"
            )

        if "data" not in result:
            raise Exception(
                f"Monday returned no data:\n{result}"
            )

        return result["data"]

    def get_board_items(self, board_id):

        query = """
        query ($board_id: ID!) {

            boards(ids: [$board_id]) {

                id
                name

                columns {
                    id
                    title
                    type
                }

                items_page(limit: 500) {

                    cursor

                    items {

                        id
                        name

                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
        }
        """

        data = self._request(
            query,
            {
                "board_id": board_id
            }
        )

        boards = data.get("boards", [])

        if not boards:

            raise Exception(
                f"Board {board_id} was not found."
            )

        board = boards[0]

        # ------------------------------------------
        # Create column ID -> column title mapping
        # ------------------------------------------

        column_mapping = {}

        for column in board.get("columns", []):

            column_mapping[
                column["id"]
            ] = column["title"]

        # ------------------------------------------
        # Convert items into readable dictionaries
        # ------------------------------------------

        clean_items = []

        for item in board[
            "items_page"
        ].get("items", []):

            row = {
                "monday_item_id": item["id"],
                "Item": item["name"]
            }

            for column in item[
                "column_values"
            ]:

                column_id = column["id"]

                column_title = column_mapping.get(
                    column_id,
                    column_id
                )

                row[column_title] = column.get(
                    "text"
                )

            clean_items.append(row)

        return {
            "board_id": board["id"],
            "board_name": board["name"],
            "items": clean_items,
            "columns": column_mapping
        }

    def get_deals(self):

        return self.get_board_items(
            DEALS_BOARD_ID
        )

    def get_work_orders(self):

        return self.get_board_items(
            WORK_ORDERS_BOARD_ID
        )