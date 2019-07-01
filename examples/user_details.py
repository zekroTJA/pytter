import os
import sys
from pytter import Client, Credentials


def main():
    creds = Credentials(
        consumer_key=os.environ.get('tw_consumer_key'),
        consumer_secret=os.environ.get('tw_consumer_secret'),
        access_token_key=os.environ.get('tw_access_token_key'),
        access_token_secret=os.environ.get('tw_access_token_secret'))
    
    client = Client(creds)

    user_name = sys.argv[1] if len(sys.argv) > 1 else 'zekroTJA'

    user = client.user(screen_name=user_name)

    print((
        "\nUsername:      {}\n" +
        "Display Name:  {}\n" +
        "ID:            {}\n" +
        "Created:       {}\n" +
        "Followers:     {}\n" +
        "Follows:       {}\n" +
        "Tweets:        {}\n" +
        "Favourites:    {}"
    ).format(
        user.username,
        user.name,
        user.id,
        user.created_at,
        user.stats.followers_count,
        user.stats.following_count,
        user.stats.tweet_count,
        user.stats.favourites_count
    ))


if __name__ == '__main__':
    exit(main())