Run locally

```
python ./weatherman.py
```

Install deps

```
pip install lxml requests requests_ftp -t .
```

Create zip file for deployment

```
rm ../weatherman.zip && zip -qr ../weatherman.zip . -x ".git/*"
```

Push new source code for lambda

```
aws lambda update-function-code --function-name weatherman --zip-file fileb://../weatherman.zip
```
