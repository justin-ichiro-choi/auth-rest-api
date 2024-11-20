# Communication Contract

## TO DO
Password Reset. Library used for sending reset token has issues with formatting links. Workaround is to just have a unsecured POST endpoint with a username, and then have new hashed password updated.

## Installation

```
# Get repository
git clone https://github.com/justin-ichiro-choi/auth-rest-api.git

# Setting up local enviroment
python3 -m venv myenv
source myenv/bin/activate

# Installing dependencies
pip install -r requirements.txt

# Running api
fastapi run

```

This is intended to run on localhost for most stable connections. Note that API docs can be found at -localURL-/docs. Great for testing requests. 



## Overview of service 

### NOTE: Please update the database with a new user prior to requesting a new authentication token: 

```python
r = requests.post(website + 'users/', json={
  "username": "testuser3",
  "hashed_password": "tgt",
  "email": "testuser3@gmail.com"
})
```

### A. Please utilize the format found in test.py for intructions on REQUESTING the token. 
In this case, utilize the requests library with a json payload with password (plaintext) and username, like so. 

```python
token = requests.post("PUT API ENDPOINT HERE" + 'validate', json={
  "username": "testuser3",
  "hashed_password": "tgt",
})
```

### B. The return value of a token once the validate POST request is sent will look like the following

```json
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzIxMjQxODEsInN1YiI6InZhbGlkYXRlZDogdHJ1ZSJ9.TlYT9CLj59xgSgziGei_R9StWJi2jIPkk1jHoLNhw-E","expiration":"600"}
```
"token": String, contains a JSON token confirming that user is validated and the time of expiration

"expiration: string contains the time (in seconds) of the token being updated.

Users can decode the JWT token with the following code
```python
decoded_jwt = jwt.decode(token_data["token"], "test", algorithms="HS256" )
```

The resulting output is the token data, listed as so:
{'exp': 1732124181, 'sub': 'validated: true'}
"exp": Expiration date coded as a string using datetime library. Use the following code snippet to convert back into a Datetime object for use in client program

```python
print(datetime.fromtimestamp(decoded_jwt_time))
```

'sub' indicates the username the token is generated for and validated with the api. 

As a general overview, you can see if the token is valid for a user if: 
    - The token is valid and can be decoded with the above
    - The current time passes the time listed in the 'exp' field of the token
    - whether the 'sub' field matches the username that is matching the web resource. 

