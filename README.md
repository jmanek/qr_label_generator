# qr_label_generator
Generate print ready QR codes.  
Based on [this label sheet](https://www.amazon.com/1-Inch-Square-Coding-Labels-Printers/dp/B01K8O9GWU?th=1), although can work with others

## Usage
```
pip install -r requirements.txt
python index.py 0 0 https://google.com https://wikipedia.com
```
This will create two labels starting at the label in position (0, 0)
![QR label](templates/qr_label.png)