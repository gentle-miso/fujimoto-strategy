
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/drive'
]

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    SCOPES
)

credentials = flow.run_local_server(
    port=0,
    access_type='offline',
    prompt='consent'
)

if not credentials.refresh_token:
    raise RuntimeError("Refresh Token 발급에 실패했습니다.")

with open('token.json', 'w', encoding='utf-8') as f:
    f.write(credentials.to_json())

print("Google Drive 인증 완료")
print("token.json 파일이 생성되었습니다.")
