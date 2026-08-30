import requests

# ==========================================
# MONDAY CONFIGURATION
# ==========================================

MONDAY_API_TOKEN = "MONDAY_API_TOKEN"

DEALS_BOARD_ID = 5030964495
WORK_ORDERS_BOARD_ID = 5030964530

MONDAY_API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_TOKEN,
    "Content-Type": "application/json"
}


# ==========================================
# GET BOARD ITEMS
# ==========================================

def get_board_items(board_id):

    query = """
    query ($board_id: ID!) {
        boards(ids: [$board_id]) {
            id
            name
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

    response = requests.post(
        MONDAY_API_URL,
        json={
            "query": query,
            "variables": {
                "board_id": board_id
            }
        },
        headers=HEADERS
    )

    print("\nHTTP STATUS:", response.status_code)

    response.raise_for_status()

    result = response.json()

    # Show API errors clearly
    if "errors" in result:
        print("\n❌ MONDAY API ERROR:")
        print(result["errors"])
        return []

    if "data" not in result:
        print("\n❌ NO DATA RETURNED:")
        print(result)
        return []

    boards = result["data"].get("boards", [])

    if not boards:
        print("\n❌ BOARD NOT FOUND:", board_id)
        return []

    board = boards[0]

    print("\nBoard Name:", board["name"])
    print("Board ID:", board["id"])

    items_page = board.get("items_page")

    if not items_page:
        print("\n❌ items_page missing:")
        print(board)
        return []

    items = items_page.get("items", [])

    print("Items Retrieved:", len(items))

    return items


# ==========================================
# TEST DEALS
# ==========================================

print("=" * 60)
print("TESTING DEALS BOARD")
print("=" * 60)

deals = get_board_items(DEALS_BOARD_ID)


# ==========================================
# TEST WORK ORDERS
# ==========================================

print("\n" + "=" * 60)
print("TESTING WORK ORDERS BOARD")
print("=" * 60)

work_orders = get_board_items(WORK_ORDERS_BOARD_ID)


# ==========================================
# FINAL RESULT
# ==========================================

print("\n" + "=" * 60)
print("FINAL RESULT")
print("=" * 60)

print("Deals:", len(deals))
print("Work Orders:", len(work_orders))


# ==========================================
# SHOW FIRST DEAL
# ==========================================

if deals:

    print("\nFirst Deal:")
    print(deals[0])


# ==========================================
# SHOW FIRST WORK ORDER
# ==========================================

if work_orders:

    print("\nFirst Work Order:")
    print(work_orders[0])