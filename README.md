A basic tool for looking up warranty information for HP computers.
Serial numbers are required. Product numbers are optional, but recommended.
As some HP computers need this. This information has to be available
in hp_products.csv.
Example:
```
serial_number,product_number
0ABA,0CAB
```


To run the script in src\:
`python warranty.py`


This tool relies on the quirky hp warranty page. Thus is prone to all sorts of peculiar failures.
The results are saved by default to hp_warranty_info.csv and this is per bulk of computers.
Typical size of 15 computers, as this is the max possible.

One requirement for this to work is uBlock or any other addon that blocks the feedback
form that automatically pops up on the HP warranty pages. I found no good workaround
for this problem and thus rely on a addon.
This addon can be obtained from https://addons.mozilla.org/en-GB/firefox/addon/ublock-origin/
And should be saved as ublock.xpi in the src/ folder.
