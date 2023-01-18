

## Setup 

#### Install requirements with 

```
python -m pip install -r requirements.txt
```


Get mongodb up 
```
docker-compose up 
```


Then start the FastAPI app with 
```
uvicorn logging_api:app --reload --host 0.0.0.0
```