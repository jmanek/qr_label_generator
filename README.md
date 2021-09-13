# qr_label_generator
Generate print ready QR codes.  
Will work with most label templates in PDF/image form

## Usage
```
> pip install -r requirements.txt

> python .\index.py -h  
usage: index.py [-h] template start data [data ...]

Create printable QR code label

positional arguments:
  template    The template to use
  start       The square to start adding labels -- zero indexed
  data        space separated list of links to convert into QR codes


> python index.py templates/template1.pdf 0 https://google.com https://wikipedia.com
. . .
Saved to qr_label.pdf/png
```

This will create two labels starting at the label in position (0, 0)
![QR label](templates/qr_label.png)
