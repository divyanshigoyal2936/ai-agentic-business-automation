from tools.customer_tools import find_customer_by_email
from tools.customer_tools import get_all_customers
from tools.customer_tools import find_customer_by_id

result = find_customer_by_email("suzy.doe@example.com")
# print(result)

all_customers = get_all_customers()
# print(all_customers)    

customer_by_id = find_customer_by_id(18734)
print(customer_by_id)