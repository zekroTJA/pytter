import os
import sys
import json
from pytter import Client, Credentials, User

def umap(u: User) -> dict:
    return {
        'id': u.id_str, 
        'username': u.username, 
        'name': u.name,
    }

def main():
    creds = Credentials(
        consumer_key=os.environ.get('tw_consumer_key'),
        consumer_secret=os.environ.get('tw_consumer_secret'),
        access_token_key=os.environ.get('tw_access_token_key'),
        access_token_secret=os.environ.get('tw_access_token_secret'))
    
    client = Client(creds)

    arg = sys.argv[1] if len(sys.argv) > 1 else 'zekroTJA'

    id = None
    name = None

    if arg.startswith('id:'):
        id = arg[3:]
    else:
        name = arg

    folls = client.user(screen_name=name, id=id).following()

    folls_formatted = [umap(u) for u in folls]

    with open('./following.json', 'w', encoding='utf8') as f:
        json.dump(folls_formatted, f, indent=2)

if __name__ == '__main__':
    exit(main())