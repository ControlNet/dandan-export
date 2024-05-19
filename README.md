# dandan-export

Export your dandanplay collections to json.

## Get Started

Require:
- Python

Run `pip install -r requirements.txt` to install all dependencies.

Get your token and the dandanplay api host, then put it in `.env`.

Then run the script,

```python
python main.py
```

The output will be exported at `output` folder.

## Export to Bangumi

Set the bangumi user id and token at `.env`.

After the json files are saved at `output`, then run the script,

```
python bangumi.py
```
