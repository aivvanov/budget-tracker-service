from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    email: str | None = None
    username: str
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str


mock_users = {"alexatom": {
                "email":"alex@gmail.com", 
                "username":"alexatom", 
                "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
                "full_name":"Alex Ivanov", 
                "disabled":False
                },
            "aprilluna": {
                "email":"april@gmail.com", 
                "username":"aprilluna",
                "hashed_password":"$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
                "full_name":"April Luna", 
                "disabled":True
            }
}