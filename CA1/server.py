import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
import os

app = FastAPI()

@app.get("/oauth/redirect")
def oauth_redirect(code: str):
	print(f'Github code is: {code}')
 
	client_secret = os.getenv("SECRET")
 
	response = requests.post('https://github.com/login/oauth/access_token', 
               json={
				   'client_id': 'Ov23li6qFyS5MKRoF4x4',
				   'client_secret': client_secret,
				   'code': code,
			   }, headers={'Accept': 'application/json'})
	print(f"Response JSON:{response.json()}")
 
	acc_token = response.json()['access_token']
 
	response = requests.get('https://api.github.com/user', 
           headers={'Accept': 'application/json', 'Authorization': f'token {acc_token}'}).json()
	response_email = requests.get('https://api.github.com/user/emails', 
           headers={'Accept': 'application/json', 'Authorization': f'token {acc_token}'}).json()
	
	print(response)
	print(response_email)
 
	response['email'] = response_email
	response['Github code'] = code
	return response

@app.get("/login")
async def get_login_page():
    return FileResponse("./login.html")

if (__name__ == '__main__'):
	uvicorn.run(app, host= '0.0.0.0', port = 8589)
