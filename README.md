A basic tool for looking up warranty information for HP computers.
Serial number and product numbers are required. This information has to be available
in hp_products.csv.
Example:
serial_number,product_number
0ABA,0CAB

This tool relies on the quirky hp warranty page. Thus is prone to all sorts of peculiar failures.
The results are saved by default to hp_warranty_info.csv and this is per bulk of computers.
Typical size of 15 computers, as this is the max possible.
